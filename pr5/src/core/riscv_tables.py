from .fu import *

def is_branch(instr :int):
    masked_inst = (instr & 0xFF000) >> 12
    if masked_inst == 0x63 :
        return True
    else:
        return False

def is_jump(instr : int):
    masked_inst = (instr & 0xFF000) >> 12
    if masked_inst == 0x6F or masked_inst == 0x67 :
        return True
    else:
        return False

def is_unimplemented(instr : int):
    masked_inst = (instr & 0xF0000) >> 16
    if masked_inst == 0x7:
        return True
    else:
        return False


def is_load(instr :int):
    masked_inst = (instr & 0xFF000) >> 12
    if masked_inst == 0x03:
        return True
    else:
        return False

def is_store(instr :int):
    masked_inst = (instr & 0xFF000) >> 12
    if masked_inst == 0x23:
        return True
    else:
        return False

alu_function = {
    0x33000: e_add,     # "add"
    0x33020: e_add,     # "sub"
    0x33400: e_xor,     # "xor"
    0x33600: e_or,      # "or"
    0x33700: e_and,     # "and"
    0x33100: e_sll,     # "sll"
    0x33500: e_srl,     # "srl"
    0x33520: e_sra,     # "sra"
    0x33200: e_slt,     # "slt"
    0x33300: e_slt,     # "sltu"
    0x13000: e_add,     # "addi"
    0x13400: e_xor,     # "xori"
    0x13600: e_or,      # "ori"
    0x13700: e_and,     # "andi"
    0x13100: e_sll,     # "slli"
    0x13500: e_srl,     # "srli"
    0x13520: e_sra,     # "srai"
    0x13200: e_slt,     # "slti"
    0x13300: e_slt,     # "sltiu"
    0x33001: e_mul,     # "mul"
    0x33101: e_mulh,    # "mulh"
    0x33201: e_mul,     # "mulsu"
    0x33301: e_mul,     # "mulu"
    0x33401: e_div,     # "div"
    0x33501: e_div,     # "divu"
    0x33601: e_rem,     # "rem"
    0x33701: e_rem,     # "remu"
    0x37000: e_sll,     # "lui"
    0x03000: e_agu,     # "lb"
    0x03100: e_agu,     # "lh"
    0x03200: e_agu,     # "lw"
    0x03400: e_agu,     # "lbu"
    0x03500: e_agu,     # "lhu"
    0x23000: e_agu,     # "sb"
    0x23100: e_agu,     # "sh"
    0x23200: e_agu,     # "sw"
    0x63000: e_beq,     # "beq"
    0x63100: e_bne,     # "bne"
    0x63400: e_blt,     # "blt"
    0x63500: e_bge,     # "bge"
    0x63600: e_blt,     # "bltu"
    0x63700: e_bge,     # "bgeu"
    0x6F000: None,      # "jal"    # TODO: Fix this entry (without changing fu.py)
    0x67000: None,      # "jalr"   # TODO: Fix this entry (without changing fu.py)
    0x17000: e_auipc,   # "auipc"
    0x73000: e_nop,     # "ecall"
    0x73001: e_nop      # "ebreak"
}

alu_operands = {
    0x33000: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "add"
    0x33020: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, -1 * v_rs2),          # "sub"
    0x33400: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "xor"
    0x33600: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "or"
    0x33700: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "and"
    0x33100: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "sll"
    0x33500: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "srl"
    0x33520: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "sra"
    0x33200: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "slt"
    0x33300: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_rs2)),  # "sltu"
    0x13000: lambda v_rs1, v_rs2, v_imm, v_pc: (None, None),                  # "addi"  # TODO: Fix this entry (without changing fu.py)
    0x13400: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "xori"
    0x13600: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "ori"
    0x13700: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "andi"
    0x13100: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "slli"
    0x13500: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "srli"
    0x13520: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "srai"
    0x13200: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "slti"
    0x13300: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_imm)),  # "sltiu"
    0x33001: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "mul"
    0x33101: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "mulh"
    0x33201: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_rs2)),  # "mulsu"
    0x33301: lambda v_rs1, v_rs2, v_imm, v_pc: (to_unsigned(v_rs1), to_unsigned(v_rs2)),  # "mulu"
    0x33401: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "div"
    0x33501: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_rs2)),  # "divu"
    0x33601: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "rem"
    0x33701: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_rs2)),  # "remu"
    0x37000: lambda v_rs1, v_rs2, v_imm, v_pc: (None, None),                 # "lui"     # TODO: Fix this entry (without changing fu.py)
    0x03000: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "lb"
    0x03100: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "lh"
    0x03200: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "lw"
    0x03400: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_imm)),  # "lbu"
    0x03500: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, to_unsigned(v_imm)),  # "lhu"
    0x23000: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "sb"
    0x23100: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "sh"
    0x23200: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_imm),               # "sw"
    0x63000: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "beq"
    0x63100: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "bne"
    0x63400: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "blt"
    0x63500: lambda v_rs1, v_rs2, v_imm, v_pc: (v_rs1, v_rs2),               # "bge"
    0x63600: lambda v_rs1, v_rs2, v_imm, v_pc: (to_unsigned(v_rs1), to_unsigned(v_rs2)),  # "bltu"
    0x63700: lambda v_rs1, v_rs2, v_imm, v_pc: (to_unsigned(v_rs1), to_unsigned(v_rs2)),  # "bgeu"
    0x6F000: lambda v_rs1, v_rs2, v_imm, v_pc: (None, None),                    # "jal"     # TODO: Fix this entry (without changing fu.py)
    0x67000: lambda v_rs1, v_rs2, v_imm, v_pc: (None, None),                    # "jalr"    # TODO: Fix this entry (without changing fu.py)
    0x17000: lambda v_rs1, v_rs2, v_imm, v_pc: (v_pc,  v_imm),               # "auipc"
    0x73000: lambda v_rs1, v_rs2, v_imm, v_pc: (None, None),                 # "ecall"      # NOTE: Unimplemented
    0x73001: lambda v_rs1, v_rs2, v_imm, v_pc: (None, None),                 # "ebreak"     # NOTE: Unimplemented
}
