from cache.cache import (
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


class MemoryHierarchyError(Exception):
    def __init__(self, msg: str):
        self.message = msg
        super().__init__(msg)


class MemoryHierarchy:
    def __init__(
        self,
        l1d_config: CacheConfig,
        l1i_config: CacheConfig,
        l2_config: CacheConfig,
        ram_config: RAMConfig,
        logger: PR5Logger,
    ) -> None:
        # TODO Error checks

        self.l1d = Cache32(l1d_config, logger)
        self.l1i = Cache32(l1i_config, logger)
        self.l2 = Cache32(l2_config, logger)
        self.ram = RAM32(ram_config, logger)
        self.block_size = self.l1d.block_size

    def _get_base_addr(self, addr: UInt32) -> UInt32:
        """
        Return the base address in any block given `addr`
        """
        return addr & (~(UInt32(self.block_size - 1)))

    def read_block_ram(self, addr: UInt32) -> DataBlock:
        """
        Fetch block containing `addr` from the RAM. Auto aligns `addr` to block boundary
        """
        base_addr = self._get_base_addr(addr)
        return self.ram.read_bytes_many(base_addr, self.block_size)

    def write_block_ram(self, addr: UInt32, new_block: DataBlock) -> None:
        """
        Write `block` into RAM, with base address `addr`. Auto aligns `addr` to block
        boundary
        """
        base_addr = self._get_base_addr(addr)
        self.ram.write_bytes_many(base_addr, new_block)

    def read_block_l2(self, addr: UInt32) -> DataBlock:
        """
        Fetch block containing `addr` from `L2`. Request load from RAM if not present.
        """
        new_block = self.l2.copy_block(addr)

        if new_block is not None:
            # cache hit
            return new_block

        # cache miss
        new_block = self.read_block_ram(addr)
        evicted = self.l2.insert(addr, new_block)

        if evicted is None:
            return new_block

        base_addr, evicted_block = evicted
        self.write_block_ram(base_addr, evicted_block)

        return new_block

    def write_block_l2(self, addr: UInt32, new_block: DataBlock) -> None:
        """
        Write `new_block` containing `addr` to L2. In case of eviction, write the
        evicted block to RAM
        """

        evicted = self.l2.insert(addr, new_block)

        if evicted is None:
            # no eviction
            return None

        # conflict eviction
        base_addr, evicted_block = evicted
        self.write_block_ram(base_addr, evicted_block)

        if self.l2.write_policy is WritePolicy.WRITE_THROUGH:
            self.write_block_ram(addr, new_block)

        return None

    def read_byte_l1(self, addr: UInt32, cache_type: CacheType) -> UInt8:
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

        if byte is not None:
            # cache hit
            return byte

        # cache miss
        new_block = self.read_block_l2(addr)
        evicted = cache.insert(addr, new_block)

        byte = cache.read_byte(addr)

        if byte is None:
            raise MemoryHierarchyError(f"[BUG] Read after refill must result in a hit")

        if evicted is not None:
            base_addr, evicted_block = evicted
            self.write_block_l2(base_addr, evicted_block)

        return byte

    def write_byte(self, addr: UInt32, byte: UInt8, cache_type: CacheType) -> None:
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

        match hitmiss:
            case WriteSignal.HIT:
                if cache.write_policy is WritePolicy.WRITE_THROUGH:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            self.write_byte(addr, byte, CacheType.L2)
                        case CacheType.L2:
                            self.ram.write_byte(addr, byte)

            case WriteSignal.MISS:
                if cache.write_policy is WritePolicy.WRITE_THROUGH:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            self.write_byte(addr, byte, CacheType.L2)
                        case CacheType.L2:
                            self.ram.write_byte(addr, byte)

                else:
                    match cache_type:
                        case CacheType.L1I | CacheType.L1D:
                            new_block = self.read_block_l2(addr)
                        case CacheType.L2:
                            new_block = self.read_block_ram(addr)

                    evicted = cache.insert(addr, new_block)

                    hitmiss2 = cache.write_byte(addr, byte)

                    if hitmiss2 is WriteSignal.MISS:
                        raise MemoryHierarchyError(
                            f"[BUG] Write after refill must result in a hit"
                        )

                    if evicted is not None:
                        base_addr, evicted_block = evicted
                        match cache_type:
                            case CacheType.L1I | CacheType.L1D:
                                self.write_block_l2(base_addr, evicted_block)
                            case CacheType.L2:
                                self.write_block_ram(base_addr, evicted_block)
