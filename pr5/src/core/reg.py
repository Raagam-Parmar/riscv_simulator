class InvalidSize(Exception):
    def __init__(self, size: int):
        self.message = f"Size for register file {size} must be positive."
        super().__init__(self.message)


class RegisterOutOfBounds(Exception):
    def __init__(self, register: int, size: int):
        self.message = f"Can not write to out-of-bounds register {register} on register file of size {size}."
        super().__init__(self.message)


class Register:
    def __init__(self) -> None:
        self.value: int = 0

    def read(self) -> int:
        return self.value

    def write(self, value: int) -> None:
        self.value = value


class RegisterFile:
    def __init__(self, size: int, zero_reg: bool) -> None:
        if size <= 0:
            raise InvalidSize(size)

        self.registers = [Register() for _ in range(size)]
        self.size = size
        self.zreg = zero_reg

    def write(self, register: int, value: int) -> None:
        if not (0 <= register < self.size):
            raise RegisterOutOfBounds(register, self.size)

        if self.zreg and (register == 0):
            return

        self.registers[register].write(value)

    def read(self, register: int) -> int:
        if not (0 <= register < self.size):
            raise RegisterOutOfBounds(register, self.size)

        if self.zreg and (register == 0):
            return 0

        return self.registers[register].read()
