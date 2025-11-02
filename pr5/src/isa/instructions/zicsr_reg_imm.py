"""
# ZICSR Register-Register Instructions

```
31                                20 19          15 14    12 11           7 6             0
+-----------------------------------+--------------+--------+--------------+--------------+
|                csr                |     uimm     | funct3 |      rd      |   1110011    |
+-----------------------------------+--------------+--------+--------------+--------------+
```
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

from src.isa.instructions._verify import verify_reg, verify_uimm5, verify_uimm12
from src.utils.field import Field


class Zicsr_reg_imm_ops(Enum):
    """
    Opcodes for CSR manipulating register-immediate instructions.

    ### Opcodes (Priviledged RV32)
    - `CSRRWI`
    - `CSRRSI`
    - `CSRRCI`
    """

    CSRRWI = auto()
    CSRRSI = auto()
    CSRRCI = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Zicsr_reg_imm:
    """
    Datatype for zicsr register-immediate instructions
    """

    op: Zicsr_reg_imm_ops
    rd: int
    csr: int
    uimm: int
    # encoded as 0 <= uimm <= 32   (2**5 = 32)
    # actual same as encoded

    def __post_init__(self):
        verify_reg(self.rd)
        verify_uimm5(self.uimm)
        verify_uimm12(self.csr)

    # def fields(self):
    #     return UnifiedInstruction(
    #         op=self.op, rs1=None, rs2=None, rd=self.rd, imm=self.uimm
    #     )

    def __str__(self):
        """
        `op rd, csr, uimm`
        """
        return f"{self.op} \tx{self.rd}, 0x{self.csr:03x}, {self.uimm}"


zicsr_imm_tbl: Dict[int, Zicsr_reg_imm_ops] = {
    0b101: Zicsr_reg_imm_ops.CSRRWI,
    0b110: Zicsr_reg_imm_ops.CSRRSI,
    0b111: Zicsr_reg_imm_ops.CSRRCI,
}
"""
Maps `funct3` to zicsr register immediate opcodes
"""


csr_uimm = Field(19, 15)
"""
**CSR unsigned immediate**: Bits 19 to 15 of an instruction
"""


_csr = Field(31, 20)
"""
**CSR**: its 31 to 20 of an instruction
"""


_rd = Field(11, 7)
"""
**Destination register**: Bits 11 to 7 of an instruction
"""


_fun3 = Field(14, 12)
"""
**3-bit function code**: Bits 14 to 12 of an instruction
"""


def decode_zicsr_reg_imm(inst: int) -> Optional[Zicsr_reg_imm]:
    """
    Decodes a 32-bit instruction into a `Zicsr_reg_imm` instruction if possible, otherwise
    returns `None`.
    """

    fun3 = _fun3.extract(inst)

    imm = csr_uimm.extract(inst)
    r_csr = _csr.extract(inst)
    rd = _rd.extract(inst)

    return Zicsr_reg_imm(zicsr_imm_tbl[fun3], rd, r_csr, imm)
