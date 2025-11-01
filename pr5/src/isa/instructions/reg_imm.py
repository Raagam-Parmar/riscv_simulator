from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

from src.isa.instructions._verify import verify_reg, verify_imm12
from src.isa.formats import i_type
from src.utils.bits import sign_extend


class Reg_imm_ops(Enum):
    """
    Opcodes for register-immediate instructions.

    ### Format
    ```
    31                     20 19   15 14      12 11            7 6         0
    +------------------------+-------+----------+---------------+-----------+
    |       imm[11:0]        |  rs1  |  funct3  |      rd       |  0010011  |
    +------------------------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `ADDI`
    - `XORI`
    - `ORI`
    - `ANDI`
    - `SLLI`
    - `SRLI`
    - `SRAI`
    - `SLTI`
    - `SLTIU`
    """

    ADDI = auto()
    XORI = auto()
    ORI = auto()
    ANDI = auto()
    SLLI = auto()
    SRLI = auto()
    SRAI = auto()
    SLTI = auto()
    SLTIU = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Reg_imm:
    op: Reg_imm_ops
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


op_imm_f3_tbl: Dict[int, Reg_imm_ops] = {
    0b000: Reg_imm_ops.ADDI,
    0b010: Reg_imm_ops.SLTI,
    0b011: Reg_imm_ops.SLTIU,
    0b100: Reg_imm_ops.XORI,
    0b110: Reg_imm_ops.ORI,
    0b111: Reg_imm_ops.ANDI,
}
"""
Maps funct3 to register-immediate opcodes
"""

op_imm_f3_f7_tbl: Dict[Tuple[int, int], Reg_imm_ops] = {
    (0b001, 0b0000000): Reg_imm_ops.SLLI,
    (0b101, 0b0000000): Reg_imm_ops.SRLI,
    (0b101, 0b0100000): Reg_imm_ops.SRAI,
}
"""
Maps (funct3, funct7) pairs to register-immediate opcodes
"""


def disassemble_op_imm(inst: int) -> Optional[Reg_imm]:
    fun3 = i_type.funct3.extract(inst)
    rd = i_type.rd.extract(inst)
    rs1 = i_type.rs1.extract(inst)
    fun7 = i_type.funct7.extract(inst)
    imm = sign_extend(i_type.i_imm.extract(inst), i_type.i_imm_width)

    # TODO Fix constraints for SRAI, SLLI, SRLI

    if fun3 in op_imm_f3_tbl:
        return Reg_imm(op_imm_f3_tbl[fun3], rd, rs1, imm)

    if (fun3, fun7) not in op_imm_f3_f7_tbl:
        return None

    opcode = op_imm_f3_f7_tbl[(fun3, fun7)]

    if (
        opcode is Reg_imm_ops.SLLI
        or opcode is Reg_imm_ops.SRLI
        or opcode is Reg_imm_ops.SRAI
    ):
        return Reg_imm(op_imm_f3_f7_tbl[(fun3, fun7)], rd, rs1, imm & 0b11111)

    return Reg_imm(opcode, rd, rs1, imm)
