"""
# Store Instructions
```
31                 25 24          20 19          15 14    12 11           7 6             0
+--------------------+--------------+--------------+--------+--------------+--------------+
|     imm[11:5]      |     rs2      |     rs1      | funct3 |   imm[4:0]   |   0100011    |
+--------------------+--------------+--------------+--------+--------------+--------------+
```
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

from src.isa.instructions._verify import verify_reg, verify_imm12
from src.utils.bits import sign_extend
from src.utils.field import Field


class Store_ops(Enum):
    """
    Opcodes for store instruction.

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
    """
    Datatype for store instructions
    """

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
Maps `funct3` to store opcodes
"""


_imm_low = Field(11, 7)
"""
**S-Type lower immediate**: Bits 11 to 7 of an instruction
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


_imm_high = Field(31, 25)
"""
**S-Type upper immediate**: Bits 31 to 25 of an instruction
"""


_imm_width = _imm_high.width + _imm_low.width
"""
Width of the S-type immediate field
"""


def decode_store(inst: int) -> Optional[Store]:
    """
    Decodes a 32-bit instruction into a `Store` instruction if possible, otherwise
    returns `None`.
    """

    fun3 = _fun3.extract(inst)

    if fun3 not in store_tbl:
        return None

    rs1 = _rs1.extract(inst)
    rs2 = _rs2.extract(inst)
    imm4_0 = _imm_low.extract(inst)
    imm11_5 = _imm_high.extract(inst)

    imm = imm11_5 << 5 | imm4_0
    imm = sign_extend(imm, _imm_width)

    return Store(store_tbl[fun3], rs1, rs2, imm)
