import os, logging
from functools import wraps

# =============================================================================
# Constants
# =============================================================================

#: Log formatting for vt100 with function name highlighted and message
LOG_FORMAT_ESCAPED = '\033[1m%(funcName)s\033[0m: %(message)s'

#: Log format for files with date/time, function info, pid/tid and message
LOG_FORMAT_STANDARD = ('%(asctime)s %(name)s.%(funcName)s: '
    'pid:tid=%(process)d:%(thread)d %(message)s')

# =============================================================================
# Logging Configuration
# =============================================================================

def configure_file_logger(name, log_dir, log_level=logging.DEBUG):
    """Configures logging to use the :class:`SizeRotatingFileHandler`"""
    from .srothandler import SizeRotatingFileHandler

    root = logging.getLogger()
    root.setLevel(log_level)
    handler = SizeRotatingFileHandler(os.path.join(log_dir, '%s.log' % name))
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT_STANDARD))

    root.addHandler(handler)


def configure_stdout_logger(log_level=logging.DEBUG):
    """Configures logging to use STDOUT"""
    root = logging.getLogger()
    root.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT_ESCAPED))

    root.addHandler(handler)


def default_logging_dict(log_dir, handlers=['file'], filename='debug.log'):
    """Returns a logging configuration dictionary with reasonable defaults.
    Defines two handlers: "default" and "file", that go to STDOUT and a
    :class:`SizeRotatingFileHandler`.

    :param log_dir:
        Directory for logs to go into.
    :param handlers:
        Which logging handlers to use.  Defaults to only 'file'
    :param filename:
        Base name of the file to log to.  Defaults to "debug.log".
    """
    d = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'escaped': {
                'format':LOG_FORMAT_ESCAPED,
            },
            'standard': {
                'format':LOG_FORMAT_STANDARD,
            },
        },
        'handlers': {
            'default': {
                'level':'DEBUG',
                'class':'logging.StreamHandler',
                'formatter':'escaped',
            },
            'file': {
                'level':'DEBUG',
                'class':'wrench.logtools.srothandler.SizeRotatingFileHandler',
                'filename': os.path.abspath(os.path.join(log_dir, filename)),
                'formatter':'standard',
                'maxBytes':300000,
            },
        },
        'loggers': {
            '': {
                'handlers':handlers,
                'propagate': False,
                'level':'DEBUG',
            },
        },
    }

    return d

# ============================================================================
# Decorators
# ============================================================================

def silence_logging(method):
    """Disables logging for the duration of what is being wrapped.  This is
    particularly useful when testing if a test method is supposed to issue an
    error message which is confusing that the error shows for a successful
    test.

    .. warning::

        Normally you can use function decorators to wrap a class, but if you
        wrap a :class:`TestCase` class what is returned is a function which
        means it won't be found by the test discovery process.  Wrap the
        individual test case methods, or alter logging in the
        :class:`TestCase.setUp` and :class`TestCase.tearDown` methods.
    """
    @wraps(method)
    def wrapper(*args, **kwargs):
        logging.disable(logging.ERROR)
        result = method(*args, **kwargs)
        logging.disable(logging.NOTSET)
        return result
    return wrapper
