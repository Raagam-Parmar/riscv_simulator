from logger import PR5Logger
from typing import Dict
from utils.pretty import pp_word

import utils.bits as bits


class AddressOutOfRange(Exception):
    def __init__(self, addr: int, maxAddr: int):
        self.message = f"Address {addr} out of range [0, {maxAddr}]"
        super().__init__(self.message)


class AddressMisaligned(Exception):
    def __init__(self, address: int, align: int):
        super().__init__(f"Address {address} is not {align}-byte aligned")


class InvalidRange(Exception):
    def __init__(self, min: int, max: int):
        self.message = f"Invalid range: min: {min}, max: {max}."
        super().__init__(self.message)


class RAM:
    def __init__(self, width: int, addr_width: int, logger: PR5Logger) -> None:
        """Initialise the RAM with specified `width` and `address width`.

        Args:
            width/byte: Width in bits for each memory cell
            addr_width: Log2 of the number of such memory cells
        """
        self.width = width
        self.depth: int = 2**addr_width
        self.addr_width = addr_width
        self.BYTE_MASK = (1 << self.width) - 1

        self.data: Dict[int, int] = {}

        self.logr = logger

    def _check_byte_addr(self, address: int) -> None:
        addr_max = self.depth - 1

        if not (0 <= address <= addr_max):
            raise AddressOutOfRange(address, addr_max)

    def _check_word_addr(self, address: int) -> None:
        if address & 0b11:
            raise AddressMisaligned(address, 4)

        addr_max = self.depth - 4
        if not (0 <= address <= addr_max):
            raise AddressOutOfRange(address, addr_max)

    def _verify_data(self, data: int, width: int) -> None:
        bits.verifyUnsigned(data, width)

    def read_byte(self, address: int) -> int:
        self._check_byte_addr(address)
        return self.data.get(address, 0)

    def write_byte(self, address: int, data: int) -> None:
        self._check_byte_addr(address)
        self._verify_data(data, self.width)

        if data == 0:
            self.data.pop(address, None)
        else:
            self.data[address] = data

    def read_word(self, address: int) -> int:
        self._check_word_addr(address)

        data: int = 0

        for i in range(4):
            byte = self.read_byte(address + i) & self.BYTE_MASK
            data |= byte << (i * self.width)

        return data

    def write_word(self, address: int, data: int) -> None:
        self._check_word_addr(address)
        self._verify_data(data, self.width * 4)

        mask = bits.unsigned_max(self.width)

        for i in range(4):
            byte = (data >> (i * self.width)) & mask
            self.write_byte(address + i, byte)

    def clear(self) -> None:
        """Clear RAM to all zeroes."""
        self.data.clear()

    def load(self, data: bytes, base_addr: int) -> int:
        """Load into RAM the contents in `bytes` starting at `base_addr`

        Returns:
            int: Number of bytes written
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
        """Print the contents of the RAM, starting at 4-byte aligned `min_word_addr` and `max_word_addr`.

        If `higher_at_top` is set (default), higher addresses are printed first, otherwise lower addresses are printed first.

        If `little_endian` is set (default), bytes are printing in little endian format, otherwise big endian format.

        Raises:
            InvalidRange: If `min_word_addr` > `max_word_addr`
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

            self.logr.debug(f" mem[{addr_pp}] -> {word_pp}")
            self.logr.out(f" {addr_pp} => {word_pp}")
            # print(bits.pp_word(wordAddr, self.width, ''), end=':\t')
            # print(bits.pp_word(self.read_word(wordAddr), self.width, delimit='', little_endian=little_endian))
