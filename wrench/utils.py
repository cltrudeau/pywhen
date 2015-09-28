import contextlib, os, shutil, sys, tempfile
from datetime import datetime, time
import time as time_mod

from enum import Enum

# =============================================================================

# compensate for long disappearing in py3
if sys.version_info > (3,):
    long = int

# =============================================================================
# Extended Enum 
# =============================================================================

class ExtendedEnum(Enum):
    """Extends ``Enum`` (either native or enum34.enum depending on python
    version) and adds some features.
    """

    @classmethod
    def choices(cls):
        """Returns a "choices" list of tuples.  Each member of the list is one
        of the possible items in the ``Enum``, with the first item in the pair
        being the value and the second the name.  This is compatible with
        django's choices attribute in fields.

        :returns:
            List of tuples
        """
        result = []
        for name, member in cls.__members__.items():
            result.append((member.value, name))

        return result

    @classmethod
    def items(cls):
        """Returns a iterable of name/value pairs for the items in the
        ``Enum``.

        :returns:
            Iterable of name/value tuples
        """
        for item in cls:
            yield (item.name, item.value)

    @classmethod
    def count(cls):
        """Returns the number of items in the enumeration."""
        return len(cls.__members__)

    @classmethod
    def values(cls):
        """Returns a list of the values of the items in the enumeration."""
        return [e.value for e in list(cls)]

    @classmethod
    def names(cls):
        """Returns a list of the names of the items in the enumeration."""
        return [e.name for e in list(cls)]

# =============================================================================
# Date Conversion
# =============================================================================

class TimeOnlyError(Exception):
    """Exception indicating that a date operation was attempted on a
    :class:`When` object that only wraps a python ``time`` instance."""
    pass


