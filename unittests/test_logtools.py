import os, sys, copy
import logging.config
from six import StringIO
from unittest import TestCase

from wrench.contexts import temp_directory, capture_stderr
from wrench.logtools.utils import (configure_file_logger, 
    configure_stdout_logger, default_logging_dict, silence_logging)

# =============================================================================

@silence_logging
def should_be_quiet():
    logger = logging.getLogger(__name__)
    logger.debug('log message for should_be_quiet()')
    return 42

# =============================================================================

class TestLogging(TestCase):
    def _reset_logging(self):
        # put the logging into a known state
        root = logging.getLogger()
        root.manager.loggerDict = {}
        if root.handlers:
            for handler in root.handlers:
                handler.close()
                root.removeHandler(handler)

    def _flush_logging(self):
        # we're checking for content we've logged which can cause race
        # conditions in some cases, this is a bit dependent on internals of
        # logging but will flush things out
        root = logging.getLogger()
        for handler in root.handlers:
            handler.flush()

    def assert_in_file(self, text, filename):
        with open(filename) as f:
            content = f.read()
            self.assertIn(text, content)

    def setUp(self):
        self._reset_logging()

    def tearDown(self):
        self._reset_logging()

    def test_config_file_logger(self):
        msg = 'log message test_config_file_logger'
        with temp_directory() as td:
            configure_file_logger('debug', td)
            logger = logging.getLogger(__name__)
            logger.debug(msg)
            self._flush_logging()

            logfile = os.path.abspath(os.path.join(td, 'debug.log'))
            self.assert_in_file(msg, logfile)

    def test_config_stdout_logger(self):
        saved_stderr = sys.stderr
        msg = 'log message test_config_stdout_logger'
        try:
            out = StringIO()
            sys.stderr = out
            configure_stdout_logger()
            logger = logging.getLogger(__name__)
            logger.debug(msg)
            self._flush_logging()

            output = out.getvalue().strip()
            self.assertIn(msg, output)

        finally:
            sys.stderr = saved_stderr

    def test_default_logging_dict(self):
        msg = 'log message test_default_logging_dict'

        with capture_stderr() as output:
            with temp_directory() as td:
                d = default_logging_dict(td, handlers=['default', 'file'])
                logging.config.dictConfig(d)

                logger = logging.getLogger(__name__)
                logger.debug(msg)
                self._flush_logging()

                logfile = os.path.abspath(os.path.join(td, 'debug.log'))

                self.assert_in_file(msg, logfile)

                self.assertIn(msg, output.getvalue())

    def test_silence_decorator(self):
        saved_stderr = sys.stderr
        try:
            out = StringIO()
            sys.stderr = out

            # put something in the log to make sure that it isn't that logging
            # isn't working before we silence things
            root = logging.getLogger()
            root.setLevel(logging.DEBUG)

            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(logging.Formatter('%(message)s'))
            root.addHandler(handler)

            root.debug('should be there')

            # --- test func decoration
            result = should_be_quiet()
            self.assertEqual(42, result)

            output = out.getvalue().strip()
            self.assertEqual('should be there', output)
        finally:
            sys.stderr = saved_stderr
