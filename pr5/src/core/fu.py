from typing import Callable
from utils.bits import sign_extend
from utils.constants import XWIDTH


ExecFunc = Callable[[int, int], int]


# Functions to handle memory operations
def to_unsigned(num: int) -> int:
    return num & 0xFFFFFFFF


# ALU
e_add: ExecFunc = lambda op1, op2: op1 + op2
e_xor: ExecFunc = lambda op1, op2: op1 ^ op2
e_or: ExecFunc = lambda op1, op2: op1 | op2
e_and: ExecFunc = lambda op1, op2: op1 & op2
e_sll: ExecFunc = lambda op1, op2: op1 << op2  # NOTE: lui uses the same unit
e_srl: ExecFunc = lambda op1, op2: op1 >> op2
e_sra: ExecFunc = lambda op1, op2: (op1 + (1 << 32)) >> op2 if op1 < 0 else op1 >> op2
e_slt: ExecFunc = lambda op1, op2: 1 if op1 < op2 else 0
e_mul: ExecFunc = lambda op1, op2: sign_extend(op1 * op2, XWIDTH)
e_mulh: ExecFunc = lambda op1, op2: (op1 * op2) >> 32
e_div: ExecFunc = lambda op1, op2: op1 // op2
e_rem: ExecFunc = lambda op1, op2: op1 % op2

# AUIPC
e_auipc: ExecFunc = lambda op1, op2: op1 + (op2 << 12)

# AGU
e_agu: ExecFunc = lambda op1, op2: op1 + op2

# e_lb  = lambda op1, op2: lb(op1, op2)
# e_lh  = lambda op1, op2: lh(op1, op2)
# e_lw  = lambda op1, op2: lw(op1, op2)
# e_lbu = lambda op1, op2: lbu(op1, op2)
# e_lhu = lambda op1, op2: lhu(op1, op2)
# e_sb  = lambda op1, op2: sb(op1, op2)
# e_sh  = lambda op1, op2: sh(op1, op2)
# e_sw  = lambda op1, op2: sw(op1, op2)

# Comparator
e_beq: ExecFunc = lambda op1, op2: op1 == op2
e_bne: ExecFunc = lambda op1, op2: op1 != op2
e_blt: ExecFunc = lambda op1, op2: op1 < op2
e_bge: ExecFunc = lambda op1, op2: op1 >= op2

# NOP
e_nop: ExecFunc = lambda op1, op2: None
