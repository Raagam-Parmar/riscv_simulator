# 15 NOV DEADLINE

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional
from math import log2

from src.utils.bits import is_power_of_two
from src.utils.cint import *
from src.utils.field import Field
from src.hardware.memory.cache.policy_random import PolicyRandom
from src.hardware.memory.cache.policy_lru import PolicyLRU
from src.hardware.memory.cache.policy_fifo import PolicyFIFO


class AddressMisaligned(Exception):
    """
    Requested to read from or write to an address which is not aligned to given boundary
    """

    def __init__(self, address: UInt32, align: int):
        super().__init__(f"Address {address} is not {align}-byte aligned")


class CacheConfigError(Exception):
    def __init__(self, msg: str):
        self.message = msg
        super().__init__(msg)


class CacheType(Enum):
    I1_CACHE = auto()
    L1_CACHE = auto()
    L2_CACHE = auto()


class ReplacementPolicy(Enum):
    RANDOM = auto()
    FIFO = auto()
    LRU = auto()


class WritePolicy(Enum):
    WRITE_BACK = auto()
    WRITE_THROUGH = auto()


class AllocatePolicy(Enum):
    WRITE_ALLOC = auto()
    WRITE_NO_ALLOC = auto()


class WriteSignal(Enum):
    HIT = auto()
    MISS = auto()


@dataclass(frozen=True)
class CacheConfig:
    """
    Cache configuration
    - `valid` : Is the cache present?
    - `latency` : Response latency for the cache, in clock-cycles
    - `cache_size` : Bytes of data stored in the cache
    - `block_size` : Bytes of data stored in one block
    - `ways` : Number of ways (blocks) in a set
    - `repl_policy` : Replacement policy
    - `write_policy` : Write policy
    """

    valid: bool
    latency: int
    cache_size: int
    block_size: int
    ways: int
    repl_policy: ReplacementPolicy
    write_policy: WritePolicy


DataBlock = List[UInt8]


@dataclass
class CacheBlock:
    valid: bool
    tag: int
    data: DataBlock


@dataclass
class CacheSet:
    ways: int
    repl_policy: ReplacementPolicy

    def __post_init__(self) -> None:
        self.blocks: List[CacheBlock] = []

        match self.repl_policy:
            case ReplacementPolicy.RANDOM:
                self._policy_algo = PolicyRandom(self.ways)
            case ReplacementPolicy.LRU:
                self._policy_algo = PolicyLRU(self.ways)
            case ReplacementPolicy.FIFO:
                self._policy_algo = PolicyFIFO(self.ways)


