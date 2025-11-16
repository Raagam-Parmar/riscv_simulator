"""
# Random Acccess Memory
"""

from typing import Dict, List
from dataclasses import dataclass

from src.utils.logger import PR5Logger
from src.utils.pretty import pp_word
from src.utils.cint import *
from src.utils.stats import Statistics


RAM_WIDTH: int = 8
"""
Width of memory cell, 8-bits
"""

RAM_DEPTH: int = 2**32
"""
Depth of the RAM, 2^32.
"""

t_addr = UInt32
"""
Address is a 32-bit unsigned integer
"""


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

    def __init__(self, address: UInt32, align: int):
        super().__init__(f"Address {address} is not {align}-byte aligned")


class InvalidRange(Exception):
    """
    Invalid range extremums
    """

    def __init__(self, min: t_addr, max: t_addr):
        self.message = f"Invalid range: min: {min}, max: {max}."
        super().__init__(self.message)


class UnwrittenMemoryAddress(Exception):
    """
    Requested to read form an unwritten memory address
    """

    def __init__(self, addr: UInt32):
        self.message = f"Address {addr} has not been written to the RAM and hence \
        should not be read from the RAM."
        super().__init__(self.message)


class RAMError(Exception):
    def __init__(self, msg: str):
        self.message = msg
        super().__init__(msg)


@dataclass(frozen=True)
class RAMConfig:
    latency: int


