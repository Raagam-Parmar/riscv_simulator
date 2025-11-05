from __future__ import annotations
from math import ceil
from typing import Self
from src.utils.bits import unsigned_max, sign_extend


class UIntN:
    """
    Emulates N-bit unsiged integers
    """

    UINT_WIDTH: int
    """Width of unsigned integer"""

    UINT_MAX: int
    """Maximum unsigned integer"""

    HEX_DIGITS: int
    """Hexadecimal digits to represent unsigned integer"""

    def __init_subclass__(cls, width: int) -> None:
        cls.UINT_WIDTH = width
        cls.UINT_MAX = unsigned_max(cls.UINT_WIDTH)
        cls.HEX_DIGITS = ceil(cls.UINT_WIDTH / 4)

    def __init__(self, value: int):
        self.value = value % (self.UINT_MAX + 1)

    # ---------------------------- Signed/Unsigned views ------------------------- #

    def signed(self) -> int:
        """
        Interprets the value in 2's complement and returns the equivalent Python integer
        """

        return sign_extend(self.value, self.UINT_WIDTH)

    def unsigned(self) -> int:
        """
        Returns the equivalent Python integer
        """
        return self.value

    # ------------------------------- Arithmetic --------------------------------- #

    def __neg__(self) -> Self:
        return type(self)(-self.value)

    def __add__(self, other: Self) -> Self:
        return type(self)(self.value + other.value)

    def __iadd__(self, other: Self) -> Self:
        self.value = (self.value + other.value) % (self.UINT_MAX + 1)
        return self

    def __radd__(self, other: Self) -> Self:
        return type(self)(other.value + self.value)

    def __sub__(self, other: Self) -> Self:
        return type(self)(self.value - other.value)

    def __isub__(self, other: Self) -> Self:
        self.value = (self.value - other.value) % (self.UINT_MAX + 1)
        return self

    def __rsub__(self, other: Self) -> Self:
        return type(self)(other.value - self.value)

    def __mul__(self, other: Self) -> Self:
        return type(self)(self.value * other.value)

    def __imul__(self, other: Self) -> Self:
        self.value = (self.value * other.value) % (self.UINT_MAX + 1)
        return self

    def __rmul__(self, other: Self) -> Self:
        return type(self)(other.value * self.value)

    def __floordiv__(self, other: Self) -> Self:
        return type(self)(self.value // other.value)

    def __ifloordiv__(self, other: Self) -> Self:
        self.value = (self.value // other.value) % (self.UINT_MAX + 1)
        return self

    def __rfloordiv__(self, other: Self) -> Self:
        return type(self)(other.value // self.value)

    def __mod__(self, other: Self) -> Self:
        return type(self)(self.value % other.value)

    def __imod__(self, other: Self) -> Self:
        self.value = (self.value % other.value) % (self.UINT_MAX + 1)
        return self

    def __rmod__(self, other: Self) -> Self:
        return type(self)(other.value % self.value)

    # -------------------------------- Bitwise ----------------------------------- #

    def __invert__(self) -> Self:
        return type(self)(self.value ^ self.UINT_MAX)

    def __and__(self, other: Self) -> Self:
        return type(self)(self.value & other.value)

    def __iand__(self, other: Self) -> Self:
        self.value &= other.value
        return self

    def __rand__(self, other: Self) -> Self:
        return type(self)(other.value & self.value)

    def __or__(self, other: Self) -> Self:
        return type(self)(self.value | other.value)

    def __ior__(self, other: Self) -> Self:
        self.value |= other.value
        return self

    def __ror__(self, other: Self) -> Self:
        return type(self)(other.value | self.value)

    def __xor__(self, other: Self) -> Self:
        return type(self)(self.value ^ other.value)

    def __ixor__(self, other: Self) -> Self:
        self.value ^= other.value
        return self

    def __rxor__(self, other: Self) -> Self:
        return type(self)(other.value ^ self.value)

    def __lshift__(self, other: Self) -> Self:
        shift = other.value
        shift %= self.UINT_WIDTH
        return type(self)(self.value << shift)

    def __ilshift__(self, other: Self) -> Self:
        shift = other.value
        shift %= self.UINT_WIDTH
        self.value = (self.value << shift) & self.UINT_MAX
        return self

    def __rlshift__(self, other: Self) -> Self:
        shift = other.value
        shift %= self.UINT_WIDTH
        return type(self)(other.value << shift)

    def __rshift__(self, other: Self) -> Self:
        shift = other.value
        shift %= self.UINT_WIDTH
        return type(self)(self.value >> shift)

    def __irshift__(self, other: Self) -> Self:
        shift = other.value
        shift %= self.UINT_WIDTH
        self.value >>= shift
        return self

    def __rrshift__(self, other: Self) -> Self:
        shift = other.value
        shift %= self.UINT_WIDTH
        v = other.value
        return type(self)((v % (self.UINT_MAX + 1)) >> shift)

    def sra(self, other: Self) -> Self:
        """
        Arithmetic right shift
        """
        shift = other.value
        shift %= self.UINT_WIDTH
        return type(self)(self.signed() >> shift)

    # ------------------------------- Comparisons -------------------------------- #

    def __eq__(self, other: object) -> bool:
        if type(other) is type(self):
            return self.value == other.value

        if isinstance(other, int):
            return self.value == (other % (self.UINT_MAX + 1))

        return NotImplemented

    def __lt__(self, other: Self) -> bool:
        return self.value < other.value

    def __gt__(self, other: Self) -> bool:
        return self.value > other.value

    def __le__(self, other: Self) -> bool:
        return self.value <= other.value

    def __ge__(self, other: Self) -> bool:
        return self.value >= other.value

    def lt_signed(self, other: Self) -> bool:
        return self.signed() < other.signed()

    def gt_signed(self, other: Self) -> bool:
        return self.signed() > other.signed()

    # --------------------------------- Display ---------------------------------- #

    def __str__(self) -> str:
        return f"0x{self.value:0{self.HEX_DIGITS}X}:u{self.UINT_WIDTH}"

    def __repr__(self) -> str:
        return f"UInt{self.UINT_WIDTH}({self.value})"

    def __int__(self) -> int:
        return self.value

    # --------------------------------- Utility ---------------------------------- #

    def __hash__(self) -> int:
        return hash(self.value)
