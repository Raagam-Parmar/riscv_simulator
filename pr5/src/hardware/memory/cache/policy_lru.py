from typing import List

from src.hardware.memory.cache.policy_base import ReplacementAlgorithm


class PolicyLRU(ReplacementAlgorithm):
    def __init__(self, ways: int) -> None:
        self.ways = ways
        self.recency: List[int] = []
        # index 0 is least recently used

    def on_access(self, way: int) -> None:
        self.recency.remove(way)
        self.recency.append(way)

    def on_insert(self, way: int) -> None:
        self.recency.append(way)

    def on_evict(self) -> int:
        return self.recency.pop(0)
