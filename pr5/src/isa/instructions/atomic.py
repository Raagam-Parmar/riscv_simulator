"""
# Atomic Instructions

```
31           27 26 25 24          20 19          15 14    12 11           7 6             0
+--------------+--+--+--------------+--------------+--------+--------------+--------------+
|    funct5    |aq|rl|     rs2      |     rs1      | funct3 |      rd      |   0101111    |
+--------------+--+--+--------------+--------------+--------+--------------+--------------+
```
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

from src.isa.instructions._verify import verify_reg, verify_bit
from src.utils.field import Field


class Atomic_ops(Enum):
    """
    Opcodes for atomic instructions.

    ### Opcodes (RV32-A)
    - `LR_W` - Load reserved
    - `SC_W` - Store conditional
    - `AMOSWAP_W`
    - `AMOADD_W`
    - `AMOXOR_W`
    - `AMOAND_W`
    - `AMOOR_W`
    - `AMOMIN_W`
    - `AMOMAX_W`
    - `AMOMINU_W`
    - `AMOMAXU_W`
    """

    LR_W = auto()
    SC_W = auto()
    AMOSWAP_W = auto()
    AMOADD_W = auto()
    AMOXOR_W = auto()
    AMOAND_W = auto()
    AMOOR_W = auto()
    AMOMIN_W = auto()
    AMOMAX_W = auto()
    AMOMINU_W = auto()
    AMOMAXU_W = auto()

    def __str__(self):
        return self.name.lower().replace("_", ".")

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Atomic:
    """
    Datatype for atomic instructions
    """

    op: Atomic_ops
    rd: int
    rs1: int
    rs2: int
    aq: int
    rl: int

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_reg(self.rs2)
        verify_bit(self.aq)
        verify_bit(self.rl)

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=self.rs1, rs2=self.rs2, rd=self.rd, imm=None
    #     )

    def __str__(self):
        """
        `op[.aq | .rl | .aqrl] rd, rs2, (rs1)`
        """
        show = f"{self.op}"

        if self.aq and not self.rl:
            show += ".aq"

        elif self.rl and not self.aq:
            show += ".rl"

        elif self.aq and self.rl:
            show += ".aqrl"

        return f"{show} \tx{self.rd}, x{self.rs2}, (x{self.rs1})"


amo_tbl: Dict[int, Atomic_ops] = {
    0b00010: Atomic_ops.LR_W,
    0b00011: Atomic_ops.SC_W,
    0b00001: Atomic_ops.AMOSWAP_W,
    0b00000: Atomic_ops.AMOADD_W,
    0b00100: Atomic_ops.AMOXOR_W,
    0b01100: Atomic_ops.AMOAND_W,
    0b01000: Atomic_ops.AMOOR_W,
    0b10000: Atomic_ops.AMOMIN_W,
    0b10100: Atomic_ops.AMOMAX_W,
    0b11000: Atomic_ops.AMOMINU_W,
    0b11100: Atomic_ops.AMOMAXU_W,
}
"""
Maps `funct5` to atomic opcodes
"""


a_fun5_field = Field(31, 27)
"""
**5-bit function code**: Bits 31 to 27 of an instruction
"""


a_aq_field = Field(26, 26)
"""
**Acquire**: Bit 26 of an instruction
"""


a_rl_field = Field(25, 25)
"""
**Release**: Bit 25 of an instruction
"""


_fun3 = Field(14, 12)
"""
**3-bit function code**: Bits 14 to 12 of an instruction
"""


_rs2 = Field(24, 20)
"""
**Second source register**: Bits 24 to 20 of an instruction
"""


_rs1 = Field(19, 15)
"""
**First source register**: Bits 19 to 15 of an instruction
"""


_rd = Field(11, 7)
"""
**Destination register**: Bits 11 to 7 of an instruction
"""


def decode_amo(inst: int) -> Optional[Atomic]:
    """
    Decodes a 32-bit instruction into a `Atomic` instruction if possible, otherwise
    returns `None`.
    """

    fun3 = _fun3.extract(inst)

    if fun3 != 0b010:
        return None

    fun5 = a_fun5_field.extract(inst)

    if fun5 not in amo_tbl:
        return None

    rs2 = _rs2.extract(inst)

    if (fun5 == 0b00010) and (rs2 != 0b00000):
        return None

    rs1 = _rs1.extract(inst)
    rd = _rd.extract(inst)
    aq = a_aq_field.extract(inst)
    rl = a_rl_field.extract(inst)

    return Atomic(amo_tbl[fun5], rd, rs1, rs2, aq, rl)
