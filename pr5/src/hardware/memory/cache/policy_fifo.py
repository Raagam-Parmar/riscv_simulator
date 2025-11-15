from typing import List

from src.hardware.memory.cache.policy_base import ReplacementAlgorithm


class PolicyFIFO(ReplacementAlgorithm):
    def __init__(self, ways: int) -> None:
        self.ways = ways
        self.queue: List[int] = []
        # index 0 is first inserted block

    def on_access(self, way: int) -> None:
        return None

    def on_insert(self, way: int) -> None:
        self.queue.append(way)

    def on_evict(self) -> int:
        return self.queue.pop(0)
