from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional, Union

from src.isa.instructions._verify import verify_reg, verify_uimm5, verify_uimm12
from src.isa.formats import r_type
from src.utils.field import Field


class System_ops(Enum):
    """
    Opcodes for system instructions.

    ###  Format
    ```
    31             25 24   20 19   15 14      12 11            7 6         0
    +----------------+-------+-------+----------+---------------+-----------+
    |     funct7     |  rs2  |  rs1  |  funct3  |      rd       |  1110011  |
    +----------------+-------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `ECALL`
    - `EBREAK`

    ### Opcodes (Priviledged RV32)
    - `SRET`
    - `MRET`
    - `MNRET`
    - `WFI`
    """

    ECALL = auto()
    EBREAK = auto()

    SRET = auto()
    MRET = auto()
    MNRET = auto()

    WFI = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class System:
    op: System_ops

    # def fields(self):
    #     return UnifiedInstruction(op=self.op, rs1=None, rs2=None, rd=None, imm=None)

    def __str__(self):
        """
        `op`
        """
        return f"{self.op}"


class Zicsr_reg_imm_ops(Enum):
    """
    Opcodes for CSR manipulating register-immediate instructions.

    ### Format
    ```
    31                     20 19   15 14      12 11            7 6         0
    +------------------------+-------+----------+---------------+-----------+
    |          csr           | uimm  |  funct3  |      rd       |  1110011  |
    +------------------------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (Priviledged RV32)
    - `CSRRWI`
    - `CSRRSI`
    - `CSRRCI`
    """

    CSRRWI = auto()
    CSRRSI = auto()
    CSRRCI = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Zicsr_reg_imm:
    op: Zicsr_reg_imm_ops
    rd: int
    csr: int
    uimm: int
    # encoded as 0 <= uimm <= 32   (2**5 = 32)
    # actual same as encoded

    def __post_init__(self):
        verify_reg(self.rd)
        verify_uimm5(self.uimm)
        verify_uimm12(self.csr)

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=None, rs2=None, rd=self.rd, imm=self.uimm
    #     )

    def __str__(self):
        """
        `op rd, csr, uimm`
        """
        return f"{self.op} \tx{self.rd}, 0x{self.csr:03x}, {self.uimm}"


class Zicsr_reg_reg_ops(Enum):
    """
    Opcodes for CSR manipulating register-immediate instructions.

    ### Format
    ```
    31                     20 19   15 14      12 11            7 6         0
    +------------------------+-------+----------+---------------+-----------+
    |          csr           |  rs1  |  funct3  |      rd       |  1110011  |
    +------------------------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (Priviledged RV32)
    - `CSRRW`
    - `CSRRS`
    - `CSRRC`
    """

    CSRRW = auto()
    CSRRS = auto()
    CSRRC = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Zicsr_reg_reg:
    op: Zicsr_reg_reg_ops
    rd: int
    rs1: int
    csr: int

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_uimm12(self.csr)

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=self.rs1, rs2=None, rd=self.rd, imm=None
    #     )

    def __str__(self):
        """
        `op rd, csr, rs1`
        """
        return f"{self.op} \tx{self.rd}, 0x{self.csr:03x}, x{self.rs1}"


sys_const = Field(31, 7)
"""
**Constant field**: Bits 31 to 7 of an instruction
"""


csr_uimm = Field(19, 15)
"""
**CSR unsigned immediate**: Bits 19 to 15 of an instruction
"""


csr = Field(31, 20)
"""
**CSR**: its 31 to 20 of an instruction
"""


system_tbl: Dict[int, System_ops] = {
    0x0000: System_ops.ECALL,
    0x2000: System_ops.EBREAK,
    # RV32 Priviledged ISA
    0x204000: System_ops.SRET,
    0x604000: System_ops.MRET,
    0xE04000: System_ops.MNRET,
    0x20A000: System_ops.WFI,
}


zicsr_tbl: Dict[int, Zicsr_reg_reg_ops] = {
    0b001: Zicsr_reg_reg_ops.CSRRW,
    0b010: Zicsr_reg_reg_ops.CSRRS,
    0b011: Zicsr_reg_reg_ops.CSRRC,
}

zicsr_imm_tbl: Dict[int, Zicsr_reg_imm_ops] = {
    0b101: Zicsr_reg_imm_ops.CSRRWI,
    0b110: Zicsr_reg_imm_ops.CSRRSI,
    0b111: Zicsr_reg_imm_ops.CSRRCI,
}


def disassemble_zicsr(inst: int, fun3: int) -> Optional[Zicsr_reg_reg]:
    rs1 = r_type.rs1.extract(inst)
    r_csr = csr.extract(inst)
    rd = r_type.rd.extract(inst)

    return Zicsr_reg_reg(zicsr_tbl[fun3], rd, rs1, r_csr)


def disassemble_zicsr_imm(inst: int, fun3: int) -> Optional[Zicsr_reg_imm]:
    imm = csr_uimm.extract(inst)
    r_csr = csr.extract(inst)
    rd = r_type.rd.extract(inst)

    return Zicsr_reg_imm(zicsr_imm_tbl[fun3], rd, r_csr, imm)


def disassemble_system(inst: int) -> Union[Zicsr_reg_reg, Zicsr_reg_imm, System, None]:
    sys = sys_const.extract(inst)

    if sys_const in system_tbl:
        return System(system_tbl[sys])

    fun3 = r_type.funct3.extract(inst)

    if fun3 in zicsr_tbl:
        return disassemble_zicsr(inst, fun3)

    if fun3 in zicsr_imm_tbl:
        return disassemble_zicsr_imm(inst, fun3)

    return None
