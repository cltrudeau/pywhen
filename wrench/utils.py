import six

# =============================================================================
# Extended Enum 
# =============================================================================

from enum import Enum

class ExtendedEnum(Enum):
    """Extends Enum (either native or flufl.enum depending on python version)
    and adds some features.
    """

    @classmethod
    def choices(cls):
        """Returns a "choices" list of tuples.  Each member of the list is one
        of the possible items in the `Enum`, with the first item in the pair
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
    pass


class When(object):
    """Date/time conversion utility.  A When object wraps either a python
    `datetime` or `time` instance, providing a common mechanism for building
    and converting them into different formats.

    If When is wrapping a `time` object then some methods will raise a
    ``class:TimeOnlyError``.

    .. _when-formats:

    Supported formats for parsing and display::

        'date': '%Y-%m-%d'
        'time': '%H:%M'
        'time_sec': '%H:%M:%S'
        'datetime': '%Y-%m-%d %H:%M'
        'datetime_sec': '%Y-%m-%d %H:%M:%S'
        'datetime_utc': '%Y-%m-%dT%H:%MZ'
        'datetime_sec_utc': '%Y-%m-%dT%H:%M:%SZ'
        'isoformat': '%Y-%m-%dT%H:%M:%S.%fZ'

    """
    parse_formats = {
        'date': '%Y-%m-%d',
        'time': '%H:%M',
        'time_sec': '%H:%M:%S',
        'datetime': '%Y-%m-%d %H:%M',
        'datetime_sec': '%Y-%m-%d %H:%M:%S',
        'datetime_utc': '%Y-%m-%dT%H:%MZ',
        'datetime_sec_utc': '%Y-%m-%dT%H:%M:%SZ',
        'isoformat': '%Y-%m-%dT%H:%M:%S.%fZ',
    }

    class WhenStrformat(object):
        def __init__(self, when):
            self.when = when

        def __getattribute__(self, name):
            try:
                formatter = When.parse_formats[name]
                return self.when.datetime.strftime(formatter)

            except KeyError:
                object.__getattribute(self, name)


    def __init__(self, **kwargs):
        """Create a When object.  The constructor accepts a variety of
        keywords depending on what type of date or time information you wish
        to convert.  Most keywords result in a python `datetime` object being
        wrapped, but certain cases use a `time` object.  If the When is only a
        `time` wrapper then some of the methods will not be available.
        
        :param datetime:
            Create `When` using a python `datetime` object
        :param date:
            Create `When` using a python `date` object, can be used in
            conjunction with the `time` keyword.  If used without the `time`
            keyword the time portion will be set to midnight.
        :param time:
            Create `When` using a python `time` object.  If used on its own the
            date based methods of `When` will not be allowed.  This keyword
            can be used in conjunction with the `date` keyword to create a
            fully qualified `When`.
        :param time_string:
            Create `When` using a string containing time information.  Handles
            either 'hour:minute' or 'hour:minute:second'.  Like the `time`
            keyword, can be used in conjunction with `date`.
        :param epoch:
            Create `When` using an integer epoch value
        :param milli_epoch:
            Create `When` using an integer that is 1000 * an epoch value with
            the last thousands being milli-epoch.
        :param detect:
            Create `When` by parsing a string which is compared against the
            list of available string parsers.
        :param parse_*: 
            Create `When` by parsing a string using the specific 
            :ref:`Supported formats <when-formats>` given.
            For example, `parse_isoformat` expects the ISO 8601 format.
        """
        pass

    @property
    def string(self):
        """Returns a placeholder object that has an attribute for each one of
        the :ref:`Supported formats <when-formats>`.  

        Example::

            >>> When(datetime=d).string.isoformat
            1972-01-31T13:45:00.02

        """


        return When.WhenStrformat(self)
