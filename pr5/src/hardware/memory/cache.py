# 15 NOV DEADLINE

from enum import Enum, auto
from dataclasses import dataclass

from src.utils.bits import is_power_of_two


class CacheConfigError(Exception):
    def __init__(self, msg: str):
        self.message = msg
        super().__init__(msg)


class CacheType(Enum):
    """
    Cache types
    - `I1_CACHE` : 1st-level instruction cache
    - `L1_CACHE` : 1st-level data cache
    - `L2_CACHE` : 2nd-level data cache
    """

    I1_CACHE = auto()
    L1_CACHE = auto()
    L2_CACHE = auto()


class ReplacementPolicy(Enum):
    """
    Replacement Policies
    - `FIFO` : First in first out
    - `LRU` : Least recently used
    """

    FIFO = auto()
    LRU = auto()


@dataclass
class CacheConfig:
    """
    Cache configuration
    - `valid` : Is the cache present?
    - `latency` : Response latency for the cache, in clock-cycles
    - `cache_size` : Bytes of data stored in the cache
    - `block_size` : Bytes of data stored in a block
    - `assoc` : Number of blocks in a set
    - `policy` : Replacement policy (`FIFO` / `LRU`)
    """

    valid: bool
    latency: int
    cache_size: int
    block_size: int
    assoc: int
    policy: ReplacementPolicy


class Cache:
    def _validate(self, config: CacheConfig) -> None:
        """
        Verify the given configuration is valid:
        - Cache size must be a positive power of two
        - Block size must be a positive power of two
        - Association must be a positive power of two, between 1 and
          (cache size / block size), the number of blocks in the cache
        - Latency must be positive

        :param config: Cache configuration

        :return: `None`, if configuration is valid

        :raises CacheConfigError: If an of the above criteria are not satisfied
        """

        cache_size = config.cache_size
        block_size = config.block_size
        assoc = config.assoc
        latency = config.latency

        if cache_size <= 0:
            raise CacheConfigError(f"Cache size: ({cache_size}) must be positive")
        if not is_power_of_two(cache_size):
            raise CacheConfigError(f"Cache size: ({cache_size}) must be a power of two")

        if block_size <= 0:
            raise CacheConfigError(f"Block size: ({block_size}) must be positive")
        if not is_power_of_two(block_size):
            raise CacheConfigError(f"Block size: ({block_size}) must be a power of two")

        if assoc <= 0:
            raise CacheConfigError(f"Association: ({assoc}) must be positive")
        if not is_power_of_two(assoc):
            raise CacheConfigError(f"Association: ({assoc}) must be a power of two")

        if latency <= 0:
            raise CacheConfigError(f"Latency: ({latency}) must be positive")

        n_blocks = cache_size / block_size

        if not (1 <= assoc <= n_blocks):
            raise CacheConfigError(
                f"Association: ({assoc}) must be between 1 and \
                                   {n_blocks}, number of blocks in the cache"
            )

        return None

    def __init__(self, config: CacheConfig) -> None:
        self._validate(config)

        self.latency = config.latency
        self.cache_size = config.cache_size
        self.block_size = config.block_size
        self.assoc = config.assoc
        self.policy = config.policy
