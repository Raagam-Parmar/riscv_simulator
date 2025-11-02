"""
# Random Acccess Memory
"""

from typing import Dict

from src.utils.logger import PR5Logger
from src.utils.pretty import pp_word
from src.utils import bits


class AddressOutOfRange(Exception):
    """
    Requested to read from or write to an address which is out of range of the RAM
    """

    def __init__(self, addr: int, maxAddr: int):
        self.message = f"Address {addr} out of range [0, {maxAddr}]"
        super().__init__(self.message)


class AddressMisaligned(Exception):
    """
    Requested to read from or write to an address which is not aligned to given boundary
    """

    def __init__(self, address: int, align: int):
        super().__init__(f"Address {address} is not {align}-byte aligned")


class InvalidRange(Exception):
    """
    Invalid range extremums
    """

    def __init__(self, min: int, max: int):
        self.message = f"Invalid range: min: {min}, max: {max}."
        super().__init__(self.message)


class UnwrittenMemoryAddress(Exception):
    """
    Requested to read form an unwritten memory address
    """

    def __init__(self, addr: int):
        self.message = f"Address {addr} has not been written to the RAM and hence \
        should not be read from the RAM."
        super().__init__(self.message)


class RAM:
    def __init__(self, width: int, addr_width: int, logger: PR5Logger) -> None:
        """Initialise the RAM with specified `width` and `address width`.

        :param width: Width in bits for each memory cell
        :param addr_width: Log2 of the number of such memory cells
        :param logger: RAM events logger
        """

        self.width = width
        self.depth: int = 2**addr_width
        self.addr_width = addr_width
        self.BYTE_MASK = (1 << self.width) - 1

        self.data: Dict[int, int] = {}

        self.logger = logger

    def _check_byte_addr(self, address: int) -> None:
        """
        Verify that the byte address is within byte range

        :raises AddressOutOfRange: If address is out of byte range
        """

        addr_max = self.depth - 1

        if not (0 <= address <= addr_max):
            raise AddressOutOfRange(address, addr_max)

    def _check_halfword_addr(self, address: int) -> None:
        """
        Verify that the halfword address is within halfword range and is 2-byte aligned

        :raises AddressMisaligned: If address is not 2-byte aligned
        :raises AddressOutOfRange: If address is out of halfword range
        """

        if address & 0b1:
            raise AddressMisaligned(address, 2)

        addr_max = self.depth - 2
        if not (0 <= address <= addr_max):
            raise AddressOutOfRange(address, addr_max)

    def _check_word_addr(self, address: int) -> None:
        """
        Verify that the word address is within word range and is 4-byte aligned

        :raises AddressMisaligned: If address is not 4-byte aligned
        :raises AddressOutOfRange: If address is out of word range
        """

        if address & 0b11:
            raise AddressMisaligned(address, 4)

        addr_max = self.depth - 4
        if not (0 <= address <= addr_max):
            raise AddressOutOfRange(address, addr_max)

    def _verify_data(self, data: int, width: int) -> None:
        """
        Verify that the data is non-negative and fits within one memory cell

        :raises UnsignedUnderflow: If the data is negative
        :raises UnsignedOverflow: If the data does not fit in one memory cell
        """

        bits.verifyUnsigned(data, width)

    # ---------------------------------------------------------------------------- #
    # Functions for reading and writing bytes

    def read_byte(self, address: int) -> int:
        """
        Read a byte at `address`.

        :param address: LSB address of the byte

        :raises UnwrittenMemoryAddress: If `address` is not written to, previously
        :raises AddressOutOfRange: If address is out of byte range
        """

        self._check_byte_addr(address)

        if address not in self.data:
            raise UnwrittenMemoryAddress(address)

        return self.data[address]

    def write_byte(self, address: int, data: int) -> None:
        """
        Write a byte at `address`.

        :param address: LSB address of the byte

        :raises AddressOutOfRange: If address is out of byte range
        :raises UnsignedUnderflow: If the data is negative
        :raises UnsignedOverflow: If the data does not fit in one memory cell
        """

        self._check_byte_addr(address)
        self._verify_data(data, self.width)

        self.data[address] = data

    # ---------------------------------------------------------------------------- #
    # Functions for reading and writing halfwords (2 bytes)

    def read_halfword(self, address: int) -> int:
        """
        Read a halfword at `address`.

        :param address: LSB address of the halfword
        :raises AddressMisaligned: If address is not 2-byte aligned
        :raises AddressOutOfRange: If address is out of halfword range
        """

        self._check_halfword_addr(address)

        data: int = 0

        for i in range(2):
            byte = self.read_byte(address + i) & self.BYTE_MASK
            data |= byte << (i * self.width)

        return data

    def write_halfword(self, address: int, data: int) -> None:
        """
        Read a halfword at `address`.

        :param address: LSB address of the halfword

        :raises AddressMisaligned: If address is not 2-byte aligned
        :raises AddressOutOfRange: If address is out of halfword range
        :raises UnsignedUnderflow: If the data is negative
        :raises UnsignedOverflow: If the data does not fit in one memory cell
        """

        self._check_halfword_addr(address)
        self._verify_data(data, self.width * 2)

        mask = bits.unsigned_max(self.width)

        for i in range(2):
            byte = (data >> (i * self.width)) & mask
            self.write_byte(address + i, byte)

    # ---------------------------------------------------------------------------- #
    # Functions for reading and writing word (4 bytes)

    def read_word(self, address: int) -> int:
        """
        Read a word at `address`.

        :param address: LSB address of the halfword
        :raises AddressMisaligned: If address is not 4-byte aligned
        :raises AddressOutOfRange: If address is out of word range
        """

        self._check_word_addr(address)

        data: int = 0

        for i in range(4):
            byte = self.read_byte(address + i) & self.BYTE_MASK
            data |= byte << (i * self.width)

        return data

    def write_word(self, address: int, data: int) -> None:
        """
        Read a word at `address`.

        :param address: LSB address of the word

        :raises AddressMisaligned: If address is not 4-byte aligned
        :raises AddressOutOfRange: If address is out of word range
        :raises UnsignedUnderflow: If the data is negative
        :raises UnsignedOverflow: If the data does not fit in one memory cell
        """

        self._check_word_addr(address)
        self._verify_data(data, self.width * 4)

        mask = bits.unsigned_max(self.width)

        for i in range(4):
            byte = (data >> (i * self.width)) & mask
            self.write_byte(address + i, byte)

    # ---------------------------------------------------------------------------- #

    def clear(self) -> None:
        """
        Clear the RAM
        """

        self.data.clear()

    def load(self, data: bytes, base_addr: int) -> int:
        """
        Load into RAM the contents in `bytes` starting at `base_addr`

        :param data: Bytes to load into the memory
        :param base_addr: Base address of load in the memory

        :return: Number of bytes written
        """

        for offset, byte in enumerate(data):
            self.write_byte(base_addr + offset, byte)

        return len(data)

    def print_words(
        self,
        min_word_addr: int,
        max_word_addr: int,
        higher_at_top: bool = True,
        little_endian: bool = True,
    ) -> None:
        """
        Print the contents of the RAM, starting at 4-byte aligned `min_word_addr` and `max_word_addr`.

        :param min_word_addr: Starting address for printing (inclusive)
        :param max_word_addr: Ending address for printing (inclusive)

        :param higher_at_top: If set (default), higher addresses are printed first,
        otherwise lower addresses are printed first.

        :param little_endian: If set (default), bytes are printing in little endian
        format, otherwise big endian format.

        :raises InvalidRange: If `min_word_addr` > `max_word_addr`
        """

        if min_word_addr > max_word_addr:
            raise InvalidRange(min_word_addr, max_word_addr)

        self._check_word_addr(min_word_addr)
        self._check_word_addr(max_word_addr)

        addr_range = range(min_word_addr, max_word_addr + 1, 4)
        addr_range = reversed(addr_range) if higher_at_top else addr_range

        for wordAddr in addr_range:
            addr_pp = pp_word(wordAddr, self.width, "")
            word_pp = pp_word(
                word=self.read_word(wordAddr),
                width=self.width,
                delimit="",
                little_endian=little_endian,
            )

            self.logger.debug(f" mem[{addr_pp}] -> {word_pp}")
            self.logger.out(f" {addr_pp} => {word_pp}")
            # print(bits.pp_word(wordAddr, self.width, ''), end=':\t')
            # print(bits.pp_word(self.read_word(wordAddr), self.width, delimit='', little_endian=little_endian))
