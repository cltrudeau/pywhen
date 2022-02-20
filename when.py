__version__ = '0.11.1'

import sys
from datetime import datetime, time
import time as time_mod

# =============================================================================

# compensate for long disappearing in py3
if sys.version_info > (3,):
    long = int

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
