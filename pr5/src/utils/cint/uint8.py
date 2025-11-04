"""
# Simulation for 8-bit Unsigned Integers
"""

from __future__ import annotations

from src.utils.bits import unsigned_max, unsigned_min, sign_extend

UINT8_WIDTH = 8
"""
Width of 8-bit unsigned integer
"""

UINT8_MAX = unsigned_max(UINT8_WIDTH)
"""
Maximum 8-bit unsigned integer
"""

UINT8_MIN = unsigned_min()
"""
Minimum 8-bit unsigned integer
"""


class UInt8:
    """
    Emulates 8-bit unsigned integers in Python
    """

    def __init__(self, value: int):
        self.value = value % (UINT8_MAX + 1)

    def signed_int(self) -> int:
        """
        Interprets the value in 2's complement and returns the equivalent Python integer
        """

        return sign_extend(self.value, UINT8_WIDTH)

    def unsigned_int(self) -> int:
        """
        Returns the equivalent Python integer
        """

        return self.value

    # -------------------------------------------------------------------------------- #
    # Arithmetic Operations

    def __add__(self, other: UInt8) -> UInt8:
        return UInt8(self.value + other.value)

    def __sub__(self, other: UInt8) -> UInt8:
        return UInt8(self.value - other.value)

    def __mul__(self, other: UInt8) -> UInt8:
        return UInt8(self.value * other.value)

    def __floordiv__(self, other: UInt8) -> UInt8:
        return UInt8(self.value // other.value)

    def __mod__(self, other: UInt8) -> UInt8:
        return UInt8(self.value % other.value)

    def __neg__(self) -> UInt8:
        return UInt8(-1 * self.value)

    # -------------------------------------------------------------------------------- #
    # Bitwise Operations

    def __and__(self, other: UInt8 | int) -> UInt8:
        and_with = other.value if isinstance(other, UInt8) else other
        return UInt8(self.value & and_with)

    def __or__(self, other: UInt8 | int) -> UInt8:
        or_with = other.value if isinstance(other, UInt8) else other
        return UInt8(self.value | or_with)

    def __invert__(self) -> UInt8:
        return UInt8(self.value ^ UINT8_MAX)

    def __xor__(self, other: UInt8 | int) -> UInt8:
        xor_with = other.value if isinstance(other, UInt8) else other
        return UInt8(self.value | xor_with)

    def __lshift__(self, other: UInt8 | int) -> UInt8:
        shift = other.value if isinstance(other, UInt8) else other
        shift &= 0b11111
        return UInt8(self.value << shift)

    def __rshift__(self, other: UInt8 | int) -> UInt8:
        shift = other.value if isinstance(other, UInt8) else other
        shift &= 0b11111
        return UInt8(self.value >> shift)

    def sra(self, other: UInt8 | int) -> UInt8:
        shift = other.value if isinstance(other, UInt8) else other
        shift &= 0b11111
        signed_val = self.signed_int()
        return UInt8(signed_val >> shift)

    # -------------------------------------------------------------------------------- #
    # Comparison Operations

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UInt8):
            return NotImplemented

        return self.value == other.value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, UInt8):
            return NotImplemented

        return self.value < other.value

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, UInt8):
            return NotImplemented

        return self.value > other.value

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)

        if result is NotImplemented:
            return NotImplemented

        return not result

    def __le__(self, other: object) -> bool:
        if not isinstance(other, UInt8):
            return NotImplemented

        return self.value <= other.value

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, UInt8):
            return NotImplemented

        return self.value >= other.value

    # -------------------------------------------------------------------------------- #
    # Pretty Printing

    def __str__(self) -> str:
        return f"{hex(self.value).zfill(UINT8_WIDTH)}:u8"

    def __repr__(self) -> str:
        return f"UInt8({self.value})"

    # -------------------------------------------------------------------------------- #
    # Utility Functions

    def __hash__(self) -> int:
        return hash(self.value)
