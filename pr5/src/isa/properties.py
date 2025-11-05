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


Inst_modifies_pc = Union[Branch, Jal, Jalr]
"""
Instructions which modify the control flow
"""


def has_rs1(inst: Instruction) -> TypeGuard[Instruction_with_rs1]:
    """
    Does the instruction have an `rs1` field?
    """
    return isinstance(
        inst,
        (Reg_reg, Reg_imm, Load, Store, Branch, Misc_mem, Atomic, Zicsr_reg_reg, Jalr),
    )


def has_rs2(inst: Instruction) -> TypeGuard[Instruction_with_rs2]:
    """
    Does the instruction have an `rs2` field?
    """
    return isinstance(inst, (Reg_reg, Store, Branch, Atomic))


def has_rd(inst: Instruction) -> TypeGuard[Instruction_with_rd]:
    """
    Does the instruction have an `rd` field?
    """
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
    """
    Does the instruction have an `imm` field?
    """
    return isinstance(
        inst, (Reg_imm, Load, Store, Branch, Upper_imm, Jal, Zicsr_reg_imm)
    )


def modifies_pc(inst: Instruction) -> TypeGuard[Inst_modifies_pc]:
    """
    Does the instruction modify the control flow?
    """
    return isinstance(inst, (Branch, Jal, Jalr))
