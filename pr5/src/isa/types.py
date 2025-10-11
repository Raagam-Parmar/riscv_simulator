from typing import Union
from formats import (
    Reg,
    Imm,
    Load,
    Store,
    Branch,
    Upper,
    Jump,
    Misc_mem,
    Atomic,
    System,
    Zicsr,
    Zicsr_Imm,
)

Instruction = Union[
    Reg,
    Imm,
    Load,
    Store,
    Branch,
    Upper,
    Jump,
    Misc_mem,
    Atomic,
    System,
    Zicsr,
    Zicsr_Imm,
]