class Cache32:
    def _validate(self, config: CacheConfig) -> None:
        """
        Verify the given configuration is valid:
        - Cache size must be a positive power of two
        - Block size must be a positive power of two
        - Block size must be at least word size (4)
        - Block size must be at most cache size
        - Ways/Association must be a positive power of two, between 1 and
          (cache size / block size), the number of blocks in the cache
        - Latency must be positive

        :raises CacheConfigError: If an of the above criteria are not satisfied
        """

        cache_size = config.cache_size
        block_size = config.block_size
        ways = config.ways
        latency = config.latency

        if cache_size <= 0:
            raise CacheConfigError(f"Cache size: ({cache_size}) must be positive")
        if not is_power_of_two(cache_size):
            raise CacheConfigError(f"Cache size: ({cache_size}) must be a power of two")

        if block_size <= 0:
            raise CacheConfigError(f"Block size: ({block_size}) must be positive")
        if not is_power_of_two(block_size):
            raise CacheConfigError(f"Block size: ({block_size}) must be a power of two")

        if block_size < 4:
            raise CacheConfigError(
                f"Bloc size: ({block_size}) must be at least word size (4)"
            )

        if block_size > cache_size:
            raise CacheConfigError(
                f"Block size: ({block_size}) can not be more than cache size ({cache_size})"
            )

        if ways <= 0:
            raise CacheConfigError(f"Association: ({ways}) must be positive")
        if not is_power_of_two(ways):
            raise CacheConfigError(f"Association: ({ways}) must be a power of two")

        if latency <= 0:
            raise CacheConfigError(f"Latency: ({latency}) must be positive")

        n_blocks = cache_size // block_size

        if not (1 <= ways <= n_blocks):
            raise CacheConfigError(
                f"Association: ({ways}) must be between 1 and n_blocks ({n_blocks})"
            )

        return None

    def _get_set_idx(self, addr: UInt32) -> int:
        """Extract set index (in cache) from 32-bit address"""
        return self.set_idx_field.extract(addr.unsigned())

    def _get_tag(self, addr: UInt32) -> int:
        """Extract tag from 32-bit address"""
        return self.tag_field.extract(addr.unsigned())

    def _get_byte_idx(self, addr: UInt32) -> int:
        """Extract byte index (in word) from 32-bit address"""
        return self.byte_idx_field.extract(addr.unsigned())

    def __init__(self, config: CacheConfig) -> None:
        self._validate(config)

        self.latency = config.latency

        self.cache_size = config.cache_size
        self.block_size = config.block_size
        self.ways = config.ways
        self.n_blocks = self.cache_size // self.block_size
        self.n_sets = self.n_blocks // self.ways

        byte_field_width = int(log2(self.block_size))
        byte_field_hi = byte_field_width - 1
        self.byte_idx_field = Field(byte_field_hi, 0)

        set_field_width = int(log2(self.n_sets))
        set_field_lo = byte_field_hi + 1
        set_field_hi = set_field_lo + set_field_width - 1
        self.set_idx_field = Field(set_field_hi, set_field_lo)

        tag_field_lo = set_field_hi + 1
        tag_field_hi = 31
        self.tag_field = Field(tag_field_hi, tag_field_lo)

        self.repl_policy = config.repl_policy

        match self.repl_policy:
            case ReplacementPolicy.RANDOM:
                self.policy_algo = PolicyRandom(self.ways)
            case ReplacementPolicy.LRU:
                self.policy_algo = PolicyLRU(self.ways)
            case ReplacementPolicy.FIFO:
                self.policy_algo = PolicyFIFO(self.ways)

        self.write_policy = config.write_policy

        self.sets = [
            CacheSet(repl_policy=self.repl_policy, ways=self.ways)
            for _ in range(self.n_sets)
        ]

    def read_byte(self, addr: UInt32) -> Optional[UInt8]:
        """
        Return the byte at `addr` if present, otherwise return `None`
        """

        byte_idx = self._get_byte_idx(addr)
        set_idx = self._get_set_idx(addr)
        tag = self._get_tag(addr)

        for block in self.sets[set_idx].blocks:
            if block.valid and block.tag == tag:
                return block.data[byte_idx]

        return None

    def read_halfword(self, addr: UInt32) -> Optional[UInt16]:
        """
        Return the halfword at `addr` if present, otherwise return `None`.
        """

        byte_idx = self._get_byte_idx(addr)
        set_idx = self._get_set_idx(addr)
        tag = self._get_tag(addr)

        for block in self.sets[set_idx].blocks:
            if block.valid and block.tag == tag:
                halfword = UInt16(0)

                for i in range(2):
                    byte = block.data[byte_idx + i]
                    byte = uint16(byte)
                    halfword = halfword | byte << (i * 8)

                return halfword

        return None

    def read_word(self, addr: UInt32) -> Optional[UInt32]:
        """
        Return the word at `addr` if present, otherwise return `None`.
        """

        byte_idx = self._get_byte_idx(addr)
        set_idx = self._get_set_idx(addr)
        tag = self._get_tag(addr)

        for block in self.sets[set_idx].blocks:
            if block.valid and block.tag == tag:
                word = UInt32(0)

                for i in range(4):
                    byte = block.data[byte_idx + i]
                    byte = uint32(byte)
                    word = word | byte << (i * 8)

                return word

        return None

    def write_byte(self, addr: UInt32, byte: UInt8) -> WriteSignal:
        """
        Write the byte at `addr` if present and return `HIT`, otherwise return `MISS`.
        """

        byte_idx = self._get_byte_idx(addr)
        set_idx = self._get_set_idx(addr)
        tag = self._get_tag(addr)

        for block in self.sets[set_idx].blocks:
            if block.valid and block.tag == tag:
                block.data[byte_idx] = byte
                return WriteSignal.HIT

        return WriteSignal.MISS

    def write_halfword(self, addr: UInt32, halfword: UInt16) -> WriteSignal:
        """
        Write the halfword at `addr` if present and return `HIT`, otherwise return `MISS`
        """

        byte_idx = self._get_byte_idx(addr)
        set_idx = self._get_set_idx(addr)
        tag = self._get_tag(addr)

        for block in self.sets[set_idx].blocks:
            if block.valid and block.tag == tag:
                for i in range(2):
                    byte = halfword >> (i * 8)
                    block.data[byte_idx + i] = uint8(byte)

                return WriteSignal.HIT

        return WriteSignal.MISS

    def write_word(self, addr: UInt32, word: UInt32) -> WriteSignal:
        """
        Write the word at `addr` if present and return `HIT`, otherwise return `MISS`
        """

        byte_idx = self._get_byte_idx(addr)
        set_idx = self._get_set_idx(addr)
        tag = self._get_tag(addr)

        for block in self.sets[set_idx].blocks:
            if block.valid and block.tag == tag:
                for i in range(4):
                    byte = word >> (i * 8)
                    block.data[byte_idx + i] = uint8(byte)

                return WriteSignal.HIT

        return WriteSignal.MISS

    def insert(self, addr: UInt32, new_block: DataBlock) -> Optional[DataBlock]:
        """
        Insert `block` into cache, return the possibly evicted block
        """

        tag = self._get_tag(addr)
        set_idx = self._get_set_idx(addr)

        blocks = self.sets[set_idx].blocks

        for way, block in enumerate(blocks):
            if not block.valid:
                blocks[way].valid = True
                blocks[way].tag = tag
                blocks[way].data = new_block
                return None

        evict_way = self.policy_algo.on_evict()
        evicted_block = blocks[evict_way].data

        blocks[evict_way].valid = True
        blocks[evict_way].tag = tag
        blocks[evict_way].data = new_block

        return evicted_block
