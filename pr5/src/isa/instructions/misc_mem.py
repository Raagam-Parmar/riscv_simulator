from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

from src.isa.instructions._verify import verify_reg, verify_uimm4
from src.isa.formats import i_type
from src.utils.field import Field


class Misc_mem_ops(Enum):
    """
    Opcodes for miscellaneous memory instructions.

    ### Format
    ```
    31    28 27    24 23   20 19   15 14      12 11            7 6         0
    +-------+--------+-------+-------+----------+---------------+-----------+
    |  fm   |  pred  | succ  |  rs1  |  funct3  |  imm[4:1|11]  |  0001111  |
    +-------+--------+-------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `FENCE`
    - `FENCE_TSO`
    - `PAUSE`
    """

    FENCE = auto()
    FENCE_TSO = auto()
    PAUSE = auto()

    def __str__(self):
        return self.name.lower().replace("_", ".")

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Misc_mem:
    op: Misc_mem_ops
    rd: int
    rs1: int
    succ: int
    pred: int
    fm: int

    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_uimm4(self.succ)
        verify_uimm4(self.pred)
        verify_uimm4(self.fm)

        # def fields(self):
        #     return UnifiedInstruction(
        #         op=self.op, rs1=self.rs1, rs2=None, rd=self.rd, imm=None
        #     )

    def __str__(self):
        if self.op != Misc_mem_ops.FENCE:
            return f"{self.op}"

        pred = ""
        succ = ""

        for i in reversed(range(4)):
            if (self.pred >> i) & 0b1:
                if i == 3:
                    pred += "i"
                if i == 2:
                    pred += "o"
                if i == 1:
                    pred += "r"
                if i == 0:
                    pred += "w"

            if (self.succ >> i) & 0b1:
                if i == 3:
                    succ += "i"
                if i == 2:
                    succ += "o"
                if i == 1:
                    succ += "r"
                if i == 0:
                    succ += "w"

        return f"{self.op} {pred}, {succ}"


misc_mem_tbl: Dict[int, Misc_mem_ops] = {
    0x0020000: Misc_mem_ops.PAUSE,
    0x1066000: Misc_mem_ops.FENCE_TSO,
}


mm_const = Field(31, 7)
"""
**Constant field**: Bits 31 to 7 of an instruction
"""


mm_succ = Field(23, 20)
"""
**Successor**: Bits 23 to 20 of an instruction
"""


mm_pred = Field(27, 24)
"""
**Predecessor**: Bits 27 to 24 of an instruction
"""


mm_fm = Field(31, 28)
"""
**Fence mode**: Bits 31 to 28 of an instruction
"""


def disassemble_misc_mem(inst: int) -> Optional[Misc_mem]:
    fun3 = i_type.funct3.extract(inst)

    const = mm_const.extract(inst)

    rd = i_type.rd.extract(inst)
    rs1 = i_type.rs1.extract(inst)
    succ = mm_succ.extract(inst)
    pred = mm_pred.extract(inst)
    fm = mm_fm.extract(inst)

    if fun3 != 0b000:
        return None

    mop = misc_mem_tbl[const] if const in misc_mem_tbl else Misc_mem_ops.FENCE

    return Misc_mem(mop, rd, rs1, succ, pred, fm)
