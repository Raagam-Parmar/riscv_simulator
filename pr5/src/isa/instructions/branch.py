"""
# Branch Instruction

```
31                 25 24          20 19          15 14    12 11           7 6             0
+--------------------+--------------+--------------+--------+--------------+--------------+
|    imm[12|10:5]    |     rs2      |     rs1      | funct3 | imm[4:1|11]  |   1100011    |
+--------------------+--------------+--------------+--------+--------------+--------------+
```
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

from src.isa.instructions._verify import verify_reg, verify_imm12, verify_2b_align
from src.utils.bits import sign_extend
from src.utils.field import Field


class Branch_ops(Enum):
    """
    Opcodes for branch instruction.

    ### Opcodes (RV32-I)
    - `BEQ`
    - `BNE`
    - `BLT`
    - `BGE`
    - `BLTU`
    - `BGEU`
    """

    BEQ = auto()
    BNE = auto()
    BLT = auto()
    BGE = auto()
    BLTU = auto()
    BGEU = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Branch:
    """
    Datatype for branch instructions
    """

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

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=self.rs1, rs2=self.rs2, rd=None, imm=self.imm
    #     )

    def __str__(self):
        """
        `op rs1, rs2, imm`
        """
        return f"{self.op} \tx{self.rs1}, x{self.rs2}, {hex(self.imm)}"


branch_tbl: Dict[int, Branch_ops] = {
    0b000: Branch_ops.BEQ,
    0b001: Branch_ops.BNE,
    0b100: Branch_ops.BLT,
    0b101: Branch_ops.BGE,
    0b110: Branch_ops.BLTU,
    0b111: Branch_ops.BGEU,
}
"""
Maps `funct3` to branch ocodes
"""



_imm_12 = Field(31, 31)
"""
**B-Type immediate[12]**: MSB of an instruction
"""


_imm_10_5 = Field(30, 25)
"""
**B-Type immediate[10:5]**: Bits 30 to 25 of an instruction
"""


_rs2 = Field(24, 20)
"""
**Second source register**: Bits 24 to 20 of an instruction
"""


_rs1 = Field(19, 15)
"""
**First source register**: Bits 19 to 15 of an instruction
"""


_fun3 = Field(14, 12)
"""
**3-bit function code**: Bits 14 to 12 of an instruction
"""


_imm_4_1 = Field(11, 8)
"""
**B-Type immediate[4:1]**: Bits 11 to 8 of an instruction
"""


_imm_11 = Field(7, 7)
"""
**B-Type immediate[11]**: Bit 7 of an instruction
"""



_imm_width = (_imm_12.width + _imm_10_5.width + _imm_4_1.width + _imm_11.width)
"""
Width of the B-type immediate field
"""




def decode_branch(inst: int) -> Optional[Branch]:
    """
    Decodes a 32-bit instruction into a `Branch` instruction if possible, otherwise
    returns `None`.
    """

    fun3 = _fun3.extract(inst)

    if fun3 not in branch_tbl:
        return None

    rs1 = _rs1.extract(inst)
    rs2 = _rs2.extract(inst)
    imm12 = _imm_12.extract(inst)
    imm11 = _imm_11.extract(inst)
    imm10_5 = _imm_10_5.extract(inst)
    imm4_1 = _imm_4_1.extract(inst)

    imm = imm12 << 12 | imm11 << 11 | imm10_5 << 5 | imm4_1 << 1
    imm = sign_extend(imm, _imm_width)

    return Branch(branch_tbl[fun3], rs1, rs2, imm)
