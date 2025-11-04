"""
# Simulation for 16-bit Unsigned Integers
"""

from __future__ import annotations

from src.utils.bits import unsigned_max, unsigned_min, sign_extend

UINT16_WIDTH = 16
"""
Width of 16-bit unsigned integer
"""

UINT16_MAX = unsigned_max(UINT16_WIDTH)
"""
Maximum 16-bit unsigned integer
"""

UINT16_MIN = unsigned_min()
"""
Minimum 16-bit unsigned integer
"""


class UInt16:
    """
    Emulates 16-bit unsigned integers in Python
    """

    def __init__(self, value: int):
        self.value = value % (UINT16_MAX + 1)

    def signed_int(self) -> int:
        """
        Interprets the value in 2's complement and returns the equivalent Python integer
        """

        return sign_extend(self.value, UINT16_WIDTH)

    def unsigned_int(self) -> int:
        """
        Returns the equivalent Python integer
        """

        return self.value

    # -------------------------------------------------------------------------------- #
    # Arithmetic Operations

    def __add__(self, other: UInt16) -> UInt16:
        return UInt16(self.value + other.value)

    def __sub__(self, other: UInt16) -> UInt16:
        return UInt16(self.value - other.value)

    def __mul__(self, other: UInt16) -> UInt16:
        return UInt16(self.value * other.value)

    def __floordiv__(self, other: UInt16) -> UInt16:
        return UInt16(self.value // other.value)

    def __mod__(self, other: UInt16) -> UInt16:
        return UInt16(self.value % other.value)

    def __neg__(self) -> UInt16:
        return UInt16(-1 * self.value)

    # -------------------------------------------------------------------------------- #
    # Bitwise Operations

    def __and__(self, other: UInt16 | int) -> UInt16:
        and_with = other.value if isinstance(other, UInt16) else other
        return UInt16(self.value & and_with)

    def __or__(self, other: UInt16 | int) -> UInt16:
        or_with = other.value if isinstance(other, UInt16) else other
        return UInt16(self.value | or_with)

    def __invert__(self) -> UInt16:
        return UInt16(self.value ^ UINT16_MAX)

    def __xor__(self, other: UInt16 | int) -> UInt16:
        xor_with = other.value if isinstance(other, UInt16) else other
        return UInt16(self.value | xor_with)

    def __lshift__(self, other: UInt16 | int) -> UInt16:
        shift = other.value if isinstance(other, UInt16) else other
        shift &= 0b11111
        return UInt16(self.value << shift)

    def __rshift__(self, other: UInt16 | int) -> UInt16:
        shift = other.value if isinstance(other, UInt16) else other
        shift &= 0b11111
        return UInt16(self.value >> shift)

    def sra(self, other: UInt16 | int) -> UInt16:
        shift = other.value if isinstance(other, UInt16) else other
        shift &= 0b11111
        signed_val = self.signed_int()
        return UInt16(signed_val >> shift)

    # -------------------------------------------------------------------------------- #
    # Comparison Operations

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UInt16):
            return NotImplemented

        return self.value == other.value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, UInt16):
            return NotImplemented

        return self.value < other.value

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, UInt16):
            return NotImplemented

        return self.value > other.value

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)

        if result is NotImplemented:
            return NotImplemented

        return not result

    def __le__(self, other: object) -> bool:
        if not isinstance(other, UInt16):
            return NotImplemented

        return self.value <= other.value

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, UInt16):
            return NotImplemented

        return self.value >= other.value

    # -------------------------------------------------------------------------------- #
    # Pretty Printing

    def __str__(self) -> str:
        return f"{hex(self.value).zfill(UINT16_WIDTH)}:u16"

    def __repr__(self) -> str:
        return f"UInt16({self.value})"

    # -------------------------------------------------------------------------------- #
    # Utility Functions

    def __hash__(self) -> int:
        return hash(self.value)
