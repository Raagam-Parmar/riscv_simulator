from typing import Tuple

from src.hardware.memory.cache.cache import (
    CacheConfig,
    Cache32,
    DataBlock,
    WritePolicy,
    WriteSignal,
    CacheType,
)
from src.utils.cint import *
from src.hardware.memory.ram32 import RAM32, RAMConfig
from src.utils.logger import PR5Logger
from src.utils.stats import Statistics


class MemoryHierarchyError(Exception):
    def __init__(self, msg: str):
        self.message = msg
        super().__init__(msg)


class MemoryHierarchy:
    def __init__(
        self,
        l1i_config: CacheConfig,
        l1d_config: CacheConfig,
        l2_config: CacheConfig,
        ram_config: RAMConfig,
        logger: PR5Logger,
        stats: Statistics
    ) -> None:
        # TODO Error checks

        self.l1d = Cache32(l1d_config, logger)
        self.l1i = Cache32(l1i_config, logger)
        self.l2 = Cache32(l2_config, logger)
        self.ram = RAM32(ram_config, logger, stats)
        self.block_size = self.l1d.block_size

        if (
            self.l1d.block_size != self.l1i.block_size
            or (self.l1d.block_size != self.l2.block_size)
            or (self.l1i.block_size != self.l2.block_size)
        ):
            raise MemoryHierarchyError(f"Caches must have same block size")

    def _get_base_addr(self, addr: UInt32) -> UInt32:
        """
        Return the base address in any block given `addr`
        """
        return addr & (~(UInt32(self.block_size - 1)))

    def read_block_ram(self, addr: UInt32) -> Tuple[DataBlock, int]:
        """
        Fetch block containing `addr` from the RAM. Auto aligns `addr` to block boundary
        """
        late = self.ram.latency
        base_addr = self._get_base_addr(addr)
        return self.ram.read_bytes_many(base_addr, self.block_size), late

    def write_block_ram(self, addr: UInt32, new_block: DataBlock) -> int:
        """
        Write `block` into RAM, with base address `addr`. Auto aligns `addr` to block
        boundary
        """
        late = self.ram.latency
        base_addr = self._get_base_addr(addr)
        self.ram.write_bytes_many(base_addr, new_block)
        return late

    def read_block_l2(self, addr: UInt32) -> Tuple[DataBlock, int]:
        """
        Fetch block containing `addr` from `L2`. Request load from RAM if not present.
        """
        new_block = self.l2.copy_block(addr)
        late = self.l2.latency

        if new_block is not None:
            # cache hit
            return new_block, late

        # cache miss
        new_block, late_ram = self.read_block_ram(addr)
        evicted = self.l2.insert(addr, new_block)
        late_evict = self.l2.latency

        late += late_ram
        late += late_evict

        if evicted is None:
            return new_block, late

        base_addr, evicted_block = evicted
        late_ram2 = self.write_block_ram(base_addr, evicted_block)

        late += late_ram2

        return new_block, late

    def write_block_l2(self, addr: UInt32, new_block: DataBlock) -> int:
        """
        Write `new_block` containing `addr` to L2. In case of eviction, write the
        evicted block to RAM
        """

        evicted = self.l2.insert(addr, new_block)
        late = self.l2.latency

        if evicted is None:
            # no eviction
            return late

        # conflict eviction
        base_addr, evicted_block = evicted
        late_ram = self.write_block_ram(base_addr, evicted_block)
        late += late_ram

        if self.l2.write_policy is WritePolicy.WRITE_THROUGH:
            late_ram_write = self.write_block_ram(addr, new_block)
            late += late_ram_write

        return late

    # -------------------------------------------------------------------------------- #
    # Functions to read and write bytes

    def read_byte_l1(self, addr: UInt32, cache_type: CacheType) -> Tuple[UInt8, int]:
        """
        Read byte at `addr` in L1 cache. Request load from lower levels if not present.
        """

        match cache_type:
            case CacheType.L1I:
                cache = self.l1i
            case CacheType.L1D:
                cache = self.l1d
            case CacheType.L2:
                raise MemoryHierarchyError(f"[BUG] Can not read directly from L2 Cache")

        byte = cache.read_byte(addr)
        late = cache.latency

        if byte is not None:
            # cache hit
            return byte, late

        # cache miss
        new_block, late_miss = self.read_block_l2(addr)
        evicted = cache.insert(addr, new_block)
        late_evict = cache.latency

        late += late_miss
        late += late_evict

        byte = cache.read_byte(addr)
        if byte is None:
            raise MemoryHierarchyError(f"[BUG] Read after refill must result in a hit")

        if evicted is not None:
            base_addr, evicted_block = evicted
            late_write = self.write_block_l2(base_addr, evicted_block)
            late += late_write

        return byte, late

    def write_byte_cache(self, addr: UInt32, byte: UInt8, cache_type: CacheType) -> int:
        """
        Write `byte` at `addr` in L1D, L1I or L2 Cache. Request load from lower levels if not
        present.
        """
        match cache_type:
            case CacheType.L1I:
                cache = self.l1i
            case CacheType.L1D:
                cache = self.l1d
            case CacheType.L2:
                cache = self.l2

        hitmiss = cache.write_byte(addr, byte)
        late = cache.latency

        match hitmiss:
            case WriteSignal.HIT:
                if cache.write_policy is WritePolicy.WRITE_THROUGH:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            late += self.write_byte_cache(addr, byte, CacheType.L2)
                        case CacheType.L2:
                            self.ram.write_byte(addr, byte)
                            late += self.ram.latency

            case WriteSignal.MISS:
                if cache.write_policy is WritePolicy.WRITE_THROUGH:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            late += self.write_byte_cache(addr, byte, CacheType.L2)
                        case CacheType.L2:
                            self.ram.write_byte(addr, byte)
                            late += self.ram.latency

                else:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            new_block, late_lower = self.read_block_l2(addr)
                        case CacheType.L2:
                            new_block, late_lower = self.read_block_ram(addr)

                    evicted = cache.insert(addr, new_block)
                    late += late_lower

                    hitmiss2 = cache.write_byte(addr, byte)
                    if hitmiss2 is WriteSignal.MISS:
                        raise MemoryHierarchyError(
                            f"[BUG] Write after refill must result in a hit"
                        )

                    if evicted is not None:
                        base_addr, evicted_block = evicted
                        match cache_type:
                            case CacheType.L1I | CacheType.L1D:
                                late += self.write_block_l2(base_addr, evicted_block)
                            case CacheType.L2:
                                late += self.write_block_ram(base_addr, evicted_block)

        return late

    # -------------------------------------------------------------------------------- #
    # Functions to read and write halfwords

    def read_halfword_l1(
        self, addr: UInt32, cache_type: CacheType
    ) -> Tuple[UInt16, int]:
        """
        Read halfword at `addr` in L1 cache. Request load from lower levels if not present.
        """

        match cache_type:
            case CacheType.L1I:
                cache = self.l1i
            case CacheType.L1D:
                cache = self.l1d
            case CacheType.L2:
                raise MemoryHierarchyError(f"[BUG] Can not read directly from L2 Cache")

        halfword = cache.read_halfword(addr)
        late = cache.latency

        if halfword is not None:
            # cache hit
            return halfword, late

        # cache miss
        new_block, late_miss = self.read_block_l2(addr)
        evicted = cache.insert(addr, new_block)
        late_evict = cache.latency

        late += late_miss
        late += late_evict

        halfword = cache.read_halfword(addr)
        if halfword is None:
            raise MemoryHierarchyError(f"[BUG] Read after refill must result in a hit")

        if evicted is not None:
            base_addr, evicted_block = evicted
            late_write = self.write_block_l2(base_addr, evicted_block)
            late += late_write

        return halfword, late

    def write_halfword_cache(
        self, addr: UInt32, halfword: UInt16, cache_type: CacheType
    ) -> int:
        """
        Write `halfword` at `addr` in L1D, L1I or L2 Cache. Request load from lower levels if not
        present.
        """
        match cache_type:
            case CacheType.L1I:
                cache = self.l1i
            case CacheType.L1D:
                cache = self.l1d
            case CacheType.L2:
                cache = self.l2

        hitmiss = cache.write_halfword(addr, halfword)
        late = cache.latency

        match hitmiss:
            case WriteSignal.HIT:
                if cache.write_policy is WritePolicy.WRITE_THROUGH:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            late += self.write_halfword_cache(
                                addr, halfword, CacheType.L2
                            )
                        case CacheType.L2:
                            self.ram.write_halfword(addr, halfword)
                            late += self.ram.latency

            case WriteSignal.MISS:
                if cache.write_policy is WritePolicy.WRITE_THROUGH:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            late += self.write_halfword_cache(
                                addr, halfword, CacheType.L2
                            )
                        case CacheType.L2:
                            self.ram.write_halfword(addr, halfword)
                            late += self.ram.latency

                else:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            new_block, late_lower = self.read_block_l2(addr)
                        case CacheType.L2:
                            new_block, late_lower = self.read_block_ram(addr)

                    evicted = cache.insert(addr, new_block)
                    late += late_lower

                    hitmiss2 = cache.write_halfword(addr, halfword)
                    if hitmiss2 is WriteSignal.MISS:
                        raise MemoryHierarchyError(
                            f"[BUG] Write after refill must result in a hit"
                        )

                    if evicted is not None:
                        base_addr, evicted_block = evicted
                        match cache_type:
                            case CacheType.L1I | CacheType.L1D:
                                late += self.write_block_l2(base_addr, evicted_block)
                            case CacheType.L2:
                                late += self.write_block_ram(base_addr, evicted_block)

        return late

    # -------------------------------------------------------------------------------- #
    # Functions to read and write words

    def read_word_l1(self, addr: UInt32, cache_type: CacheType) -> Tuple[UInt32, int]:
        """
        Read word at `addr` in L1 cache. Request load from lower levels if not present.
        """

        match cache_type:
            case CacheType.L1I:
                cache = self.l1i
            case CacheType.L1D:
                cache = self.l1d
            case CacheType.L2:
                raise MemoryHierarchyError(f"[BUG] Can not read directly from L2 Cache")

        word = cache.read_word(addr)
        late = cache.latency

        if word is not None:
            # cache hit
            return word, late

        # cache miss
        new_block, late_miss = self.read_block_l2(addr)
        evicted = cache.insert(addr, new_block)
        late_evict = cache.latency

        late += late_miss
        late += late_evict

        word = cache.read_word(addr)
        if word is None:
            raise MemoryHierarchyError(f"[BUG] Read after refill must result in a hit")

        if evicted is not None:
            base_addr, evicted_block = evicted
            late_write = self.write_block_l2(base_addr, evicted_block)
            late += late_write

        return word, late

    def write_word_cache(
        self, addr: UInt32, word: UInt32, cache_type: CacheType
    ) -> int:
        """
        Write `word` at `addr` in L1D, L1I or L2 Cache. Request load from lower levels if not
        present.
        """
        match cache_type:
            case CacheType.L1I:
                cache = self.l1i
            case CacheType.L1D:
                cache = self.l1d
            case CacheType.L2:
                cache = self.l2

        hitmiss = cache.write_word(addr, word)
        late = cache.latency

        match hitmiss:
            case WriteSignal.HIT:
                if cache.write_policy is WritePolicy.WRITE_THROUGH:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            late += self.write_word_cache(addr, word, CacheType.L2)
                        case CacheType.L2:
                            self.ram.write_word(addr, word)
                            late += self.ram.latency

            case WriteSignal.MISS:
                if cache.write_policy is WritePolicy.WRITE_THROUGH:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            late += self.write_word_cache(addr, word, CacheType.L2)
                        case CacheType.L2:
                            self.ram.write_word(addr, word)
                            late += self.ram.latency

                else:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            new_block, late_lower = self.read_block_l2(addr)
                        case CacheType.L2:
                            new_block, late_lower = self.read_block_ram(addr)

                    evicted = cache.insert(addr, new_block)
                    late += late_lower

                    hitmiss2 = cache.write_word(addr, word)
                    if hitmiss2 is WriteSignal.MISS:
                        raise MemoryHierarchyError(
                            f"[BUG] Write after refill must result in a hit"
                        )

                    if evicted is not None:
                        base_addr, evicted_block = evicted
                        match cache_type:
                            case CacheType.L1I | CacheType.L1D:
                                late += self.write_block_l2(base_addr, evicted_block)
                            case CacheType.L2:
                                late += self.write_block_ram(base_addr, evicted_block)

        return late

    def read_byte(self, addr: UInt32) -> Tuple[UInt8, int]:
        return self.read_byte_l1(addr, CacheType.L1D)

    def write_byte(self, addr: UInt32, byte: UInt8) -> int:
        return self.write_byte_cache(addr, byte, CacheType.L1D)

    def read_halfword(self, addr: UInt32) -> Tuple[UInt16, int]:
        return self.read_halfword_l1(addr, CacheType.L1D)

    def write_halfword(self, addr: UInt32, halfword: UInt16) -> int:
        return self.write_halfword_cache(addr, halfword, CacheType.L1D)

    def read_word_inst(self, addr: UInt32) -> Tuple[UInt32, int]:
        return self.read_word_l1(addr, CacheType.L1I)

    def read_word(self, addr: UInt32) -> Tuple[UInt32, int]:
        return self.read_word_l1(addr, CacheType.L1D)

    def write_word(self, addr: UInt32, word: UInt32) -> int:
        return self.write_word_cache(addr, word, CacheType.L1D)
