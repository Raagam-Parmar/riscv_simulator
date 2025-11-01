from typing import Union

from src.isa.instructions.reg_reg import Reg_reg, disassemble_op
from src.isa.instructions.reg_imm import Reg_imm, disassemble_op_imm
from src.isa.instructions.jalr import Jalr, disassemble_jalr
from src.isa.instructions.load import Load, disassemble_load
from src.isa.instructions.store import Store, disassemble_store
from src.isa.instructions.branch import Branch, disassemble_branch
from src.isa.instructions.upper_imm import Upper_imm, disassemble_auipc, disassemble_lui
from src.isa.instructions.jal import Jal, disassemble_jal
from src.isa.instructions.misc_mem import Misc_mem, disassemble_misc_mem
from src.isa.instructions.atomic import Atomic, disassemble_amo
from src.isa.instructions.system import System, Zicsr_reg_reg, Zicsr_reg_imm, disassemble_system


Instruction = Union[
    Reg_reg,
    Reg_imm,
    Jalr,
    Load,
    Store,
    Branch,
    Upper_imm,
    Jal,
    Misc_mem,
    Atomic,
    System,
    Zicsr_reg_reg,
    Zicsr_reg_imm,
]
"""
List of all suppported instructions by the simulation library.
- `Reg_reg`
- `Reg_imm`
- `Jalr`
- `Load`
- `Store`
- `Branch`
- `Upper_imm`
- `Jal`
- `Misc_mem`
- `Atomic`
- `System`
- `Zicsr_reg_reg`
- `Zicsr_reg_imm`
"""
