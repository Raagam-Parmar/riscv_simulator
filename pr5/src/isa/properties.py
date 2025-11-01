# TODO Verify.

from typing import Union, TypeGuard

from src.isa.instructions import *

Instruction_with_rs1 = Union[
    Reg_reg, Reg_imm, Load, Store, Branch, Misc_mem, Atomic, Zicsr_reg_reg
]

Instruction_with_rs2 = Union[Reg_reg, Store, Branch, Atomic]

Instruction_with_rd = Union[
    Reg_reg,
    Reg_imm,
    Load,
    Upper_imm,
    Jal,
    Misc_mem,
    Atomic,
    Zicsr_reg_reg,
    Zicsr_reg_imm,
]

Instruction_with_imm = Union[
    Reg_imm, Load, Store, Branch, Upper_imm, Jal, Zicsr_reg_imm
]


def has_rs1(inst: Instruction) -> TypeGuard[Instruction_with_rs1]:
    return isinstance(
        inst, (Reg_reg, Reg_imm, Load, Store, Branch, Misc_mem, Atomic, Zicsr_reg_reg)
    )


def has_rs2(inst: Instruction) -> TypeGuard[Instruction_with_rs2]:
    return isinstance(inst, (Reg_reg, Store, Branch, Atomic))


def has_rd(inst: Instruction) -> TypeGuard[Instruction_with_rd]:
    return isinstance(
        inst,
        (
            Reg_reg,
            Reg_imm,
            Load,
            Upper_imm,
            Jal,
            Misc_mem,
            Atomic,
            Zicsr_reg_reg,
            Zicsr_reg_imm,
        ),
    )


def has_imm(inst: Instruction) -> TypeGuard[Instruction_with_imm]:
    return isinstance(
        inst, (Reg_imm, Load, Store, Branch, Upper_imm, Jal, Zicsr_reg_imm)
    )


def modifies_pc(inst: Instruction) -> bool:
    return isinstance(inst, (Branch, Jal, Jalr))
