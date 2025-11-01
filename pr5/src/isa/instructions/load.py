from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

from src.isa.instructions._verify import verify_reg, verify_imm12
from src.isa.formats import i_type
from src.utils.bits import sign_extend


class Load_ops(Enum):
    """
    Opcodes for memory-load instruction.

    ### Format
    ```
    31                     20 19   15 14      12 11            7 6         0
    +------------------------+-------+----------+---------------+-----------+
    |       imm[11:0]        |  rs1  |  funct3  |      rd       |  0000011  |
    +------------------------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `LB`
    - `LH`
    - `LW`
    - `LBU`
    - `LHU`
    """

    LB = auto()
    LH = auto()
    LW = auto()
    LBU = auto()
    LHU = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


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

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=self.rs1, rs2=None, rd=self.rd, imm=self.imm
    #     )

    def __str__(self):
        """
        `op rd, imm(rs1)`
        """
        return f"{self.op} \tx{self.rd}, {self.imm}(x{self.rs1})"


load_tbl: Dict[int, Load_ops] = {
    0b000: Load_ops.LB,
    0b001: Load_ops.LH,
    0b010: Load_ops.LW,
    0b100: Load_ops.LBU,
    0b101: Load_ops.LHU,
}
"""
Maps funct3 to load opcodes
"""


def disassemble_load(inst: int) -> Optional[Load]:
    fun3 = i_type.funct3.extract(inst)

    if fun3 not in load_tbl:
        return None

    rd = i_type.rd.extract(inst)
    rs1 = i_type.rs1.extract(inst)
    imm = sign_extend(i_type.i_imm.extract(inst), i_type.i_imm_width)

    return Load(load_tbl[fun3], rd, rs1, imm)
