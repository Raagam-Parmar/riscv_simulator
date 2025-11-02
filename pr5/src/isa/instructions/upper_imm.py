"""
# Upper Immediate Instruction

```
31                                                        12 11           7 6             0
+-----------------------------------------------------------+--------------+--------------+
|                          imm[31:12]                       |      rd      |    opcode    |
+-----------------------------------------------------------+--------------+--------------+
```
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

from src.isa.instructions._verify import verify_reg, verify_uimm20
from src.utils.field import Field


class Upper_imm_ops(Enum):
    """
    Opcodes for branch instruction.

    ### Opcodes (RV32-I)
    - `LUI` (opcode `0110111`)
    - `AUIPC` (opcode `0010111`)
    """

    LUI = auto()
    AUIPC = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Upper_imm:
    """
    Datatype for upper-immediate instructions
    """

    op: Upper_imm_ops
    rd: int
    imm: int
    # encoded as 0 <= imm <= 1048575   (2**20 = 1048576)

    def __post_init__(self):
        verify_reg(self.rd)
        verify_uimm20(self.imm)

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=None, rs2=None, rd=self.rd, imm=self.imm
    #     )

    def __str__(self):
        """
        `op rd, imm`
        """
        return f"{self.op} \tx{self.rd}, {hex(self.imm)}"


_imm = Field(31, 12)
"""
**U-Type immediate**: Bits 31 to 12 of an instruction
"""


_rd = Field(11, 7)
"""
**Destination register**: Bits 11 to 7 of an instruction
"""


_imm_width = _imm.width
"""
Width of the U-type immediate field
"""


def decode_auipc(inst: int) -> Optional[Upper_imm]:
    """
    Decodes a 32-bit instruction into a `Upper_imm` `AUIPC` instruction if possible, otherwise
    returns `None`.
    """

    rd = _rd.extract(inst)
    imm = _imm.extract(inst)

    return Upper_imm(Upper_imm_ops.AUIPC, rd, imm)


def decode_lui(inst: int) -> Optional[Upper_imm]:
    """
    Decodes a 32-bit instruction into a `Upper_imm` `LUI` instruction if possible, otherwise
    returns `None`.
    """

    rd = _rd.extract(inst)
    imm = _imm.extract(inst)

    return Upper_imm(Upper_imm_ops.LUI, rd, imm)
