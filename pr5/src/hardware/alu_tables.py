from typing import Dict, Callable, Tuple

from src.isa.opcodes import *
from src.isa.instructions import *
from src.hardware.fu import *

OperandFunc = Callable[[int, int, int, int], Tuple[int, int]]

operands_tbl: Dict[OpCode, OperandFunc] = {
    # Reg instruction
    Reg_reg_ops.ADD: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.SUB: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, -1 * v_rs2),
    Reg_reg_ops.XOR: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.OR: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.AND: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.SLL: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.SRL: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.SRA: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.SLT: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.SLTU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.MUL: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.MULH: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.MULHSU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.MULHU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.DIV: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.DIVU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.REM: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_reg_ops.REMU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    # Imm instruction
    Reg_imm_ops.ADDI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Reg_imm_ops.XORI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Reg_imm_ops.ORI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Reg_imm_ops.ANDI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Reg_imm_ops.SLLI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Reg_imm_ops.SRLI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Reg_imm_ops.SRAI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Reg_imm_ops.SLTI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Reg_imm_ops.SLTIU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    # JALR Instruction
    Jalr_ops.JALR: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    # Load instruction
    Load_ops.LB: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Load_ops.LH: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Load_ops.LW: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Load_ops.LBU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Load_ops.LHU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    # Store instruction
    Store_ops.SB: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Store_ops.SH: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Store_ops.SW: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    # Branch instruction
    Branch_ops.BEQ: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Branch_ops.BNE: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Branch_ops.BLT: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Branch_ops.BGE: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Branch_ops.BLTU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Branch_ops.BGEU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    # Upper-Immediate instruction
    Upper_imm_ops.LUI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_imm, 12),
    Upper_imm_ops.AUIPC: lambda v_rs1, v_rs2, v_imm, v_pc: (v_pc, v_imm),
    # Jump instruction
    Jal_ops.JAL: lambda v_rs1, v_rs2, v_imm, v_pc: (v_pc, v_imm),
    # TODO Misc Mem instruction
    # TODO Atomic instruction
    # Environment instruction
    System_ops.ECALL: lambda v_rs1, v_rs2, v_imm, v_pc: (0, 0),  # NOTE: Unimplemented
    System_ops.EBREAK: lambda v_rs1, v_rs2, v_imm, v_pc: (0, 0),  # NOTE: Unimplemented
    # TODO Zicsr instruction
    # TODO Zicsr Immediate instruction
}


function_tbl: Dict[OpCode, ExecFunc] = {
    # Reg instruction
    Reg_reg_ops.ADD: e_add,
    Reg_reg_ops.SUB: e_add,
    Reg_reg_ops.XOR: e_xor,
    Reg_reg_ops.OR: e_or,
    Reg_reg_ops.AND: e_and,
    Reg_reg_ops.SLL: e_sll,
    Reg_reg_ops.SRL: e_srl,
    Reg_reg_ops.SRA: e_sra,
    Reg_reg_ops.SLT: e_slt,
    Reg_reg_ops.SLTU: e_slt,
    Reg_reg_ops.MUL: e_mul,
    Reg_reg_ops.MULH: e_mulh,
    Reg_reg_ops.MULHSU: e_mulh,
    Reg_reg_ops.MULHU: e_mulh,
    Reg_reg_ops.DIV: e_div,
    Reg_reg_ops.DIVU: e_div,
    Reg_reg_ops.REM: e_rem,
    Reg_reg_ops.REMU: e_rem,
    # Imm instruction
    Reg_imm_ops.ADDI: e_add,
    Reg_imm_ops.XORI: e_xor,
    Reg_imm_ops.ORI: e_or,
    Reg_imm_ops.ANDI: e_and,
    Reg_imm_ops.SLLI: e_sll,
    Reg_imm_ops.SRLI: e_srl,
    Reg_imm_ops.SRAI: e_sra,
    Reg_imm_ops.SLTI: e_slt,
    Reg_imm_ops.SLTIU: e_slt,
    Jalr_ops.JALR: e_add,  # NOTE: Modified
    # Load instruction
    Load_ops.LB: e_agu,
    Load_ops.LH: e_agu,
    Load_ops.LW: e_agu,
    Load_ops.LBU: e_agu,
    Load_ops.LHU: e_agu,
    # Store instruction
    Store_ops.SB: e_agu,
    Store_ops.SH: e_agu,
    Store_ops.SW: e_agu,
    # Branch instruction
    Branch_ops.BEQ: e_beq,
    Branch_ops.BNE: e_bne,
    Branch_ops.BLT: e_blt,
    Branch_ops.BGE: e_bge,
    Branch_ops.BLTU: e_blt,
    Branch_ops.BGEU: e_bge,
    # Upper-Immediate instruction
    Upper_imm_ops.LUI: e_sll,
    Upper_imm_ops.AUIPC: e_auipc,
    # Jump instruction
    Jal_ops.JAL: e_add,  # NOTE: Modified
    # TODO Misc Mem instruction
    # TODO Atomic instruction
    # Environment instruction
    System_ops.ECALL: e_nop,
    System_ops.EBREAK: e_nop,
    # TODO Zicsr instruction
    # TODO Zicsr Immediate instruction
}
