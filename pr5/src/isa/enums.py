# RISC-V Unpriviledged ISA, Page 608
# RV32I Instruction Set Listings
#
# inst[1:0] = 11
#
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
# | inst[4:2] |   000   |   001   |   010   |   011    |   100   |   101   |   110   |   111   |
# | inst[6:5] |         |         |         |          |         |         |         |         |
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
# |        00 |  LOAD   |         |         | MISC-MEM |  OP-IMM |  AUIPC  |         |         |
# |        01 |  STORE  |         |         |   AMO    |  OP     |  LUI    |         |         |
# |        10 |         |         |         |          |         |         |         |         |
# |        11 |  BRANCH |  JALR   |         |   JAL    |  SYSTEM |         |         |         |
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
#
# The blank fields are illegal instructions in RV32-IMA-ZICSR

# ---------------------------------------------------------------------------- #

from typing import Union
from enum import Enum, auto


class Reg_ops(Enum):
    # RV32-I
    ADD = auto()
    SUB = auto()
    XOR = auto()
    OR = auto()
    AND = auto()
    SLL = auto()
    SRL = auto()
    SRA = auto()
    SLT = auto()
    SLTU = auto()

    # RV32-M
    MUL = auto()
    MULH = auto()
    MULHSU = auto()
    MULHU = auto()
    DIV = auto()
    DIVU = auto()
    REM = auto()
    REMU = auto()

    def __str__(self):
        return self.name.lower()


class Imm_ops(Enum):
    # RV32-I
    ADDI = auto()
    XORI = auto()
    ORI = auto()
    ANDI = auto()
    SLLI = auto()
    SRLI = auto()
    SRAI = auto()
    SLTI = auto()
    SLTIU = auto()

    JALR = auto()

    def __str__(self):
        return self.name.lower()


class Load_ops(Enum):
    # RV32-I
    LB = auto()
    LH = auto()
    LW = auto()
    LBU = auto()
    LHU = auto()

    def __str__(self):
        return self.name.lower()


class Store_ops(Enum):
    # RV32-I
    SB = auto()
    SH = auto()
    SW = auto()

    def __str__(self):
        return self.name.lower()


class Branch_ops(Enum):
    # RV32-I
    BEQ = auto()
    BNE = auto()
    BLT = auto()
    BGE = auto()
    BLTU = auto()
    BGEU = auto()

    def __str__(self):
        return self.name.lower()


class Upper_ops(Enum):
    # RV32-I
    LUI = auto()
    AUIPC = auto()

    def __str__(self):
        return self.name.lower()


class Jump_ops(Enum):
    # RV32-I
    JAL = auto()

    def __str__(self):
        return self.name.lower()


class Misc_mem_ops(Enum):
    # RV32-I
    FENCE = auto()
    FENCE_TSO = auto()
    PAUSE = auto()

    def __str__(self):
        return self.name.lower().replace("_", ".")


class Atomic_ops(Enum):
    # RV32-A
    LR_W = auto()
    SC_W = auto()
    AMOSWAP_W = auto()
    AMOADD_W = auto()
    AMOXOR_W = auto()
    AMOAND_W = auto()
    AMOOR_W = auto()
    AMOMIN_W = auto()
    AMOMAX_W = auto()
    AMOMINU_W = auto()
    AMOMAXU_W = auto()

    def __str__(self):
        return self.name.lower().replace("_", ".")


class System_ops(Enum):
    # RV32-I
    ECALL = auto()
    EBREAK = auto()

    # RV32 Privledged ISA
    SRET = auto()
    MRET = auto()
    MNRET = auto()

    WFI = auto()

    def __str__(self):
        return self.name.lower()


class Zicsr_ops(Enum):
    CSRRW = auto()
    CSRRS = auto()
    CSRRC = auto()

    def __str__(self):
        return self.name.lower()


class Zicsr_imm_ops(Enum):
    CSRRWI = auto()
    CSRRSI = auto()
    CSRRCI = auto()

    def __str__(self):
        return self.name.lower()


OpCode = Union[
    Reg_ops,
    Imm_ops,
    Load_ops,
    Store_ops,
    Branch_ops,
    Upper_ops,
    Jump_ops,
    Misc_mem_ops,
    Atomic_ops,
    System_ops,
    Zicsr_ops,
    Zicsr_imm_ops,
]