class RAM32:
    def __init__(
        self, ram_config: RAMConfig, logger: PR5Logger, stats: Statistics
    ) -> None:
        """Initialise a RAM, 32-bit addressible and 32-bit wide.

        :param logger: RAM events logger
        """

        self.data: Dict[UInt32, UInt8] = {}
        """Address (`uint32`) to byte (`uint8`) hashmap"""

        self.logger = logger
        self.latency = ram_config.latency
        self.stats = stats

    def _check_halfword_addr(self, address: t_addr) -> None:
        """
        Verify that the halfword address is 2-byte aligned

        :raises AddressMisaligned: If address is not 2-byte aligned
        """

        if address & 0b1 != 0:
            raise AddressMisaligned(address, 2)

    def _check_word_addr(self, address: t_addr) -> None:
        """
        Verify that the word address is 4-byte aligned

        :raises AddressMisaligned: If address is not 4-byte aligned
        """

        if address & 0b11 != 0:
            raise AddressMisaligned(address, 4)

    # ---------------------------------------------------------------------------- #
    # Functions for reading and writing bytes

    def read_byte(self, address: t_addr, incr: bool = True) -> Byte:
        """
        Read a byte at `address`.

        :param address: LSB address of the byte

        :raises UnwrittenMemoryAddress: If `address` is not written to, previously
        :raises AddressOutOfRange: If address is out of byte range
        """

        if address not in self.data:
            raise UnwrittenMemoryAddress(address)

        if incr:
            self.stats.increment_memory_access()
            self.stats.increment_clock_cycle(self.latency)

        return self.data[address]

    def write_byte(self, address: t_addr, data: Byte, incr: bool = True) -> None:
        """
        Write a byte at `address`.

        :param address: LSB address of the byte
        """

        if incr:
            self.stats.increment_memory_access()
            self.stats.increment_clock_cycle(self.latency)

        self.data[address] = data

    # ---------------------------------------------------------------------------- #
    # Functions for reading and writing halfwords (2 bytes)

    def read_halfword(self, address: t_addr) -> HalfWord:
        """
        Read a halfword at `address`.

        :param address: LSB address of the halfword

        :raises AddressMisaligned: If address is not 2-byte aligned
        """

        self._check_halfword_addr(address)

        data = uint16(0)

        for i in range(2):
            byte = self.read_byte(address + i, incr=False)
            byte = uint16(byte)
            data = data | byte << (i * RAM_WIDTH)

        self.stats.increment_memory_access()
        self.stats.increment_clock_cycle(self.latency)
        return data

    def write_halfword(self, address: t_addr, data: HalfWord) -> None:
        """
        Read a halfword at `address`.

        :param address: LSB address of the halfword

        :raises AddressMisaligned: If address is not 2-byte aligned
        """

        self._check_halfword_addr(address)

        for i in range(2):
            byte = data >> (i * RAM_WIDTH)
            self.write_byte(address + i, uint8(byte), incr=False)

        self.stats.increment_memory_access()
        self.stats.increment_clock_cycle(self.latency)

    # ---------------------------------------------------------------------------- #
    # Functions for reading and writing word (4 bytes)

    def read_word(self, address: t_addr) -> Word:
        """
        Read a word at `address`.

        :param address: LSB address of the word
        :raises AddressMisaligned: If address is not 4-byte aligned
        :raises AddressOutOfRange: If address is out of word range
        """

        self._check_word_addr(address)

        data = uint32(0)

        for i in range(4):
            byte = self.read_byte(address + i, incr=False)
            data |= uint32(byte) << (i * RAM_WIDTH)

        self.stats.increment_memory_access()
        self.stats.increment_clock_cycle(self.latency)
        return data

    def write_word(self, address: t_addr, data: Word) -> None:
        """
        Read a word at `address`.

        :param address: LSB address of the word

        :raises AddressMisaligned: If address is not 4-byte aligned
        """

        self._check_word_addr(address)

        for i in range(4):
            byte = uint8((data >> (i * RAM_WIDTH)))
            self.write_byte(address + i, byte, incr=False)

        self.stats.increment_memory_access()
        self.stats.increment_clock_cycle(self.latency)

    # ---------------------------------------------------------------------------- #
    # Function for reading multiple bytes

    def read_bytes_many(self, address: t_addr, count: int) -> List[Byte]:
        """
        Read `count` many bytes, starting at `address`. Unwritten bytes are set to
        zeroes.
        """
        if count < 0:
            raise RAMError(f"Byte count ({count}) must be non-negative")

        many_bytes = [self.data.get(address + i, UInt8(0)) for i in range(count)]
        self.stats.increment_memory_access()
        self.stats.increment_clock_cycle(self.latency)
        return many_bytes

    def write_bytes_many(self, address: t_addr, many_bytes: List[Byte]) -> None:
        """
        Write `many_bytes` into the RAM, starting from base `address`
        """
        count = len(many_bytes)

        for i in range(count):
            self.write_byte(address + i, many_bytes[i])

        self.stats.increment_memory_access()
        self.stats.increment_clock_cycle(self.latency)

    def clear(self) -> None:
        """
        Clear the RAM
        """

        self.data.clear()

    def load(self, data: bytes, base_addr: t_addr) -> int:
        """
        Load into RAM the contents in `bytes` starting at `base_addr`

        :param data: Bytes to load into the memory
        :param base_addr: Base address of load in the memory

        :return: Number of bytes written
        """

        for offset, byte in enumerate(data):
            self.write_byte(base_addr + offset, uint8(byte), incr=False)

        return len(data)

    def print_words(
        self,
        min_word_addr: t_addr,
        max_word_addr: t_addr,
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

        addr_range = range(min_word_addr.value, max_word_addr.value + 1, 4)
        addr_range = reversed(addr_range) if higher_at_top else addr_range

        for wordAddr in addr_range:
            wordAddr = uint32(wordAddr)
            addr_pp = pp_word(wordAddr.value, RAM_WIDTH, "")
            word_pp = pp_word(
                word=self.read_word(wordAddr).value,
                width=RAM_WIDTH,
                delimit="",
                little_endian=little_endian,
            )

            self.logger.debug(f" mem[{addr_pp}] -> {word_pp}")
            self.logger.out(f" {addr_pp} => {word_pp}")
            # print(bits.pp_word(wordAddr, self.width, ''), end=':\t')
            # print(bits.pp_word(self.read_word(wordAddr), self.width, delimit='', little_endian=little_endian))
