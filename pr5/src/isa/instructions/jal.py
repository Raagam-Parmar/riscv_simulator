"""
# JAL Instruction

```
31                                                        12 11           7 6             0
+-----------------------------------------------------------+--------------+--------------+
|                imm[20 | 10:1 | 11 | 19:12]                |      rd      |   1101111    |
+-----------------------------------------------------------+--------------+--------------+
```
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

from src.isa.instructions._verify import verify_reg, verify_imm20, verify_2b_align
from src.utils.bits import sign_extend
from src.utils.field import Field


class Jal_ops(Enum):
    """
    Opcode for JAL instruction.

    ### Opcodes (RV32-I)
    - `JAL`
    """

    JAL = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Jal:
    """
    Datatype for JAL instruction
    """

    op: Jal_ops
    rd: int
    imm: int
    # encoded as -524288 <= imm <= 524287   (2**19 = 524288)
    # actual  as -1048575 <= imm <= 1048576 (2**20 = 1048576) (evens only)

    def __post_init__(self):
        verify_reg(self.rd)
        verify_imm20(self.imm // 2)
        verify_2b_align(self.imm)

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=None, rs2=None, rd=self.rd, imm=self.imm
    #     )

    def __str__(self):
        """
        `op rd, imm`
        """
        return f"{self.op} \tx{self.rd}, {hex(self.imm)}"


_imm_20 = Field(31, 31)
"""
**J-Type immediate[20]**: MSB of an instruction
"""


_imm_10_1 = Field(30, 21)
"""
J-Type immediate[10:1]**: Bits 30 to 21 of an instruction
"""


_imm_11 = Field(20, 20)
"""
J-Type immediate[11]**: Bit 20 of an instruction
"""


_imm_19_12 = Field(19, 12)
"""
J-Type immediate[19:12]**: Bits 19 to 12 of an instruction
"""


_rd = Field(11, 7)
"""
**Destination register**: Bits 11 to 7 of an instruction
"""


_imm_width = _imm_20.width + _imm_10_1.width + _imm_11.width + _imm_19_12.width
"""
Width of the J-type immediate field
"""


def decode_jal(inst: int) -> Optional[Jal]:
    """
    Decodes a 32-bit instruction into a `Jal` instruction if possible, otherwise
    returns `None`.
    """

    rd = _rd.extract(inst)
    imm20 = _imm_20.extract(inst)
    imm10_1 = _imm_10_1.extract(inst)
    imm11 = _imm_11.extract(inst)
    imm19_12 = _imm_19_12.extract(inst)

    imm = imm20 << 20 | imm19_12 << 12 | imm11 << 11 | imm10_1 << 1
    imm = sign_extend(imm, _imm_width)

    return Jal(Jal_ops.JAL, rd, imm)
