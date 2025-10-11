from dataclasses import dataclass

from enums import *
from verify import *


@dataclass(frozen=True)
class Reg:
    op: Reg_ops
    rd: int
    rs1: int
    rs2: int

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_reg(self.rs2)

    def __str__(self):
        # op    rd, rs1, rs2
        return f"{self.op} \tx{self.rd}, x{self.rs1}, x{self.rs2}"


@dataclass(frozen=True)
class Imm:
    op: Imm_ops
    rd: int
    rs1: int
    imm: int
    # encoded as -2048 <= imm <= 2047  (2**11 = 2048)
    # actual same as encoded

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_imm12(self.imm)

    def __str__(self):
        # op    rd, rs1, imm
        return f"{self.op} \tx{self.rd}, x{self.rs1}, {self.imm}"


@dataclass(frozen=True)
class Load:
    op: Load_ops
    rd: int
    rs1: int
    imm: int
    # encoded as -2048 <= imm <= 2047  (2**11 = 2048)
    # actual same as encoded

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_imm12(self.imm)

    def __str__(self):
        # op    rd, imm(rs1)
        return f"{self.op} \tx{self.rd}, {self.imm}(x{self.rs1})"


@dataclass(frozen=True)
class Store:
    op: Store_ops
    rs1: int
    rs2: int
    imm: int
    # encoded as -2048 <= imm <= 2047   (2**11 = 2048)
    # actual same as encoded

    def __post_init__(self):
        verify_reg(self.rs1)
        verify_reg(self.rs2)
        verify_imm12(self.imm)

    def __str__(self):
        # op    rs2, imm(rs1)
        return f"{self.op} \tx{self.rs2}, {self.imm}(x{self.rs1})"


@dataclass(frozen=True)
class Branch:
    op: Branch_ops
    rs1: int
    rs2: int
    # encoded as -2048 <= imm <= 2047   (2**11 = 2048)
    # actual  as -4096 <= imm <= 4095   (2**12 = 4096) (evens only)
    imm: int

    def __post_init__(self):
        verify_reg(self.rs1)
        verify_reg(self.rs2)
        verify_2b_align(self.imm)
        verify_imm12(self.imm // 2)

    def __str__(self):
        # op    rs1, rs2, imm
        return f"{self.op} \tx{self.rs1}, x{self.rs2}, {hex(self.imm)}"


@dataclass(frozen=True)
class Upper:
    op: Upper_ops
    rd: int
    imm: int
    # encoded as 0 <= imm <= 1048575   (2**20 = 1048576)
    # actual same as encoded [TODO TEST]

    def __post_init__(self):
        verify_reg(self.rd)
        verify_uimm20(self.imm)

    def __str__(self):
        # op    rd, imm
        return f"{self.op} \tx{self.rd}, {hex(self.imm)}"


@dataclass(frozen=True)
class Jump:
    op: Jump_ops
    rd: int
    imm: int
    # encoded as -524288 <= imm <= 524287   (2**19 = 524288)
    # actual  as -1048575 <= imm <= 1048576 (2**20 = 1048576) (evens only)

    def __post_init__(self):
        verify_reg(self.rd)
        verify_imm20(self.imm // 2)
        verify_2b_align(self.imm)

    def __str__(self):
        # op    rd, imm
        return f"{self.op} \tx{self.rd}, {hex(self.imm)}"


@dataclass(frozen=True)
class Misc_mem:
    op: Misc_mem_ops
    rd: int
    rs1: int
    succ: int
    pred: int
    fm: int

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_uimm4(self.succ)
        verify_uimm4(self.pred)
        verify_uimm4(self.fm)

    def __str__(self):
        if self.op != Misc_mem_ops.FENCE:
            return f"{self.op}"

        pred = ""
        succ = ""

        for i in reversed(range(4)):
            if (self.pred >> i) & 0b1:
                if i == 3:
                    pred += "i"
                if i == 2:
                    pred += "o"
                if i == 1:
                    pred += "r"
                if i == 0:
                    pred += "w"

            if (self.succ >> i) & 0b1:
                if i == 3:
                    succ += "i"
                if i == 2:
                    succ += "o"
                if i == 1:
                    succ += "r"
                if i == 0:
                    succ += "w"

        return f"{self.op} {pred}, {succ}"


@dataclass(frozen=True)
class Atomic:
    op: Atomic_ops
    rd: int
    rs1: int
    rs2: int
    aq: int
    rl: int

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_reg(self.rs2)
        verify_bit(self.aq)
        verify_bit(self.rl)

    def __str__(self):
        show = f"{self.op}"

        if self.aq and not self.rl:
            show += ".aq"

        elif self.rl and not self.aq:
            show += ".rl"

        elif self.aq and self.rl:
            show += ".aqrl"

        return f"{show} \tx{self.rd}, x{self.rs2}, (x{self.rs1})"


@dataclass(frozen=True)
class System:
    op: System_ops

    def __str__(self):
        # op
        return f"{self.op}"


@dataclass(frozen=True)
class Zicsr:
    op: Zicsr_ops
    rd: int
    rs1: int
    csr: int

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_uimm12(self.csr)

    def __str__(self):
        # op    rd, csr, rs1
        return f"{self.op} \tx{self.rd}, 0x{self.csr:03x}, x{self.rs1}"


@dataclass(frozen=True)
class Zicsr_Imm:
    op: Zicsr_imm_ops
    rd: int
    csr: int
    uimm: int
    # encoded as 0 <= uimm <= 32   (2**5 = 32)
    # actual same as encoded

    def __post_init__(self):
        verify_reg(self.rd)
        verify_uimm5(self.uimm)
        verify_uimm12(self.csr)

    def __str__(self):
        # op    rd, csr, uimm
        return f"{self.op} \tx{self.rd}, 0x{self.csr:03x}, {self.uimm}"
