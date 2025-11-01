from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

from src.isa.instructions._verify import verify_reg
from src.isa.formats import r_type


class Reg_reg_ops(Enum):
    """
    Opcodes for register-register instructions.

    ###  Format
    ```
    31             25 24   20 19   15 14      12 11            7 6         0
    +----------------+-------+-------+----------+---------------+-----------+
    |     funct7     |  rs2  |  rs1  |  funct3  |      rd       |  0110011  |
    +----------------+-------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `ADD`
    - `SUB`
    - `XOR`
    - `OR`
    - `AND`
    - `SLL`
    - `SRL`
    - `SRA`
    - `SLT`
    - `SLTU`

    ### Opcodes (RV32-M)
    - `MUL`
    - `MULH`
    - `MULHSU`
    - `MULHU`
    - `DIV`
    - `DIVU`
    - `REM`
    - `REMU`
    """

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

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Reg_reg:
    op: Reg_reg_ops
    rd: int
    rs1: int
    rs2: int

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_reg(self.rs2)

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=self.rs1, rs2=self.rs2, rd=self.rd, imm=None
    #     )

    def __str__(self):
        """
        `op rd, rs1, rs2`
        """
        return f"{self.op} \tx{self.rd}, x{self.rs1}, x{self.rs2}"


op_tbl: Dict[Tuple[int, int], Reg_reg_ops] = {
    # RV32-I
    (0b000, 0b0000000): Reg_reg_ops.ADD,
    (0b000, 0b0100000): Reg_reg_ops.SUB,
    (0b001, 0b0000000): Reg_reg_ops.SLL,
    (0b010, 0b0000000): Reg_reg_ops.SLT,
    (0b011, 0b0000000): Reg_reg_ops.SLTU,
    (0b100, 0b0000000): Reg_reg_ops.XOR,
    (0b101, 0b0000000): Reg_reg_ops.SRL,
    (0b101, 0b0100000): Reg_reg_ops.SRA,
    (0b110, 0b0000000): Reg_reg_ops.OR,
    (0b111, 0b0000000): Reg_reg_ops.AND,
    # RV32-M
    (0b000, 0b0000001): Reg_reg_ops.MUL,
    (0b001, 0b0000001): Reg_reg_ops.MULH,
    (0b010, 0b0000001): Reg_reg_ops.MULHSU,
    (0b011, 0b0000001): Reg_reg_ops.MULHU,
    (0b100, 0b0000001): Reg_reg_ops.DIV,
    (0b101, 0b0000001): Reg_reg_ops.DIVU,
    (0b110, 0b0000001): Reg_reg_ops.REM,
    (0b111, 0b0000001): Reg_reg_ops.REMU,
}
"""
Maps (funct3, funct7) pairs to register-register opcodes
"""


def disassemble_op(inst: int) -> Optional[Reg_reg]:
    """
    Disassemble a 32-bit instruction into register-register instruction.

    :param inst: 32-bit instruction

    :return: Register-register instruction if `inst` is a valid register-register
    instruction, otherwise `None`.
    """

    fun3 = r_type.funct3.extract(inst)
    fun7 = r_type.funct7.extract(inst)

    pair = (fun3, fun7)

    if pair not in op_tbl:
        return None

    rd = r_type.rd.extract(inst)
    rs1 = r_type.rs1.extract(inst)
    rs2 = r_type.rs2.extract(inst)

    return Reg_reg(op_tbl[pair], rd, rs1, rs2)

