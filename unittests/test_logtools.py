import os, sys, copy
import logging.config
from six import StringIO
from unittest import TestCase

from wrench.utils import temp_directory
from wrench.logtools.utils import (configure_file_logger, 
    configure_stdout_logger, default_logging_dict, silence_logging)

# =============================================================================

class GotHere(Exception):
    pass


@silence_logging
class ShouldBeQuiet(object):
    def logthing(self):
        logger = logging.getLogger(__name__)
        logger.debug('this is a message')
        raise GotHere()


@silence_logging
def should_be_quiet():
    logger = logging.getLogger(__name__)
    logger.debug('this is a message')
    raise GotHere()

# =============================================================================

class TestLogging(TestCase):
    def _reset_logging(self):
        # put the logging into a known state
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                handler.close()
                root.removeHandler(handler)

        logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    def setUp(self):
        self._reset_logging()

    def tearDown(self):
        self._reset_logging()

    def test_config_file_logger(self):
        with temp_directory() as td:
            configure_file_logger('debug', td)
            logger = logging.getLogger(__name__)
            logger.debug('this is a message')

            logfile = os.path.abspath(os.path.join(td, 'debug.log'))
            self.assertTrue(os.path.exists(logfile))

    def test_config_stdout_logger(self):
        saved_stderr = sys.stderr
        try:
            out = StringIO()
            sys.stderr = out
            configure_stdout_logger()
            logger = logging.getLogger(__name__)
            logger.debug('this is a message')

            output = out.getvalue().strip()
            self.assertIn('this is a message', output)

        finally:
            sys.stderr = saved_stderr

    def test_default_logging_dict(self):
        with temp_directory() as td:
            d = default_logging_dict(td)
            logging.config.dictConfig(d)

            logger = logging.getLogger(__name__)
            logger.debug('this is a message')

            logfile = os.path.abspath(os.path.join(td, 'debug.log'))
            self.assertTrue(os.path.exists(logfile))

    def test_silence_decorator(self):
        saved_stderr = sys.stderr
        try:
            out = StringIO()
            sys.stderr = out

            with self.assertRaises(GotHere):
                should_be_quiet()

            s = ShouldBeQuiet()
            with self.assertRaises(GotHere):
                s.logthing()

            output = out.getvalue().strip()
            self.assertEqual(0, len(output))

        finally:
            sys.stderr = saved_stderr