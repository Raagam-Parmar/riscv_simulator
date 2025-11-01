from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

from src.isa.instructions._verify import verify_reg, verify_imm20, verify_2b_align
from src.isa.formats import j_type
from src.utils.bits import sign_extend


class Jal_ops(Enum):
    """
    Opcode for JAL instruction.

    ### Format
    ```
    31                                        12 11            7 6         0
    +-------------------------------------------+---------------+-----------+
    |          imm[20|10:1|11|19:12]            |       rd      |  1101111  |
    +-------------------------------------------+---------------+-----------+
    ```

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


def disassemble_jal(inst: int) -> Optional[Jal]:
    rd = j_type.rd.extract(inst)
    imm20 = j_type.j_imm_20.extract(inst)
    imm10_1 = j_type.j_imm_10_1.extract(inst)
    imm11 = j_type.j_imm_11.extract(inst)
    imm19_12 = j_type.j_imm_19_12.extract(inst)

    imm = imm20 << 20 | imm19_12 << 12 | imm11 << 11 | imm10_1 << 1
    imm = sign_extend(imm, j_type.j_imm_width)

    return Jal(Jal_ops.JAL, rd, imm)
