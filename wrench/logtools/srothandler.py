# SizeRotatingFileHandler
#
# Based on:
#
# https://pypi.python.org/pypi/ConcurrentLogHandler
# version = 0.9.1
#
# Original work:
#
#     Copyright 2013 Lowell Alleman
#
#      Licensed under the Apache License, Version 2.0 (the "License"); you may
#      not use this file except in compliance with the License. You may obtain
#      a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#      Unless required by applicable law or agreed to in writing, software
#      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#      License for the specific language governing permissions and limitations
#      under the License.

import os, sys, time
from random import randint
from logging import Handler, LogRecord
from logging.handlers import BaseRotatingHandler

try:
    import codecs
except ImportError:
    codecs = None

from portalocker import lock, unlock, LOCK_EX


# Workaround for handleError() in Python 2.7+ where record is written to stderr
class NullLogRecord(LogRecord):
    def __init__(self):
        pass
    def __getattr__(self, attr):
        return None

class SizeRotatingFileHandler(BaseRotatingHandler):
    """Rotating file handler that handles concurrent access without losing
    logs.  When a size limit is hit the log is rotated, with the old log
    renamed based on timestamp.

    Depending on the platform, the size limit may not be completely respected
    if several processes have it open simultaneously as it may need to wait
    for a process to let go.

    This handler is based on the version 0.9.1 of the 
    `ConcurrentLogHandler <https://pypi.python.org/pypi/ConcurrentLogHandler>`_
    by Lowell Alleman and with the exception of the removal of the "backup
    count" feature and how the files are renamed is a direct copy, the same
    caveats apply.
    """

    def __init__(self, filename, mode='a', maxBytes=0, encoding=None, 
            debug=True, delay=0):
        """
        Open the specified file and use it as the stream for logging.

        By default, the file grows indefinitely. You can specify particular
        values of maxBytes to allow the file to rollover at a predetermined
        size.

        Rollover occurs whenever the current log file is nearly maxBytes in
        length.  Old files are renamed based on timestamps.

        If maxBytes is zero, rollover never occurs.
        """
        # Absolute file name handling done by FileHandler since Python 2.5  
        BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
        self.delay = delay
        self._rotateFailed = False
        self.maxBytes = maxBytes
        self._open_lockfile()
        # For debug mode, swap out the "_degrade()" method with a more a verbose one.
        if debug:
            self._degrade = self._degrade_debug
    
    def _open_lockfile(self):
        # Use 'file.lock' and not 'file.log.lock' (Only handles the normal "*.log" case.)
        if self.baseFilename.endswith(".log"):
            lock_file = self.baseFilename[:-4]
        else:
            lock_file = self.baseFilename
        lock_file += ".lock"
        self.stream_lock = open(lock_file,"w")
    
    def _open(self, mode=None):
        """
        Open the current base file with the (original) mode and encoding.
        Return the resulting stream.
        
        Note:  Copied from stdlib.  Added option to override 'mode'
        """
        if mode is None:
            mode = self.mode
        if self.encoding is None:
            stream = open(self.baseFilename, mode)
        else:
            stream = codecs.open(self.baseFilename, mode, self.encoding)
        return stream
    
    def _close(self):
        """ Close file stream.  Unlike close(), we don't tear anything down, we
        expect the log to be re-opened after rotation."""
        if self.stream:
            try:
                if not self.stream.closed:
                    # Flushing probably isn't technically necessary, but it feels right
                    self.stream.flush()
                    self.stream.close()
            finally:
                self.stream = None
    
    def acquire(self):
        """ Acquire thread and file locks.  Re-opening log for 'degraded' mode.
        """
        # handle thread lock
        Handler.acquire(self)
        # Issue a file lock.  (This is inefficient for multiple active threads
        # within a single process. But if you're worried about high-performance,
        # you probably aren't using this log handler.)
        if self.stream_lock:
            # If stream_lock=None, then assume close() was called or something
            # else weird and ignore all file-level locks.
            if self.stream_lock.closed:
                # Daemonization can close all open file descriptors, see
                # https://bugzilla.redhat.com/show_bug.cgi?id=952929
                # Try opening the lock file again.  Should we warn() here?!?
                try:
                    self._open_lockfile()
                except Exception:
                    self.handleError(NullLogRecord())
                    # Don't try to open the stream lock again
                    self.stream_lock = None
                    return
            lock(self.stream_lock, LOCK_EX)
        # Stream will be opened as part by FileHandler.emit()

    def release(self):
        """ Release file and thread locks. If in 'degraded' mode, close the
        stream to reduce contention until the log files can be rotated. """
        try:
            if self._rotateFailed:
                self._close()
        except Exception:
            self.handleError(NullLogRecord())
        finally:
            try:
                if self.stream_lock and not self.stream_lock.closed:
                    unlock(self.stream_lock)
            except Exception:
                self.handleError(NullLogRecord())
            finally:
                # release thread lock
                Handler.release(self)
    
    def close(self):
        """
        Close log stream and stream_lock. """
        try:
            self._close()
            if hasattr(self.stream_lock, 'closed') and \
                    not self.stream_lock.closed:
                self.stream_lock.close()
        finally:
            self.stream_lock = None
            Handler.close(self)
    
    def _degrade(self, degrade, msg, *args):
        """ Set degrade mode or not.  Ignore msg. """
        self._rotateFailed = degrade
        del msg, args   # avoid pychecker warnings
    
    def _degrade_debug(self, degrade, msg, *args):
        """ A more colorful version of _degade(). (This is enabled by passing
        "debug=True" at initialization).
        """
        if degrade:
            if not self._rotateFailed:
                sys.stderr.write("Degrade mode - ENTERING - (pid=%d)  %s\n" %
                                 (os.getpid(), msg % args))
                self._rotateFailed = True
        else:
            if self._rotateFailed:
                sys.stderr.write("Degrade mode - EXITING  - (pid=%d)   %s\n" %
                                 (os.getpid(), msg % args))
                self._rotateFailed = False
    
    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        self._close()

        try:
            dfn = self.baseFilename + "." + time.strftime(self.SUFFIX, 
                time.gmtime(int(time.time())))

            # Determine if we can rename the log file or not. Windows refuses
            # to rename an open file, Unix is inode base so it doesn't care.
            
            # Attempt to rename logfile to tempname:  There is a slight
            # race-condition here, but it seems unavoidable
            tmpname = None
            while not tmpname or os.path.exists(tmpname):
                tmpname = "%s.rotate.%08d" % (self.baseFilename, randint(0,99999999))
            try:
                # Do a rename test to determine if we can successfully rename
                # the log file
                os.rename(self.baseFilename, tmpname)
            except (IOError, OSError):
                exc_value = sys.exc_info()[1]
                self._degrade(True, "rename failed.  File in use?  "
                              "exception=%s", exc_value)
                return

            os.rename(tmpname, dfn)
            #print "%s -> %s" % (self.baseFilename, dfn)
            self._degrade(False, "Rotation completed")
        finally:
            # Re-open the output stream, but if "delay" is enabled then wait
            # until the next emit() call. This could reduce rename contention in
            # some usage patterns.
            if not self.delay:
                self.stream = self._open()
    
    def shouldRollover(self, record):
        """
        Determine if rollover should occur.

        For those that are keeping track. This differs from the standard
        library's RotatingLogHandler class. Because there is no promise to keep
        the file size under maxBytes we ignore the length of the current record.
        """
        del record  # avoid pychecker warnings
        # Is stream is not yet open, skip rollover check. (Check will occur on
        # next message, after emit() calls _open())
        if self.stream is None:
            return False
        if self._shouldRollover():
            # If some other process already did the rollover (which is possible
            # on Unix) the file our stream may now be named "log.1", thus
            # triggering another rollover. Avoid this by closing and opening
            # "log" again.
            self._close()
            self.stream = self._open()
            return self._shouldRollover()
        return False
    
    def _shouldRollover(self):
        if self.maxBytes > 0:                   # are we rolling over?
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            if self.stream.tell() >= self.maxBytes:
                return True
            else:
                self._degrade(False, "Rotation done or not needed at this time")
        return False


# Publish this class to the "logging.handlers" module so that it can be use 
# from a logging config file via logging.config.fileConfig().
import logging.handlers
logging.handlers.SizeRotatingFileHandler = SizeRotatingFileHandler
