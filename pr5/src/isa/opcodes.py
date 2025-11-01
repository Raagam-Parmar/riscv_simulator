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
from src.isa.instructions.system import System_ops, Zicsr_reg_reg_ops, Zicsr_reg_imm_ops

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
    System_ops,
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
