from typing import Dict, Callable, Tuple

from isa.enums import *
from isa.formats import *
from .fu import *

def is_unimplemented(instr: int):
    masked_inst = (instr & 0xF0000) >> 16
    if masked_inst == 0x7:
        return True
    else:
        return False

OperandFunc = Callable[
    [int, int, int, int],
    Tuple[int, int]
]

operands_tbl : Dict[OpCode, OperandFunc] = {
    # Reg instruction
    Reg_ops.ADD: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.SUB: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, -1 * v_rs2),
    Reg_ops.XOR: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.OR: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.AND: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.SLL: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.SRL: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.SRA: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.SLT: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.SLTU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_rs2)),
    
    Reg_ops.MUL: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.MULH: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.MULHSU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_rs2)),
    Reg_ops.MULHU: lambda v_rs1, v_rs2, v_imm, v_pc: (to_unsigned(v_rs1), to_unsigned(v_rs2)),
    Reg_ops.DIV: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.DIVU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_rs2)),
    Reg_ops.REM: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Reg_ops.REMU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_rs2)),
    
    # Imm instruction
    Imm_ops.ADDI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Imm_ops.XORI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Imm_ops.ORI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Imm_ops.ANDI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Imm_ops.SLLI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Imm_ops.SRLI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Imm_ops.SRAI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Imm_ops.SLTI: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Imm_ops.SLTIU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_imm)),
    Imm_ops.JALR: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm), # NOTE: Modified
    
    # Load instruction
    Load_ops.LB: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Load_ops.LH: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Load_ops.LW: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Load_ops.LBU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_imm)),
    Load_ops.LHU: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_imm)),
    
    # Store instruction
    Store_ops.SB: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Store_ops.SH: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    Store_ops.SW: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),
    
    # Branch instruction
    Branch_ops.BEQ: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Branch_ops.BNE: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Branch_ops.BLT: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Branch_ops.BGE: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),
    Branch_ops.BLTU: lambda v_rs1, v_rs2, v_imm, v_pc: (to_unsigned(v_rs1), to_unsigned(v_rs2)),
    Branch_ops.BGEU: lambda v_rs1, v_rs2, v_imm, v_pc: (to_unsigned(v_rs1), to_unsigned(v_rs2)),
    
    # Upper-Immediate instruction
    Upper_ops.LUI: lambda v_rs1, v_rs2, v_imm, v_pc: (0, v_imm << 12), # NOTE: Modified
    Upper_ops.AUIPC: lambda v_rs1, v_rs2, v_imm, v_pc: (v_pc, v_imm),

    # Jump instruction
    Jump_ops.JAL: lambda v_rs1, v_rs2, v_imm, v_pc: (v_pc, v_imm), # NOTE: Modified
    
    # TODO Misc Mem instruction
    # TODO Atomic instruction
    
    # Environment instruction
    System_ops.ECALL: lambda v_rs1, v_rs2, v_imm, v_pc: (0, 0), # NOTE: Unimplemented
    System_ops.EBREAK: lambda v_rs1, v_rs2, v_imm, v_pc: (0, 0), # NOTE: Unimplemented
    
    # TODO Zicsr instruction
    # TODO Zicsr Immediate instruction
}


function_tbl : Dict[OpCode, ExecFunc] = {
    # Reg instruction
    Reg_ops.ADD: e_add,
    Reg_ops.SUB: e_add,
    Reg_ops.XOR: e_xor,
    Reg_ops.OR: e_or,
    Reg_ops.AND: e_and,
    Reg_ops.SLL: e_sll,
    Reg_ops.SRL: e_srl,
    Reg_ops.SRA: e_sra,
    Reg_ops.SLT: e_slt,
    Reg_ops.SLTU: e_slt,
    
    Reg_ops.MUL: e_mul,
    Reg_ops.MULH: e_mulh,
    Reg_ops.MULHSU: e_mulh,
    Reg_ops.MULHU: e_mulh,
    Reg_ops.DIV: e_div,
    Reg_ops.DIVU: e_div,
    Reg_ops.REM: e_rem,
    Reg_ops.REMU: e_rem,
    
    # Imm instruction
    Imm_ops.ADDI: e_add,
    Imm_ops.XORI: e_xor,
    Imm_ops.ORI: e_or,
    Imm_ops.ANDI: e_and,
    Imm_ops.SLLI: e_sll,
    Imm_ops.SRLI: e_srl,
    Imm_ops.SRAI: e_sra,
    Imm_ops.SLTI: e_slt,
    Imm_ops.SLTIU: e_slt,
    Imm_ops.JALR: e_add, # NOTE: Modified
    
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
    Upper_ops.LUI: e_sll,
    Upper_ops.AUIPC: e_auipc,

    # Jump instruction
    Jump_ops.JAL: e_add, # NOTE: Modified
    
    # TODO Misc Mem instruction
    # TODO Atomic instruction
    
    # Environment instruction
    System_ops.ECALL: e_nop,
    System_ops.EBREAK: e_nop
    
    # TODO Zicsr instruction
    # TODO Zicsr Immediate instruction
}
