"""
# ZICSR Register-Register Instructions

```
31                                20 19          15 14    12 11           7 6             0
+-----------------------------------+--------------+--------+--------------+--------------+
|                csr                |     rs1      | funct3 |      rd      |   1110011    |
+-----------------------------------+--------------+--------+--------------+--------------+
```
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

from src.isa.instructions._verify import verify_reg, verify_uimm12
from src.utils.field import Field


class Zicsr_reg_reg_ops(Enum):
    """
    Opcodes for CSR manipulating register-immediate instructions.

    ### Opcodes (Priviledged RV32)
    - `CSRRW`
    - `CSRRS`
    - `CSRRC`
    """

    CSRRW = auto()
    CSRRS = auto()
    CSRRC = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Zicsr_reg_reg:
    """
    Datatype for zicsr register-register instructions
    """

    op: Zicsr_reg_reg_ops
    rd: int
    rs1: int
    csr: int

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_uimm12(self.csr)

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=self.rs1, rs2=None, rd=self.rd, imm=None
    #     )

    def __str__(self):
        """
        `op rd, csr, rs1`
        """
        return f"{self.op} \tx{self.rd}, 0x{self.csr:03x}, x{self.rs1}"


zicsr_tbl: Dict[int, Zicsr_reg_reg_ops] = {
    0b001: Zicsr_reg_reg_ops.CSRRW,
    0b010: Zicsr_reg_reg_ops.CSRRS,
    0b011: Zicsr_reg_reg_ops.CSRRC,
}
"""
Maps `funct3` to zicsr register register opcodes
"""


_rs1 = Field(19, 15)
"""
**First source register**: Bits 19 to 15 of an instruction
"""


_rd = Field(11, 7)
"""
**Destination register**: Bits 11 to 7 of an instruction
"""


_csr = Field(31, 20)
"""
**CSR**: its 31 to 20 of an instruction
"""


_fun3 = Field(14, 12)
"""
**3-bit function code**: Bits 14 to 12 of an instruction
"""


def decode_zicsr_reg_reg(inst: int) -> Optional[Zicsr_reg_reg]:
    """
    Decodes a 32-bit instruction into a `Zicsr_reg_reg` instruction if possible, otherwise
    returns `None`.
    """

    fun3 = _fun3.extract(inst)

    rs1 = _rs1.extract(inst)
    r_csr = _csr.extract(inst)
    rd = _rd.extract(inst)

    return Zicsr_reg_reg(zicsr_tbl[fun3], rd, rs1, r_csr)
