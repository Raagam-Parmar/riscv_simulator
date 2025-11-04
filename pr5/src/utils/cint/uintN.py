from __future__ import annotations
from math import ceil

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

    def __neg__(self) -> UIntN:
        return UIntN(-self.value)

    def __add__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        return UIntN(self.value + other_value)

    def __iadd__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        self.value = (self.value + other_value) % (self.UINT_MAX + 1)
        return self

    def __radd__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        return UIntN(other_value + self.value)

    def __sub__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        return UIntN(self.value - other_value)

    def __isub__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        self.value = (self.value - other_value) % (self.UINT_MAX + 1)
        return self

    def __rsub__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        return UIntN(other_value - self.value)

    def __mul__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        return UIntN(self.value * other_value)

    def __imul__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        self.value = (self.value * other_value) % (self.UINT_MAX + 1)
        return self

    def __rmul__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        return UIntN(other_value * self.value)

    def __floordiv__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        return UIntN(self.value // other_value)

    def __ifloordiv__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        self.value = (self.value // other_value) % (self.UINT_MAX + 1)
        return self

    def __rfloordiv__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        return UIntN(other_value // self.value)

    def __mod__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        return UIntN(self.value % other_value)

    def __imod__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        self.value = (self.value % other_value) % (self.UINT_MAX + 1)
        return self

    def __rmod__(self, other: UIntN | int) -> UIntN:
        other_value = other.value if isinstance(other, UIntN) else other
        return UIntN(other_value % self.value)

    # -------------------------------- Bitwise ----------------------------------- #

    def __invert__(self) -> UIntN:
        return UIntN(self.value ^ self.UINT_MAX)

    def __and__(self, other: UIntN | int) -> UIntN:
        v = other.value if isinstance(other, UIntN) else other
        return UIntN(self.value & v)

    def __iand__(self, other: UIntN | int) -> UIntN:
        v = other.value if isinstance(other, UIntN) else other
        self.value &= v
        return self

    def __rand__(self, other: UIntN | int) -> UIntN:
        v = other.value if isinstance(other, UIntN) else other
        return UIntN(v & self.value)

    def __or__(self, other: UIntN | int) -> UIntN:
        v = other.value if isinstance(other, UIntN) else other
        return UIntN(self.value | v)

    def __ior__(self, other: UIntN | int) -> UIntN:
        v = other.value if isinstance(other, UIntN) else other
        self.value |= v
        return self

    def __ror__(self, other: UIntN | int) -> UIntN:
        v = other.value if isinstance(other, UIntN) else other
        return UIntN(v | self.value)

    def __xor__(self, other: UIntN | int) -> UIntN:
        v = other.value if isinstance(other, UIntN) else other
        return UIntN(self.value ^ v)

    def __ixor__(self, other: UIntN | int) -> UIntN:
        v = other.value if isinstance(other, UIntN) else other
        self.value ^= v
        return self

    def __rxor__(self, other: UIntN | int) -> UIntN:
        v = other.value if isinstance(other, UIntN) else other
        return UIntN(v ^ self.value)

    def __lshift__(self, other: UIntN | int) -> UIntN:
        shift = other.value if isinstance(other, UIntN) else other
        shift %= self.UINT_WIDTH
        return UIntN(self.value << shift)

    def __ilshift__(self, other: UIntN | int) -> UIntN:
        shift = other.value if isinstance(other, UIntN) else other
        shift %= self.UINT_WIDTH
        self.value = (self.value << shift) & self.UINT_MAX
        return self

    def __rlshift__(self, other: UIntN | int) -> UIntN:
        shift = other.value if isinstance(other, UIntN) else other
        shift %= self.UINT_WIDTH
        v = other.value if isinstance(other, UIntN) else other
        return UIntN(v << shift)

    def __rshift__(self, other: UIntN | int) -> UIntN:
        shift = other.value if isinstance(other, UIntN) else other
        shift %= self.UINT_WIDTH
        return UIntN(self.value >> shift)

    def __irshift__(self, other: UIntN | int) -> UIntN:
        shift = other.value if isinstance(other, UIntN) else other
        shift %= self.UINT_WIDTH
        self.value >>= shift
        return self

    def __rrshift__(self, other: UIntN | int) -> UIntN:
        shift = other.value if isinstance(other, UIntN) else other
        shift %= self.UINT_WIDTH
        v = other.value if isinstance(other, UIntN) else other
        return UIntN((v % (self.UINT_MAX + 1)) >> shift)

    def sra(self, other: UIntN | int) -> UIntN:
        """
        Arithmetic right shift
        """
        shift = other.value if isinstance(other, UIntN) else other
        shift %= self.UINT_WIDTH
        return UIntN(self.signed() >> shift)

    # ------------------------------- Comparisons -------------------------------- #

    def _other_val(self, other: UIntN | int) -> int:
        if isinstance(other, UIntN):
            return other.value

        return other % (self.UINT_MAX + 1)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UIntN):
            return self.value == other.value

        if isinstance(other, int):
            return self.value == (other % (self.UINT_MAX + 1))

        return NotImplemented

    def __lt__(self, other: UIntN | int) -> bool:
        v = self._other_val(other)
        return self.value < v

    def __gt__(self, other: UIntN | int) -> bool:
        v = self._other_val(other)
        return self.value > v

    def __le__(self, other: UIntN | int) -> bool:
        v = self._other_val(other)
        return self.value <= v

    def __ge__(self, other: UIntN | int) -> bool:
        v = self._other_val(other)
        return self.value >= v

    def lt_signed(self, other: UIntN | int) -> bool:
        if not isinstance(other, UIntN):
            return NotImplemented

        return self.signed() < other.signed()

    def gt_signed(self, other: UIntN | int) -> bool:
        if not isinstance(other, UIntN):
            return NotImplemented

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
