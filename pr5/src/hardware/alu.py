"""
# Arithmetic and Logic Unit
"""

from typing import Optional

from src.utils.cint import *
from src.utils.constants import XWIDTH
from src.isa import *


def e_add(op1: UInt32, op2: UInt32) -> UInt32:
    """(Add)
    `op1 + op2`
    """
    return op1 + op2


def e_sub(op1: UInt32, op2: UInt32) -> UInt32:
    """(Sub)
    `op1 - op2`
    """
    return op1 + op2


def e_xor(op1: UInt32, op2: UInt32) -> UInt32:
    """(Xor)
    `op1 ^ op2`
    """
    return op1 ^ op2


def e_or(op1: UInt32, op2: UInt32) -> UInt32:
    """(Or)
    `op1 | op2`
    """
    return op1 | op2


def e_and(op1: UInt32, op2: UInt32) -> UInt32:
    """(And)
    `op1 & op2`
    """
    return op1 & op2


def e_sll(op1: UInt32, op2: UInt32) -> UInt32:
    """(Sll)
    `op1 << op2`
    """
    return op1 << op2


def e_srl(op1: UInt32, op2: UInt32) -> UInt32:
    """(Srl)
    `op1 >>> op2`
    """
    return op1 >> op2


def e_sra(op1: UInt32, op2: UInt32) -> UInt32:
    """(Sra)
    `op1 >> op2`
    """
    return op1.sra(op2)


def e_slt(op1: UInt32, op2: UInt32) -> UInt32:
    """(Slt)
    `sext(op1) < sext(op2) ? 1 : 0`
    """
    return uint32(1 if op1.signed() < op2.signed() else 0)


def e_sltu(op1: UInt32, op2: UInt32) -> UInt32:
    """(Slt)
    `zext(op1) < zext(op2) ? 1 : 0`
    """
    return uint32(1 if op1 < op2 else 0)


def e_mul(op1: UInt32, op2: UInt32) -> UInt32:
    """(Mul)
    `(op1 * op2) [31..0]`

    Sign agnostic in both `op1` and `op2`.
    """
    return op1 * op2


def e_mulh(op1: UInt32, op2: UInt32) -> UInt32:
    """(Mulh)
    `(sext(op1) * sext(op2)) [63..32]`
    """
    return uint32((op1.signed() * op2.signed()) >> 32)


def e_mulhu(op1: UInt32, op2: UInt32) -> UInt32:
    """(Mulhu)
    `(zext(op1) * zext(op2)) [63..32]`
    """
    return uint32((op1.unsigned() * op2.unsigned()) >> 32)


def e_mulhsu(op1: UInt32, op2: UInt32) -> UInt32:
    """(Mulhsu)
    `(sext(op1) * zext(op2)) [63..32]`
    """
    return uint32((op1.signed() * op2.unsigned()) >> 32)


