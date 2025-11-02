"""
# JALR (Jump and link register) Instruction

```
31                                20 19          15 14    12 11           7 6             0
+-----------------------------------+--------------+--------+--------------+--------------+
|             imm[11:0]             |     rs1      | funct3 |      rd      |   1100111    |
+-----------------------------------+--------------+--------+--------------+--------------+
```
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

from src.isa.instructions._verify import verify_reg, verify_imm12
from src.utils.bits import sign_extend
from src.utils.field import Field


class Jalr_ops(Enum):
    """
    Opcode for JALR instruction.

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
    """
    Datatype for JALR instruction
    """

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


_imm = Field(31, 20)
"""
**I-Type immediate**: Bits 31 to 20 of an instruction
"""


_rs1 = Field(19, 15)
"""
**First source register**: Bits 19 to 15 of an instruction
"""


_fun3 = Field(14, 12)
"""
**3-bit function code**: Bits 14 to 12 of an instruction
"""


_rd = Field(11, 7)
"""
**Destination register**: Bits 11 to 7 of an instruction
"""


_imm_width = _imm.width
"""
Width of the I-type immediate field
"""


def decode_jalr(inst: int) -> Optional[Jalr]:
    """
    Decodes a 32-bit instruction into a `Jalr` instruction if possible, otherwise
    returns `None`.
    """

    fun3 = _fun3.extract(inst)

    if fun3 != 0b000:
        return None

    rd = _rd.extract(inst)
    rs1 = _rs1.extract(inst)
    imm = sign_extend(_imm.extract(inst), _imm_width)

    return Jalr(Jalr_ops.JALR, rd, rs1, imm)
