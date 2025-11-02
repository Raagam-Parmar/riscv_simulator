"""
# Environment Instructions

```
31                 25 24          20 19          15 14    12 11           7 6             0
+--------------------+--------------+--------------+--------+--------------+--------------+
|       funct7       |     rs2      |     rs1      | funct3 |      rd      |   1110011    |
+--------------------+--------------+--------------+--------+--------------+--------------+
```
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

from src.utils.field import Field


class Env_ops(Enum):
    """
    Opcodes for environment instructions.

    ### Opcodes (RV32-I)
    - `ECALL`
    - `EBREAK`

    ### Opcodes (Priviledged RV32)
    - `SRET`
    - `MRET`
    - `MNRET`
    - `WFI`
    """

    ECALL = auto()
    EBREAK = auto()

    SRET = auto()
    MRET = auto()
    MNRET = auto()

    WFI = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


@dataclass(frozen=True)
class Env:
    """
    Datatype for environment instructions
    """

    op: Env_ops

    # def fields(self):
    #     return UnifiedInstruction(op=self.op, rs1=None, rs2=None, rd=None, imm=None)

    def __str__(self):
        """
        `op`
        """
        return f"{self.op}"


sys_const = Field(31, 7)
"""
**Constant field**: Bits 31 to 7 of an instruction
"""


tbl: Dict[int, Env_ops] = {
    0x0000: Env_ops.ECALL,
    0x2000: Env_ops.EBREAK,
    # RV32 Priviledged ISA
    0x204000: Env_ops.SRET,
    0x604000: Env_ops.MRET,
    0xE04000: Env_ops.MNRET,
    0x20A000: Env_ops.WFI,
}
"""
Maps the `constant` field (everything but `opcode`) to environment opcodes
"""


def decode_env(inst: int) -> Optional[Env]:
    """
    Decodes a 32-bit instruction into a `Env` instruction if possible, otherwise
    returns `None`.
    """

    sys = sys_const.extract(inst)

    if sys_const in tbl:
        return Env(tbl[sys])

    return None
