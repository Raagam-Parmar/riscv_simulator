"""
# Registers and Register Files
"""

from src.utils.cint import *


class InvalidSize(Exception):
    """
    Invalid size parameter for register file
    """

    def __init__(self, size: int):
        self.message = f"Size for register file {size} must be positive."
        super().__init__(self.message)


class RegisterOutOfBounds(Exception):
    """
    Requested register is out of bounds of the register file
    """

    def __init__(self, register: int, size: int):
        self.message = f"Can not write to out-of-bounds register {register} on register file of size {size}."
        super().__init__(self.message)


class Register32:
    def __init__(self) -> None:
        """
        Create a new 32-bit register
        """

        self.value: UInt32 = UInt32(0)

    def read(self) -> UInt32:
        """
        Read the register

        :return: Contents of the register
        """

        return self.value

    def write(self, value: UInt32) -> None:
        """
        Write to the register
        """

        self.value = value


class RegisterFile32:
    def __init__(self, size: int, zero_reg: bool) -> None:
        """
        Create a new 32-bit register file

        :param size: Number of registers in the register file
        :param zero_reg: Should 0th register always contain constant zero?
        """

        if size <= 0:
            raise InvalidSize(size)

        self.size = size
        self.registers = [Register32() for _ in range(size)]
        self.zreg = zero_reg

    def write(self, rd: int, value: UInt32) -> None:
        """
        Write `value` to register `rd`

        :param rd: Destination register
        :param value: Contents to write to `rd`
        """

        if not (0 <= rd < self.size):
            raise RegisterOutOfBounds(rd, self.size)

        if self.zreg and (rd == 0):
            return

        self.registers[rd].write(value)

    def read(self, rs: int) -> UInt32:
        """
        Read the register `rs`

        :param rs: Source register

        :return: Contents of `rs`
        """

        if not (0 <= rs < self.size):
            raise RegisterOutOfBounds(rs, self.size)

        if self.zreg and (rs == 0):
            return UInt32(0)

        return self.registers[rs].read()