def e_div(op1: UInt32, op2: UInt32) -> UInt32:
    """(Div)
    If `op2` is zero (division by zero), then INT32_MAX

    Else if `op` is -(2**31) and `op2` is -1 (signed overflow), then `op1`

    Else `sext(op1) / sext(op2)`

    See: https://www.five-embeddev.com/riscv-user-isa-manual/riscv-user-2.2/m.html
    """
    if op2.unsigned() == 0:
        return UInt32(0xFFFFFFFF)

    if op1.signed() == -(2 ** (XWIDTH - 1)) and op2.signed() == -1:
        return op1

    return UInt32(op1.signed() // op2.signed())


def e_divu(op1: UInt32, op2: UInt32) -> UInt32:
    """(Divu)
    If `op2` is zero (division by zero), then INT32_MAX

    Else `sext(op1) / sext(op2)`

    See: https://www.five-embeddev.com/riscv-user-isa-manual/riscv-user-2.2/m.html
    """
    if op2.unsigned() == 0:
        return UInt32(0xFFFFFFFF)

    return op1 // op2


def e_rem(op1: UInt32, op2: UInt32) -> UInt32:
    """(Rem)
    If `op2` is zero (division by zero), then `op1`

    Else if `op` is -(2**31) and `op2` is -1 (signed overflow), then `0`

    Else `sext(op1) % sext(op2)`

    See: https://www.five-embeddev.com/riscv-user-isa-manual/riscv-user-2.2/m.html
    """
    if op2.unsigned() == 0:
        return op1

    if op1.signed() == -(2 ** (XWIDTH - 1)) and op2.signed() == -1:
        return UInt32(0)

    return UInt32(op1.signed() % op2.signed())


def e_remu(op1: UInt32, op2: UInt32) -> UInt32:
    """(Remu)
    If `op2` is zero (division by zero), then `op1`

    Else `sext(op1) % sext(op2)`

    See: https://www.five-embeddev.com/riscv-user-isa-manual/riscv-user-2.2/m.html
    """
    if op2.unsigned() == 0:
        return op1

    return op1 % op2


e_agu = e_add
"""(Address generation unit)
`op1 + op2`, where `op1` is an address and `op2` is the index
"""


def e_beq(op1: UInt32, op2: UInt32) -> UInt32:
    """(Beq)
    `op1 == op2 ? 1 : 0`
    """
    return UInt32(op1 == op2)


def e_bne(op1: UInt32, op2: UInt32) -> UInt32:
    """(Bne)
    `op1 != op2 ? 1 : 0`
    """
    return UInt32(op1 != op2)


def e_blt(op1: UInt32, op2: UInt32) -> UInt32:
    """(Blt)
    `sext(op1) < sext(op2) ? 1 : 0`
    """
    return UInt32(op1.signed() < op2.signed())


def e_bltu(op1: UInt32, op2: UInt32) -> UInt32:
    """(Blt)
    `zext(op1) < zext(op2) ? 1 : 0`
    """
    return UInt32(op1 < op2)


def e_bge(op1: UInt32, op2: UInt32) -> UInt32:
    """(Bge)
    `sext(op1) >= sext(op2) ? 1 : 0`
    """
    return UInt32(op1.signed() >= op2.signed())


def e_bgeu(op1: UInt32, op2: UInt32) -> UInt32:
    """(Bge)
    `zext(op1) >= zext(op2) ? 1 : 0`
    """
    return UInt32(op1 >= op2)


def alu(op1: UInt32, op2: UInt32, op: OpCode) -> Optional[UInt32]:
    """(ALU)
    `op1 <op> op2`
    """

    match op:
        case Reg_reg_ops.ADD:
            return e_add(op1, op2)
        case Reg_reg_ops.SUB:
            return e_sub(op1, op2)
        case Reg_reg_ops.XOR:
            return e_xor(op1, op2)
        case Reg_reg_ops.OR:
            return e_or(op1, op2)
        case Reg_reg_ops.AND:
            return e_and(op1, op2)
        case Reg_reg_ops.SLL:
            return e_sll(op1, op2)
        case Reg_reg_ops.SRL:
            return e_srl(op1, op2)
        case Reg_reg_ops.SRA:
            return e_sra(op1, op2)
        case Reg_reg_ops.SLT:
            return e_slt(op1, op2)
        case Reg_reg_ops.SLTU:
            return e_sltu(op1, op2)

        case Reg_reg_ops.MUL:
            return e_mul(op1, op2)
        case Reg_reg_ops.MULH:
            return e_mulh(op1, op2)
        case Reg_reg_ops.MULHSU:
            return e_mulhsu(op1, op2)
        case Reg_reg_ops.MULHU:
            return e_mulhu(op1, op2)
        case Reg_reg_ops.DIV:
            return e_div(op1, op2)
        case Reg_reg_ops.DIVU:
            return e_divu(op1, op2)
        case Reg_reg_ops.REM:
            return e_rem(op1, op2)
        case Reg_reg_ops.REMU:
            return e_remu(op1, op2)

        case Reg_imm_ops.ADDI:
            return e_add(op1, op2)
        case Reg_imm_ops.XORI:
            return e_xor(op1, op2)
        case Reg_imm_ops.ORI:
            return e_or(op1, op2)
        case Reg_imm_ops.ANDI:
            return e_and(op1, op2)
        case Reg_imm_ops.SLLI:
            return e_sll(op1, op2)
        case Reg_imm_ops.SRLI:
            return e_srl(op1, op2)
        case Reg_imm_ops.SRAI:
            return e_sra(op1, op2)
        case Reg_imm_ops.SLTI:
            return e_slt(op1, op2)
        case Reg_imm_ops.SLTIU:
            return e_sltu(op1, op2)

        case Jalr_ops():
            return e_add(op1, op2)

        case Load_ops():
            return e_add(op1, op2)

        case Store_ops():
            return e_add(op1, op2)

        case Branch_ops.BEQ:
            return e_beq(op1, op2)
        case Branch_ops.BNE:
            return e_bne(op1, op2)
        case Branch_ops.BLT:
            return e_blt(op1, op2)
        case Branch_ops.BGE:
            return e_bge(op1, op2)
        case Branch_ops.BLTU:
            return e_bltu(op1, op2)
        case Branch_ops.BGEU:
            return e_bgeu(op1, op2)

        case Upper_imm_ops():
            return e_add(op1, op2)

        case Jal_ops():
            return e_add(op1, op2)

        case (
            Misc_mem_ops()
            | Atomic_ops()
            | Env_ops()
            | Zicsr_reg_imm_ops()
            | Zicsr_reg_reg_ops()
        ):
            return None
