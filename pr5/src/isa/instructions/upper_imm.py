from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

from src.isa.instructions._verify import verify_reg, verify_uimm20
from src.isa.formats import u_type


class Upper_imm_ops(Enum):
    """
    Opcodes for branch instruction.

    ### Format

    ```
    31                                        12 11            7 6         0
    +-------------------------------------------+---------------+-----------+
    |                imm[31:12]                 |       rd      |  opcode   |
    +-------------------------------------------+---------------+-----------+
    ```

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


def disassemble_auipc(inst: int) -> Optional[Upper_imm]:
    rd = u_type.rd.extract(inst)
    imm = u_type.u_imm.extract(inst)

    return Upper_imm(Upper_imm_ops.AUIPC, rd, imm)


def disassemble_lui(inst: int) -> Optional[Upper_imm]:
    rd = u_type.rd.extract(inst)
    imm = u_type.u_imm.extract(inst)

    return Upper_imm(Upper_imm_ops.LUI, rd, imm)
