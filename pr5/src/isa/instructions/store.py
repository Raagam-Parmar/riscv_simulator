from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

from src.isa.instructions._verify import verify_reg, verify_imm12
from src.isa.formats import s_type
from src.utils.bits import sign_extend


class Store_ops(Enum):
    """
    Opcodes for memory-store instruction.

    ### Format
    ```
    31             25 24   20 19   15 14      12 11            7 6         0
    +----------------+-------+-------+----------+---------------+-----------+
    |   imm[11:5]    |  rs2  |  rs1  |  funct3  |   imm[4:0]    |  0100011  |
    +----------------+-------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `SB`
    - `SH`
    - `SW`
    """

    SB = auto()
    SH = auto()
    SW = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


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

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=self.rs1, rs2=self.rs2, rd=None, imm=self.imm
    #     )

    def __str__(self):
        """
        `op rs2, imm(rs1)
        """
        return f"{self.op} \tx{self.rs2}, {self.imm}(x{self.rs1})"


store_tbl: Dict[int, Store_ops] = {
    0b000: Store_ops.SB,
    0b001: Store_ops.SH,
    0b010: Store_ops.SW,
}
"""
Maps funct3 to store opcodes
"""


# ---------------------------------------------------------------------------- #
# Store Instruction
# ---------------------------------------------------------------------------- #
def disassemble_store(inst: int) -> Optional[Store]:
    fun3 = s_type.funct3.extract(inst)

    if fun3 not in store_tbl:
        return None

    rs1 = s_type.rs1.extract(inst)
    rs2 = s_type.rs2.extract(inst)
    imm4_0 = s_type.s_imm_low.extract(inst)
    imm11_5 = s_type.s_imm_high.extract(inst)

    imm = imm11_5 << 5 | imm4_0
    imm = sign_extend(imm, s_type.s_imm_width)

    return Store(store_tbl[fun3], rs1, rs2, imm)
