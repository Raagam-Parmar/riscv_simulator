# TODO Verify.

from typing import Union, TypeGuard

from src.isa.instructions import *


class UnimplementedExecution(Exception):
    def __init__(self, inst: Instruction):
        self.message = f"Execution of instruction '{inst}' is not implemented."
        super().__init__(self.message)


Instruction_with_rs1 = Union[
    Reg_reg, Reg_imm, Load, Store, Branch, Misc_mem, Atomic, Zicsr_reg_reg, Jalr
]
"""
Instructions which have an `rs1` field
"""

Instruction_with_rs2 = Union[Reg_reg, Store, Branch, Atomic]
"""
Instructions which have an `rs2` field
"""


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
"""
Instructions which have an `rd` field
"""


Instruction_with_imm = Union[
    Reg_imm, Load, Store, Branch, Upper_imm, Jal, Zicsr_reg_imm
]
"""
Instructions which have an `imm` field
"""


Exec_Unimpl = Union[Misc_mem | Atomic | Env | Zicsr_reg_imm | Zicsr_reg_reg]
"""
Instructions whose execution is unimplemented
"""

Exec_Impl = Union[Reg_reg, Reg_imm, Jalr, Load, Store, Branch, Upper_imm, Jal]
"""
Instructions whose execution is implemented
"""


Inst_modifies_pc = Union[Branch, Jal, Jalr]
"""
Instructions which modify the control flow
"""

Inst_not_modifies_pc = Union[
    Reg_reg,
    Reg_imm,
    Load,
    Store,
    Upper_imm,
    Misc_mem,
    Atomic,
    Env,
    Zicsr_reg_imm,
    Zicsr_reg_reg,
]
"""
Instructions which do not modify the control flow
"""


def has_rs1(inst: Instruction) -> TypeGuard[Instruction_with_rs1]:
    """
    Does the instruction have an `rs1` field?
    """
    return isinstance(inst, Instruction_with_rs1)


def has_rs2(inst: Instruction) -> TypeGuard[Instruction_with_rs2]:
    """
    Does the instruction have an `rs2` field?
    """
    return isinstance(inst, Instruction_with_rs2)


def has_rd(inst: Instruction) -> TypeGuard[Instruction_with_rd]:
    """
    Does the instruction have an `rd` field?
    """
    return isinstance(inst, Instruction_with_rd)


def has_imm(inst: Instruction) -> TypeGuard[Instruction_with_imm]:
    """
    Does the instruction have an `imm` field?
    """
    return isinstance(inst, Instruction_with_imm)


def modifies_pc(inst: Instruction) -> TypeGuard[Inst_modifies_pc]:
    """
    Does the instruction modify the control flow?
    """
    return isinstance(inst, Inst_modifies_pc)


def not_modifies_pc(inst: Instruction) -> TypeGuard[Inst_not_modifies_pc]:
    """
    Does the instruction not modify the control flow?
    """
    return isinstance(inst, Inst_not_modifies_pc)


def is_unimplemented(inst: Instruction) -> TypeGuard[Exec_Unimpl]:
    """
    Is the instruction not implemented for execution?
    """
    return isinstance(inst, Exec_Unimpl)


def is_implemented(inst: Instruction) -> TypeGuard[Exec_Impl]:
    """
    Is the instruction implemented for execution?
    """
    return isinstance(inst, Exec_Impl)