class When(object):
    # https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    """Date/time conversion utility.  A When object wraps either a python
    ``datetime`` or ``time`` instance, providing a common mechanism for
    building and converting them into different formats.

    If When is wrapping a ``time`` object then some methods will raise a
    :class:`TimeOnlyError`.

    .. _when-formats:

    Supported formats for parsing and display::

        'date': '%Y-%m-%d'
        'time': '%H:%M'
        'time_sec': '%H:%M:%S'
        'datetime': '%Y-%m-%d %H:%M'
        'datetime_sec': '%Y-%m-%d %H:%M:%S'
        'datetime_utc': '%Y-%m-%dT%H:%MZ'
        'datetime_sec_utc': '%Y-%m-%dT%H:%M:%SZ'
        'iso_micro': '%Y-%m-%dT%H:%M:%S.%fZ'

    .. warning::

        All python ``datetime`` objects in this class are naive and have no
        timezone information associated with them, this includes various
        formats labelled "utc".
    """
    parse_formats = {
        'date': '%Y-%m-%d',
        'time': '%H:%M',
        'time_sec': '%H:%M:%S',
        'datetime': '%Y-%m-%d %H:%M',
        'datetime_sec': '%Y-%m-%d %H:%M:%S',
        'datetime_utc': '%Y-%m-%dT%H:%MZ',
        'datetime_sec_utc': '%Y-%m-%dT%H:%M:%SZ',
        'iso_micro': '%Y-%m-%dT%H:%M:%S.%fZ',
    }

    class WhenStrformat(object):
        def __init__(self, when):
            self.when = when

        def __getattribute__(self, name):
            if name == 'when':
                return object.__getattribute__(self, name)

            formatter = self.when.parse_formats[name]
            if name == 'iso_micro':
                # iso_micro needs special handling as python's %f returns a
                # zero padded number but the standard doesn't pad the value
                formatter = self.when.parse_formats['datetime_sec_utc']

            result = self.when.datetime.strftime(formatter)

            if name == 'iso_micro':
                result = result[:-1] + '.%dZ' % int(
                    self.when.datetime.strftime('%f'))

            return result


    def __init__(self, **kwargs):
        """Create a When object.  The constructor accepts a variety of
        keywords depending on what type of date or time information you wish
        to convert.  Most keywords result in a python ``datetime`` object
        being wrapped, but certain cases use a ``time`` object.  If the When
        is only a ``time`` wrapper then some of the methods will not be
        available.

        :param datetime:
            Create ``When`` using a python ``datetime`` object
        :param date:
            Create ``When`` using a python ``date`` object, can be used in
            conjunction with the ``time`` keyword.  If used without the
            ``time`` keyword the time portion will be set to midnight.
        :param time:
            Create ``When`` using a python ``time`` object.  If used on its
            own the date based methods of ``When`` will not be allowed.  This
            keyword can be used in conjunction with the ``date`` keyword to
            create a fully qualified ``When``.
        :param time_string:
            Create ``When`` using a string containing time information.
            Handles either 'hour:minute' or 'hour:minute:second'.  Like the
            ``time`` keyword, can be used in conjunction with ``date``.
        :param epoch:
            Create ``When`` using an integer epoch value
        :param milli_epoch:
            Create ``When`` using an integer that is 1000 * an epoch value with
            the last thousands being milli-epoch.
        :param detect:
            Create ``When`` by parsing a string which is compared against the
            list of available string parsers.
        :param parse_*: 
            Create ``When`` by parsing a string using the specific 
            :ref:`Supported formats <when-formats>` given.
            For example, ``parse_iso_micro`` expects the ISO 8601 format.

        :raises ValueError:
            If a bad string is passed to ``detect`` or ``parse_*`` keywords
        :raises AttributeError:
            If the constructor was called without sufficient arguments to
            result in a date or time being wrapped.
        """
        self._datetime = None
        self._time = None

        if 'datetime' in kwargs:
            self._datetime = kwargs['datetime']
        elif 'date' in kwargs:
            d = kwargs['date']
            if 'time' in kwargs:
                t = kwargs['time']
            elif 'time_string' in kwargs:
                t = self._parse_time_string(kwargs['time_string'])
            else:
                t = time()

            self._datetime = datetime(d.year, d.month, d.day, t.hour, t.minute,
                t.second)
        elif 'time' in kwargs:
            self._time = kwargs['time']
        elif 'time_string' in kwargs:
            self._time = self._parse_time_string(kwargs['time_string'])
        elif 'epoch' in kwargs:
            self._datetime = datetime.fromtimestamp(kwargs['epoch'])
        elif 'milli_epoch' in kwargs:
            mepoch = kwargs['milli_epoch']
            epoch = float(mepoch) / 1000.0
            milli = float(mepoch) - (epoch * 1000.0)
            self._datetime = datetime.fromtimestamp(long(epoch))
            self._datetime.replace(microsecond = int(milli / 10.0))
        elif 'detect' in kwargs:
            for f in self.parse_formats.values():
                try:
                    self._datetime = datetime.strptime(kwargs['detect'], f)
                    break
                except ValueError:
                    # couldn't parse using this format, ignore and try again
                    pass

            if not self._datetime:
                # nothing parsed
                raise ValueError(('could not parse the date/time passed to '
                    'detect'))
        else:
            # loop through all the possible kwargs looking for parse_* keys,
            # if found parse based on that and stop
            for key, value in kwargs.items():
                if key.startswith('parse_'):
                    f = self.parse_formats[key[6:]]
                    if key.startswith('parse_time'):
                        self._time = self._parse_time_string(value)
                    else:
                        self._datetime = datetime.strptime(value, f)

                    break

        if not self._datetime and not self._time:
            raise AttributeError('invalid keyword arguments')

    def _parse_time_string(self, value):
        parts = value.split(':')
        parts = [int(p) for p in parts]
        return time(*parts)

    @property
    def string(self):
        """Returns a placeholder object that has an attribute for each one of
        the :ref:`Supported formats <when-formats>`.  

        Example::

            >>> When(datetime=d).string.iso_micro
            1972-01-31T13:45:00.2

        """
        return When.WhenStrformat(self)

    @property
    def date(self):
        """Returns a python ``date`` object."""
        return self._datetime.date()

    @property
    def datetime(self):
        """Returns a python ``datetime`` object."""
        return self._datetime

    @property
    def time(self):
        """Returns a python ``time`` object."""
        if self._datetime:
            return self._datetime.time()

        return self._time

    @property
    def epoch(self):
        """Returns an integer version of epoch, i.e. the number of seconds
        since Jan 1, 1970."""
        return long(time_mod.mktime(self._datetime.timetuple()))

    @property
    def milli_epoch(self):
        """Returns an int of the epoch * 1000 + milliseconds."""
        return self.epoch * 1000 + self._datetime.microsecond * 10

# =============================================================================
# Utility Methods
# =============================================================================

def dynamic_load(name):
    """Equivalent of "from X import Y" statement using dot notation to specify
    what to import and return.  For example, foo.bar.thing returns the item
    "thing" in the module "foo.bar" """
    pieces = name.split('.')
    item = pieces[-1]
    mod_name = '.'.join(pieces[:-1])

    mod = __import__(mod_name, globals(), locals(), [item])
    return getattr(mod, item)


def camelcase_to_underscore(text):
    prev_cap = text[0].isupper()
    result = [text[0].lower(), ]
    for letter in text[1:]:
        if letter.isupper():
            if not prev_cap:
                result.append('_')

            result.append(letter.lower())
            prev_cap = True
        else:
            result.append(letter)
            prev_cap = False

    return ''.join(result)


def rows_to_columns(matrix):
    """Takes a two dimensional array and returns an new one where rows in the
    first become columns in the second."""
    num_rows = len(matrix)
    num_cols = len(matrix[0])

    data = []
    for i in range(0, num_cols):
        data.append([matrix[j][i] for j in range(0, num_rows)])

    return data

# =============================================================================
# Contexts
# =============================================================================

@contextlib.contextmanager
def replaced_directory(dirname):
    """This ``Context`` is used to move the contents of a directory elsewhere
    temporarily and put them back upon exit.  This allows testing code to use
    the same file directories as normal code without fear of damage.

    The name of the temporary directory which contains your files is yielded.

    :param dirname:
        Path name of the directory to be replaced.
    """
    if dirname[-1] == '/':
        dirname = dirname[:-1]

    full_path = os.path.abspath(dirname)
    if not os.path.isdir(full_path):
        raise AttributeError('dir_name must be a directory')

    base, name = os.path.split(full_path)

    # create a temporary directory, move provided dir into it and recreate the
    # directory for the user
    tempdir = tempfile.mkdtemp()
    shutil.move(full_path, tempdir)
    os.mkdir(full_path)
    try:
        yield tempdir

    finally:
        # done context, undo everything
        shutil.rmtree(full_path)
        moved = os.path.join(tempdir, name)
        shutil.move(moved, base)
        shutil.rmtree(tempdir)


@contextlib.contextmanager
def temp_directory():
    """This ``Context`` creates a temporary directory and yields its path.
    Upon exit the directory is removed.
    """
    tempdir = tempfile.mkdtemp()
    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir)
