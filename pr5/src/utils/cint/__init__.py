"""
# C-like Integers
"""

from src.utils.cint.types import (
    uint8,
    sext_uint8,
    uint16,
    sext_uint16,
    uint32,
    sext_uint32,
    uint64,
    sext_uint64,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
)

Byte = UInt8
byte = uint8

HalfWord = UInt16
halfword = uint16

Word = UInt32
word = uint32

DoubleWord = UInt64
doubleword = uint64


__all__ = [
    "UInt8",
    "uint8",
    "sext_uint8",
    "UInt16",
    "uint16",
    "sext_uint16",
    "UInt32",
    "uint32",
    "sext_uint32",
    "UInt64",
    "uint64",
    "sext_uint64",
    "Byte",
    "byte",
    "HalfWord",
    "halfword",
    "Word",
    "word",
    "DoubleWord",
    "doubleword",
]
