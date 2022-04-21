from enum import Enum


class StrEnum(Enum):
    """
    Enum with string description in value field
    """

    def __str__(self):
        return self.value
