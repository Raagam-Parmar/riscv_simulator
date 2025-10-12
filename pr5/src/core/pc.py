class InvalidStartPC(Exception):
    def __init__(self, pc: int):
        self.message = f"Program counter can not be negative."
        super().__init__(self.message)


class ProgramCounter:
    def __init__(self, start: int) -> None:
        if start < 0:
            raise InvalidStartPC(start)
        self.pointer: int = start

    def fetch(self) -> int:
        return self.pointer

    def set_next(self, address: int) -> None:
        self.pointer = address
