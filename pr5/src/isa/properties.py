from typing import Union, TypeGuard
from .formats import (
    Instruction,
    Reg,
    Jalr,
    Imm,
    Load,
    Store,
    Branch,
    Upper,
    Jal,
    Misc_mem,
    Atomic,
    # System,
    Zicsr,
    Zicsr_Imm,
)

Instruction_with_rs1 = Union[Reg, Imm, Load, Store, Branch, Misc_mem, Atomic, Zicsr]

Instruction_with_rs2 = Union[Reg, Store, Branch, Atomic]

Instruction_with_rd = Union[
    Reg, Imm, Load, Upper, Jal, Misc_mem, Atomic, Zicsr, Zicsr_Imm
]

Instruction_with_imm = Union[Imm, Load, Store, Branch, Upper, Jal, Zicsr_Imm]


def has_rs1(inst: Instruction) -> TypeGuard[Instruction_with_rs1]:
    return isinstance(inst, (Reg, Imm, Load, Store, Branch, Misc_mem, Atomic, Zicsr))


def has_rs2(inst: Instruction) -> TypeGuard[Instruction_with_rs2]:
    return isinstance(inst, (Reg, Store, Branch, Atomic))


def has_rd(inst: Instruction) -> TypeGuard[Instruction_with_rd]:
    return isinstance(
        inst, (Reg, Imm, Load, Upper, Jal, Misc_mem, Atomic, Zicsr, Zicsr_Imm)
    )


def has_imm(inst: Instruction) -> TypeGuard[Instruction_with_imm]:
    return isinstance(inst, (Imm, Load, Store, Branch, Upper, Jal, Zicsr_Imm))


def modifies_pc(inst: Instruction) -> bool:
    return isinstance(inst, (Branch, Jal, Jalr))
