from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

from src.isa.instructions._verify import verify_reg, verify_imm12
from src.isa.formats import i_type
from src.utils.bits import sign_extend


class Jalr_ops(Enum):
    """
    Opcode for JALR instruction.

    ### Format
    ```
    31                     20 19   15 14      12 11            7 6         0
    +------------------------+-------+----------+---------------+-----------+
    |       imm[11:0]        |  rs1  |  funct3  |      rd       |  1100111  |
    +------------------------+-------+----------+---------------+-----------+
    ```

    ### Opcode (RV32-I)
    - `JALR`
    """

    JALR = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Jalr:
    op: Jalr_ops
    rd: int
    rs1: int
    imm: int
    # encoded as -2048 <= imm <= 2047  (2**11 = 2048)
    # actual same as encoded

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_imm12(self.imm)

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=self.rs1, rs2=None, rd=self.rd, imm=self.imm
    #     )

    def __str__(self):
        """
        `op rd, rs1, imm`
        """
        return f"{self.op} \tx{self.rd}, x{self.rs1}, {self.imm}"


def disassemble_jalr(inst: int) -> Optional[Jalr]:
    fun3 = i_type.funct3.extract(inst)

    if fun3 != 0b000:
        return None

    rd = i_type.rd.extract(inst)
    rs1 = i_type.rs1.extract(inst)
    imm = sign_extend(i_type.i_imm.extract(inst), i_type.i_imm_width)

    return Jalr(Jalr_ops.JALR, rd, rs1, imm)
