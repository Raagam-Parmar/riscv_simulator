class Field:
    def __init__(self, hi: int, lo: int):
        self.hi = hi
        self.lo = lo

        w = hi - lo + 1
        self.width: int = w
        self.mask: int = (1 << w) - 1

    def extract(self, word: int) -> int:
        return (word >> self.lo) & self.mask

    def __repr__(self):
        return f"Field range [{self.hi}...{self.lo}]"
