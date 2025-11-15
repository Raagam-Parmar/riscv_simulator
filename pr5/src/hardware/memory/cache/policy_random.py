from random import randint

from src.hardware.memory.cache.policy_base import ReplacementAlgorithm


class PolicyRandom(ReplacementAlgorithm):
    def __init__(self, ways: int) -> None:
        self.ways = ways

    def on_access(self, way: int) -> None:
        return None

    def on_insert(self, way: int) -> None:
        return None

    def on_evict(self) -> int:
        return randint(0, self.ways - 1)
