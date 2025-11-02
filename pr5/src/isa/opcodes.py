"""
The opcode is the least significant 7-bits of an instruction.

`inst[0]` and `inst[6]` are the MSB and LSB of the opcode respectively.

`inst[0]` and `inst[1]` are always set
to `1`.

Below is the format table for the rest of the opcodes supported by the simulation
library. Unsuppported opcode cells are left blank.

## Opcodes

|           | inst[4:2] |   000   |   001   |   010   |    011    |   100   |   101   |   110   |   111   |
|-----------|-----------|---------|---------|---------|-----------|---------|---------|---------|---------|
| inst[6:5] |           |         |         |         |           |         |         |         |         |
|        00 |           |  LOAD   |         |         | MISC-MEM  |  OP-IMM |  AUIPC  |         |         |
|        01 |           |  STORE  |         |         |    AMO    |  OP     |  LUI    |         |         |
|        10 |           |         |         |         |           |         |         |         |         |
|        11 |           |  BRANCH |  JALR   |         |    JAL    |  SYSTEM |         |         |         |

See: [RV32/64G Instruction Set Listings](https://docs.riscv.org/reference/isa/unpriv/rv-32-64g.html)
"""

from typing import Union

from src.isa.instructions.reg_reg import Reg_reg_ops
from src.isa.instructions.reg_imm import Reg_imm_ops
from src.isa.instructions.jalr import Jalr_ops
from src.isa.instructions.load import Load_ops
from src.isa.instructions.store import Store_ops
from src.isa.instructions.branch import Branch_ops
from src.isa.instructions.upper_imm import Upper_imm_ops
from src.isa.instructions.jal import Jal_ops
from src.isa.instructions.misc_mem import Misc_mem_ops
from src.isa.instructions.atomic import Atomic_ops
from src.isa.instructions.environment import Env_ops
from src.isa.instructions.zicsr_reg_reg import Zicsr_reg_reg_ops
from src.isa.instructions.zicsr_reg_imm import Zicsr_reg_imm_ops

OpCode = Union[
    Reg_reg_ops,
    Reg_imm_ops,
    Jalr_ops,
    Load_ops,
    Store_ops,
    Branch_ops,
    Upper_imm_ops,
    Jal_ops,
    Misc_mem_ops,
    Atomic_ops,
    Env_ops,
    Zicsr_reg_reg_ops,
    Zicsr_reg_imm_ops,
]
"""
List of all suppported opcodes by the simulation library.
- `Reg_reg_ops`
- `Reg_imm_ops`
- `Jalr_ops`
- `Load_ops`
- `Store_ops`
- `Branch_ops`
- `Upper_imm_ops`
- `Jal_ops`
- `Misc_mem_ops`
- `Atomic_ops`
- `System_ops`
- `Zicsr_reg_reg_ops`
- `Zicsr_reg_imm_ops`
"""
