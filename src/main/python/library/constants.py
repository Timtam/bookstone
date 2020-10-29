from enum import IntEnum, auto, unique


@unique
class INDEXING(IntEnum):

    READING = auto()
    GROUPING = auto()


class PROGRESS(IntEnum):

    # int, increasing the current maximum by that amount
    UPDATE_MAXIMUM = auto()
    # int, increase the value by that amount
    VALUE = auto()

    # int, set the maximum to that amount
    MAXIMUM = auto()

    # str, message to display as label in the progress window
    # following format strings should be passed in:
    # maximum
    # value
    MESSAGE = auto()
