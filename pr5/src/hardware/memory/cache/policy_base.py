from abc import ABC, abstractmethod


class ReplacementAlgorithm(ABC):
    @abstractmethod
    def __init__(self, ways: int) -> None:
        """Initialise metadata for replacement policy"""
        pass

    @abstractmethod
    def on_access(self, way: int) -> None:
        """Update metadata on cache hit"""
        pass

    @abstractmethod
    def on_insert(self, way: int) -> None:
        """Update matadata on cache insert"""
        pass

    @abstractmethod
    def on_evict(self) -> int:
        """Update metadata on eviction, return index of way to be evicted"""
        pass
