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
