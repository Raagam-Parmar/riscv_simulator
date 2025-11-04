"""
# Simulation for 64-bit Unsigned Integers
"""

from __future__ import annotations

from src.utils.bits import unsigned_max, unsigned_min, sign_extend


UINT64_WIDTH = 64
"""
Width of 64-bit unsigned integer
"""

UINT64_MAX = unsigned_max(UINT64_WIDTH)
"""
Maximum 64-bit unsigned integer
"""

UINT64_MIN = unsigned_min()
"""
Minimum 64-bit unsigned integer
"""


class UInt64:
    """
    Emulates 64-bit unsigned integers in Python
    """

    def __init__(self, value: int):
        self.value = value % (UINT64_MAX + 1)

    def signed_int(self) -> int:
        """
        Interprets the value in 2's complement and returns the equivalent Python integer
        """

        return sign_extend(self.value, UINT64_WIDTH)

    def unsigned_int(self) -> int:
        """
        Returns the unsigned value as an equivalent Python integer
        """

        return self.value

    # -------------------------------------------------------------------------------- #
    # Arithmetic Operations

    def __add__(self, other: UInt64) -> UInt64:
        return UInt64(self.value + other.value)

    def __sub__(self, other: UInt64) -> UInt64:
        return UInt64(self.value - other.value)

    def __mul__(self, other: UInt64) -> UInt64:
        return UInt64(self.value * other.value)

    def __floordiv__(self, other: UInt64) -> UInt64:
        return UInt64(self.value // other.value)

    def __mod__(self, other: UInt64) -> UInt64:
        return UInt64(self.value % other.value)

    def __neg__(self) -> UInt64:
        return UInt64(-1 * self.value)

    # -------------------------------------------------------------------------------- #
    # Bitwise Operations

    def __and__(self, other: UInt64) -> UInt64:
        return UInt64(self.value & other.value)

    def __or__(self, other: UInt64) -> UInt64:
        return UInt64(self.value | other.value)

    def __invert__(self) -> UInt64:
        return UInt64(self.value ^ UINT64_MAX)

    def __xor__(self, other: UInt64) -> UInt64:
        return UInt64(self.value ^ other.value)

    def __lshift__(self, other: UInt64 | int) -> UInt64:
        shift = other.value if isinstance(other, UInt64) else other
        shift &= 0b111111
        return UInt64(self.value << shift)

    def __rshift__(self, other: UInt64 | int) -> UInt64:
        shift = other.value if isinstance(other, UInt64) else other
        shift &= 0b111111
        return UInt64(self.value >> shift)

    def sra(self, other: UInt64 | int) -> UInt64:
        shift = other.value if isinstance(other, UInt64) else other
        shift &= 0b111111
        signed_val = self.signed_int()
        return UInt64(signed_val >> shift)

    # -------------------------------------------------------------------------------- #
    # Comparison Operations

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UInt64):
            return NotImplemented

        return self.value == other.value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, UInt64):
            return NotImplemented

        return self.value < other.value

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, UInt64):
            return NotImplemented

        return self.value > other.value

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)

        if result is NotImplemented:
            return NotImplemented

        return not result

    def __le__(self, other: object) -> bool:
        if not isinstance(other, UInt64):
            return NotImplemented

        return self.value <= other.value

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, UInt64):
            return NotImplemented

        return self.value >= other.value

    # -------------------------------------------------------------------------------- #
    # Pretty Printing

    def __str__(self) -> str:
        return f"{hex(self.value).zfill(UINT64_WIDTH)}:u64"

    def __repr__(self) -> str:
        return f"UInt64({self.value})"

    # -------------------------------------------------------------------------------- #
    # Utility Functions

    def __hash__(self) -> int:
        return hash(self.value)
