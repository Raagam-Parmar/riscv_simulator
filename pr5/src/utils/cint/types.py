"""
# Type conversions between C-like Integers and Python Integers
"""

from src.utils.cint.uintN import UIntN


class UInt8(UIntN, width=8):
    pass


class UInt16(UIntN, width=16):
    pass


class UInt32(UIntN, width=32):
    pass


class UInt64(UIntN, width=64):
    pass


def uint8(x: int | UInt8 | UInt16 | UInt32 | UInt64) -> UInt8:
    """
    Zero-extends/truncates `int`, `uint8`, `uint16`, `uint32` and `uint64` into `uint8`.
    """

    match x:
        case int():
            return UInt8(x)
        case UInt8():
            return x
        case UInt16() | UInt32() | UInt64():
            return UInt8(x.unsigned())


def sext_uint8(x: int | UInt8 | UInt16 | UInt32 | UInt64) -> UInt8:
    """
    Sign-extends/truncates `int`, `uint8`, `uint16`, `uint32` and `uint64` into `uint8`.
    """

    match x:
        case int():
            return UInt8(x)
        case UInt8():
            return x
        case UInt16() | UInt32() | UInt64():
            return UInt8(x.signed())


def uint16(x: int | UInt8 | UInt16 | UInt32 | UInt64) -> UInt16:
    """
    Zero-extends/truncates `int`, `uint8`, `uint16`, `uint32` and `uint64` into `uint16`.
    """

    match x:
        case int():
            return UInt16(x)
        case UInt16():
            return x
        case UInt8() | UInt32() | UInt64():
            return UInt16(x.unsigned())


def sext_uint16(x: int | UInt8 | UInt16 | UInt32 | UInt64) -> UInt16:
    """
    Sign-extends/truncates `int`, `uint8`, `uint16`, `uint32` and `uint64` into `uint16`.
    """

    match x:
        case int():
            return UInt16(x)
        case UInt16():
            return x
        case UInt8() | UInt32() | UInt64():
            return UInt16(x.signed())


def uint32(x: int | UInt8 | UInt16 | UInt32 | UInt64) -> UInt32:
    """
    Zero-extends/truncates `int`, `uint8`, `uint16`, `uint32` and `uint64` into `uint32`.
    """

    match x:
        case int():
            return UInt32(x)
        case UInt32():
            return x
        case UInt8() | UInt16() | UInt64():
            return UInt32(x.unsigned())


def sext_uint32(x: int | UInt8 | UInt16 | UInt32 | UInt64) -> UInt32:
    """
    Sign-extends/truncates `int`, `uint8`, `uint16`, `uint32` and `uint64` into `uint32`.
    """

    match x:
        case int():
            return UInt32(x)
        case UInt32():
            return x
        case UInt8() | UInt16() | UInt64():
            return UInt32(x.signed())


def uint64(x: int | UInt8 | UInt16 | UInt32 | UInt64) -> UInt64:
    """
    Zero-extends/truncates `int`, `uint8`, `uint16`, `uint32` and `uint64` into `uint64`.
    """

    match x:
        case int():
            return UInt64(x)
        case UInt64():
            return x
        case UInt8() | UInt16() | UInt32():
            return UInt64(x.unsigned())


def sext_uint64(x: int | UInt8 | UInt16 | UInt32 | UInt64) -> UInt64:
    """
    Sign-extends/truncates `int`, `uint8`, `uint16`, `uint32` and `uint64` into `uint64`.
    """

    match x:
        case int():
            return UInt64(x)
        case UInt64():
            return x
        case UInt8() | UInt16() | UInt32():
            return UInt64(x.signed())
