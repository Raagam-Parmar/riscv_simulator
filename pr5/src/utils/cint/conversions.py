"""
# Type conversions between UInt32 and UInt64
"""

from src.utils.cint.int32 import UInt32
from src.utils.cint.int64 import UInt64


def uint32_to_uint64(value: UInt32) -> UInt64:
    """
    Zero-extend UInt32 to UInt64
    """

    return UInt64(value.value)


def uint64_to_uint32(value: UInt64) -> UInt32:
    """
    Truncate UInt64 to UInt32
    """

    return UInt32(value.value)
