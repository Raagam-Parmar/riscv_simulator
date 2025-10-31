"""
# RISC-V Instruction Encoding-Decoding Tables
Lookup tables mapping instruction bit patterns to operation enumerations.
"""

from typing import Dict, Tuple

from .enums import *

type funct3 = int
type funct5 = int
type funct7 = int
type opcode = int
type mmconst = int
type const = int
type csr = int


# ============================================================================
# R-Type: Register Operations
# ============================================================================
# Maps (funct3, funct7) pairs to register-register operations
#
#  31        25 24    20 19    15 14    12 11     7 6       0
# +-----------+--------+--------+--------+--------+----------+
# |  funct7   |  rs2   |  rs1   | funct3 |   rd   | 0110011  |
# +-----------+--------+--------+--------+--------+----------+
op_tbl: Dict[Tuple[funct3, funct7], Reg_ops] = {
    # RV32-I
    (0b000, 0b0000000): Reg_ops.ADD,
    (0b000, 0b0100000): Reg_ops.SUB,
    (0b001, 0b0000000): Reg_ops.SLL,
    (0b010, 0b0000000): Reg_ops.SLT,
    (0b011, 0b0000000): Reg_ops.SLTU,
    (0b100, 0b0000000): Reg_ops.XOR,
    (0b101, 0b0000000): Reg_ops.SRL,
    (0b101, 0b0100000): Reg_ops.SRA,
    (0b110, 0b0000000): Reg_ops.OR,
    (0b111, 0b0000000): Reg_ops.AND,
    # RV32-M
    (0b000, 0b0000001): Reg_ops.MUL,
    (0b001, 0b0000001): Reg_ops.MULH,
    (0b010, 0b0000001): Reg_ops.MULHSU,
    (0b011, 0b0000001): Reg_ops.MULHU,
    (0b100, 0b0000001): Reg_ops.DIV,
    (0b101, 0b0000001): Reg_ops.DIVU,
    (0b110, 0b0000001): Reg_ops.REM,
    (0b111, 0b0000001): Reg_ops.REMU,
}


# Imm instruction
# Base ISA Immediate Operations and JALR
# +-------------------+------+---------+------------+-----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  opcode   |
# +-------------------+------+---------+------------+-----------+
op_imm_f3_tbl: Dict[funct3, Imm_ops] = {
    0b000: Imm_ops.ADDI,
    0b010: Imm_ops.SLTI,
    0b011: Imm_ops.SLTIU,
    0b100: Imm_ops.XORI,
    0b110: Imm_ops.ORI,
    0b111: Imm_ops.ANDI,
}

op_imm_f3_f7_tbl: Dict[Tuple[funct3, funct7], Imm_ops] = {
    (0b001, 0b0000000): Imm_ops.SLLI,
    (0b101, 0b0000000): Imm_ops.SRLI,
    (0b101, 0b0100000): Imm_ops.SRAI,
}


# Load instruction
#  Base ISA Load operations
# +-------------------+------+---------+------------+-----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  0000011  |
# +-------------------+------+---------+------------+-----------+
load_tbl: Dict[funct3, Load_ops] = {
    0b000: Load_ops.LB,
    0b001: Load_ops.LH,
    0b010: Load_ops.LW,
    0b100: Load_ops.LBU,
    0b101: Load_ops.LHU,
}

# Store instruction
#  Base ISA store operations
# +------------+------+------+---------+------------+-----------+
# | imm[11:5]  | rs2  | rs1  | funct3  |  imm[4:0]  |  0100011  |
# +------------+------+------+---------+------------+-----------+
store_tbl: Dict[funct3, Store_ops] = {
    0b000: Store_ops.SB,
    0b001: Store_ops.SH,
    0b010: Store_ops.SW,
}

# Branch instruction
# Base ISA branch operations
# +---------------+------+------+---------+---------------+-----------+
# | imm[12|10:5]  | rs2  | rs1  | funct3  |  imm[4:1|11]  |  1100011  |
# +---------------+------+------+---------+---------------+-----------+
branch_tbl: Dict[funct3, Branch_ops] = {
    0b000: Branch_ops.BEQ,
    0b001: Branch_ops.BNE,
    0b100: Branch_ops.BLT,
    0b101: Branch_ops.BGE,
    0b110: Branch_ops.BLTU,
    0b111: Branch_ops.BGEU,
}

# Misc Mem instruction
# Base ISA Misc Mem Instructions (FENCE, FENCE.TSO, PAUSE)
# +--------+---------+--------+-------+-------+------+-----------+
# |   fm   |  pred   | succ   |  rs1  |  000  |  rd  |  0001111  |
# +--------+---------+--------+-------+-------+------+-----------+
misc_mem_tbl: Dict[mmconst, Misc_mem_ops] = {
    0x0020000: Misc_mem_ops.PAUSE,
    0x1066000: Misc_mem_ops.FENCE_TSO,
}

# Atomic instruction
# Atomic Extension (R-type instructions)
# +--------+----+----+-------+------+---------+------------+-----------+
# | funct5 | aq | rl |  rs2  | rs1  |  010    |  rd        |  0101111  |
# +--------+----+----+-------+------+---------+------------+-----------+
amo_tbl: Dict[funct5, Atomic_ops] = {
    0b00010: Atomic_ops.LR_W,
    0b00011: Atomic_ops.SC_W,
    0b00001: Atomic_ops.AMOSWAP_W,
    0b00000: Atomic_ops.AMOADD_W,
    0b00100: Atomic_ops.AMOXOR_W,
    0b01100: Atomic_ops.AMOAND_W,
    0b01000: Atomic_ops.AMOOR_W,
    0b10000: Atomic_ops.AMOMIN_W,
    0b10100: Atomic_ops.AMOMAX_W,
    0b11000: Atomic_ops.AMOMINU_W,
    0b11100: Atomic_ops.AMOMAXU_W,
}


# Environment instruction
# Base ISA System Instructions (ECALL, EBREAK)
# Some of Priviledged ISA instructions (SRET, MRET, MNRET, WFI)
# +-----------------+--------+-------+----------+----------+-----------+
# |   funct7        |  rs2   |  rs1  |  funct3  |  rd      |  1110011  |
# +-----------------+--------+-------+----------+----------+-----------+
system_tbl: Dict[const, System_ops] = {
    0x0000: System_ops.ECALL,
    0x2000: System_ops.EBREAK,
    # RV32 Priviledged ISA
    0x204000: System_ops.SRET,
    0x604000: System_ops.MRET,
    0xE04000: System_ops.MNRET,
    0x20A000: System_ops.WFI,
}


# Zicsr instruction
# Zicsr Extension (R-type instructions)
# +--------------------------+-------+----------+----------+-----------+
# |            csr           | rs1   |  funct3  |  rd      |  1110011  |
# +--------------------------+-------+----------+----------+-----------+
zicsr_tbl: Dict[funct3, Zicsr_ops] = {
    0b001: Zicsr_ops.CSRRW,
    0b010: Zicsr_ops.CSRRS,
    0b011: Zicsr_ops.CSRRC,
}

# Zicsr Immediate instruction
# Zicsr Extension (I-type instructions)
# +--------------------------+-------+----------+----------+-----------+
# |            csr           | uimm  |  funct3  |  rd      |  1110011  |
# +--------------------------+-------+----------+----------+-----------+
zicsr_imm_tbl: Dict[funct3, Zicsr_imm_ops] = {
    0b101: Zicsr_imm_ops.CSRRWI,
    0b110: Zicsr_imm_ops.CSRRSI,
    0b111: Zicsr_imm_ops.CSRRCI,
}
