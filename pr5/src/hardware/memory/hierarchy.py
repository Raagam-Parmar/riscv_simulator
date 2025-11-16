from typing import Union

from src.hardware.memory.cache.cache import (
    CacheConfig,
    Cache32,
    DataBlock,
    WritePolicy,
    WriteSignal,
)
from src.utils.cint import *
from src.hardware.memory.ram32 import RAM32, RAMConfig
from src.utils.logger import PR5Logger
from src.utils.stats import Statistics


class MemoryHierarchyError(Exception):
    def __init__(self, msg: str):
        self.message = msg
        super().__init__(msg)


MemoryUnit = Union[Cache32, RAM32]


class MemoryHierarchy:
    def __init__(
        self,
        l1i_config: CacheConfig,
        l1d_config: CacheConfig,
        l2_config: CacheConfig,
        ram_config: RAMConfig,
        logger: PR5Logger,
        stats: Statistics,
    ) -> None:
        # TODO Error checks

        self.l1d = Cache32(l1d_config, logger, stats)
        self.l1i = Cache32(l1i_config, logger, stats)
        self.l2 = Cache32(l2_config, logger, stats)
        self.ram = RAM32(ram_config, logger, stats)
        self.block_size = self.l1d.block_size
        self.logger = logger
        self.stats = stats

        if (
            self.l1d.block_size != self.l1i.block_size
            or (self.l1d.block_size != self.l2.block_size)
            or (self.l1i.block_size != self.l2.block_size)
        ):
            raise MemoryHierarchyError(f"Caches must have same block size")

        # Instruction inteface
        if self.l1i.valid:
            self.inst_unit = self.l1i
            self.l1i.next_level = self.l2 if self.l2.valid else self.ram

        elif self.l2.valid:
            self.inst_unit = self.l2

        else:
            self.inst_unit = self.ram

        # Data inteface
        if self.l1d.valid:
            self.data_unit = self.l1d
            self.l1d.next_level = self.l2 if self.l2.valid else self.ram

        elif self.l2.valid:
            self.data_unit = self.l2

        else:
            self.data_unit = self.ram

        # L2 next level pointer
        if self.l2.valid:
            self.l2.next_level = self.ram

    def _get_base_addr(self, addr: UInt32) -> UInt32:
        """
        Return the base address in any block given `addr`
        """
        return addr & (~(UInt32(self.block_size - 1)))

    # def write_block_ram(self, addr: UInt32, new_block: DataBlock) -> None:
    #     """
    #     Write `block` into RAM, with base address `addr`. Auto aligns `addr` to block
    #     boundary
    #     """
    #     base_addr = self._get_base_addr(addr)
    #     self.ram.write_bytes_many(base_addr, new_block)

    def read_block_mu(self, addr: UInt32, memory_unit: MemoryUnit) -> DataBlock:
        if isinstance(memory_unit, RAM32):
            base_addr = self._get_base_addr(addr)
            return self.ram.read_bytes_many(base_addr, self.block_size)

        cache = memory_unit
        new_block = cache.copy_block(addr)

        if new_block is not None:
            # cache hit
            return new_block

        # cache miss
        next_level_unit = cache.next_level
        new_block = self.read_block_mu(addr, next_level_unit)

        evicted = cache.insert(addr, new_block)

        if evicted is None:
            return new_block

        base_addr, evicted_block = evicted

        self.write_block_mu(base_addr, evicted_block, next_level_unit)

        return new_block

    def write_block_mu(
        self, addr: UInt32, new_block: DataBlock, memory_unit: MemoryUnit
    ) -> None:
        if isinstance(memory_unit, RAM32):
            base_addr = self._get_base_addr(addr)
            self.ram.write_bytes_many(base_addr, new_block)
            return None

        cache = memory_unit
        evicted = cache.insert(addr, new_block)

        if evicted is None:
            # no eviction
            return None

        # conflict eviction
        next_level_unit = cache.next_level
        base_addr, evicted_block = evicted
        self.write_block_mu(base_addr, evicted_block, next_level_unit)

        if cache.write_policy is WritePolicy.WRITE_THROUGH:
            self.write_block_mu(addr, new_block, next_level_unit)

        return None

    # -------------------------------------------------------------------------------- #
    # Functions to read and write bytes

    def read_byte_mu(self, addr: UInt32, memory_unit: MemoryUnit) -> UInt8:
        if isinstance(memory_unit, RAM32):
            return self.ram.read_byte(addr)

        cache = memory_unit
        byte = cache.read_byte(addr)

        if byte is not None:
            # cache hit
            return byte

        # cache miss
        next_level_cache = cache.next_level
        new_block = self.read_block_mu(addr, next_level_cache)
        evicted = cache.insert(addr, new_block)

        byte = cache.read_byte(addr)
        if byte is None:
            raise MemoryHierarchyError(f"[BUG] Read after refill must result in a hit")

        if evicted is not None:
            base_addr, evicted_block = evicted
            self.write_block_mu(base_addr, evicted_block, next_level_cache)

        return byte

    def write_byte_mu(self, addr: UInt32, byte: UInt8, memory_unit: MemoryUnit) -> None:
        if isinstance(memory_unit, RAM32):
            return self.ram.write_byte(addr, byte)

        cache = memory_unit
        hitmiss = cache.write_byte(addr, byte)
        next_level_cache = cache.next_level

        if hitmiss is WriteSignal.HIT:
            if cache.write_policy is WritePolicy.WRITE_THROUGH:
                self.write_byte_mu(addr, byte, next_level_cache)

        else:
            # hitmiss was a MISS
            if cache.write_policy is WritePolicy.WRITE_THROUGH:
                # write through  -  write-no-allocate policy
                self.write_byte_mu(addr, byte, next_level_cache)

            else:
                # write back  -  write-allocate policy
                new_block = self.read_block_mu(addr, next_level_cache)
                evicted = cache.insert(addr, new_block)

                hitmiss2 = cache.write_byte(addr, byte)
                if hitmiss2 is WriteSignal.MISS:
                    raise MemoryHierarchyError(
                        f"[BUG] Write after refill must result in a hit"
                    )

                if evicted is not None:
                    base_addr, evicted_block = evicted
                    self.write_block_mu(base_addr, evicted_block, next_level_cache)

        return None

    # -------------------------------------------------------------------------------- #
    # Functions to read and write halfwords

    def read_halfword_mu(self, addr: UInt32, memory_unit: MemoryUnit) -> UInt16:
        if isinstance(memory_unit, RAM32):
            return self.ram.read_halfword(addr)

        cache = memory_unit
        halfword = cache.read_halfword(addr)

        if halfword is not None:
            # cache hit
            return halfword

        # cache miss
        next_level_cache = cache.next_level
        new_block = self.read_block_mu(addr, next_level_cache)
        evicted = cache.insert(addr, new_block)

        halfword = cache.read_halfword(addr)
        if halfword is None:
            raise MemoryHierarchyError(f"[BUG] Read after refill must result in a hit")

        if evicted is not None:
            base_addr, evicted_block = evicted
            self.write_block_mu(base_addr, evicted_block, next_level_cache)

        return halfword

    def write_halfword_mu(
        self, addr: UInt32, halfword: UInt16, memory_unit: MemoryUnit
    ) -> None:
        if isinstance(memory_unit, RAM32):
            return self.ram.write_halfword(addr, halfword)

        cache = memory_unit
        hitmiss = cache.write_halfword(addr, halfword)
        next_level_cache = cache.next_level

        if hitmiss is WriteSignal.HIT:
            if cache.write_policy is WritePolicy.WRITE_THROUGH:
                self.write_halfword_mu(addr, halfword, next_level_cache)

        else:
            # hitmiss was a MISS
            if cache.write_policy is WritePolicy.WRITE_THROUGH:
                # write through  -  write-no-allocate policy
                self.write_halfword_mu(addr, halfword, next_level_cache)

            else:
                # write back  -  write-allocate policy
                new_block = self.read_block_mu(addr, next_level_cache)
                evicted = cache.insert(addr, new_block)

                hitmiss2 = cache.write_halfword(addr, halfword)
                if hitmiss2 is WriteSignal.MISS:
                    raise MemoryHierarchyError(
                        f"[BUG] Write after refill must result in a hit"
                    )

                if evicted is not None:
                    base_addr, evicted_block = evicted
                    self.write_block_mu(base_addr, evicted_block, next_level_cache)

        return None

    # -------------------------------------------------------------------------------- #
    # Functions to read and write words

    def read_word_mu(self, addr: UInt32, memory_unit: MemoryUnit) -> UInt32:
        if isinstance(memory_unit, RAM32):
            return self.ram.read_word(addr)

        cache = memory_unit
        word = cache.read_word(addr)

        if word is not None:
            # cache hit
            return word

        # cache miss
        next_level_cache = cache.next_level
        new_block = self.read_block_mu(addr, next_level_cache)
        evicted = cache.insert(addr, new_block)

        word = cache.read_word(addr)
        if word is None:
            raise MemoryHierarchyError(f"[BUG] Read after refill must result in a hit")

        if evicted is not None:
            base_addr, evicted_block = evicted
            self.write_block_mu(base_addr, evicted_block, next_level_cache)

        return word

    def write_word_mu(
        self, addr: UInt32, word: UInt32, memory_unit: MemoryUnit
    ) -> None:
        if isinstance(memory_unit, RAM32):
            return self.ram.write_word(addr, word)

        cache = memory_unit
        hitmiss = cache.write_word(addr, word)
        next_level_cache = cache.next_level

        if hitmiss is WriteSignal.HIT:
            if cache.write_policy is WritePolicy.WRITE_THROUGH:
                self.write_word_mu(addr, word, next_level_cache)

        else:
            # hitmiss was a MISS
            if cache.write_policy is WritePolicy.WRITE_THROUGH:
                # write through  -  write-no-allocate policy
                self.write_word_mu(addr, word, next_level_cache)

            else:
                # write back  -  write-allocate policy
                new_block = self.read_block_mu(addr, next_level_cache)
                evicted = cache.insert(addr, new_block)

                hitmiss2 = cache.write_word(addr, word)
                if hitmiss2 is WriteSignal.MISS:
                    raise MemoryHierarchyError(
                        f"[BUG] Write after refill must result in a hit"
                    )

                if evicted is not None:
                    base_addr, evicted_block = evicted
                    self.write_block_mu(base_addr, evicted_block, next_level_cache)

        return None

    def read_byte(self, addr: UInt32) -> UInt8:
        return self.read_byte_mu(addr, self.data_unit)

    def write_byte(self, addr: UInt32, byte: UInt8) -> None:
        return self.write_byte_mu(addr, byte, self.data_unit)

    def read_halfword(self, addr: UInt32) -> UInt16:
        return self.read_halfword_mu(addr, self.data_unit)

    def write_halfword(self, addr: UInt32, halfword: UInt16) -> None:
        return self.write_halfword_mu(addr, halfword, self.data_unit)

    def read_word(self, addr: UInt32) -> UInt32:
        return self.read_word_mu(addr, self.data_unit)

    def write_word(self, addr: UInt32, word: UInt32) -> None:
        return self.write_word_mu(addr, word, self.data_unit)

    def read_word_inst(self, addr: UInt32) -> UInt32:
        return self.read_word_mu(addr, self.inst_unit)
