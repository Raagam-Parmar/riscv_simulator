from dataclasses import dataclass
from enum import Enum, auto

# RISC-V Unpriviledged ISA, Page 608
# RV32I Instruction Set Listings 
# 
# inst[1:0] = 11
# 
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
# | inst[4:2] |   000   |   001   |   010   |   011    |   100   |   101   |   110   |   111   |
# | inst[6:5] |         |         |         |          |         |         |         |         |
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
# |        00 |  LOAD   |         |         | MISC-MEM |  OP-IMM |  AUIPC  |         |         |
# |        01 |  STORE  |         |         |   AMO    |  OP     |  LUI    |         |         |
# |        10 |         |         |         |          |         |         |         |         |
# |        11 |  BRANCH |  JALR   |         |  JAL     |  SYSTEM |         |         |         |
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
# 
# The blank fields are illegal instructions in RV32-IMA


class R_ops(Enum):
    # RV32-I
    ADD  = auto()
    SUB  = auto()
    XOR  = auto()
    OR   = auto()
    AND  = auto()
    SLL  = auto()
    SRL  = auto()
    SRA  = auto()
    SLT  = auto()
    SLTU = auto()
    
    # RV32-M
    MUL   = auto()
    MULH  = auto()
    MULSU = auto()
    MULU  = auto() 
    DIV   = auto()
    DIVU  = auto() 
    REM   = auto()
    REMU  = auto() 
    
    # RV32-A
    LR_W      = auto()
    SC_W      = auto()
    AMOSWAP_W = auto()
    AMOADD_W  = auto()
    AMOAND_W  = auto()
    AMOOR_W   = auto()
    AMOXOR_W  = auto()
    AMOMAX_W  = auto()
    AMOMIN_W  = auto()
    
    def __repr__(self):
        return f"R-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower().replace('_', '.')


class I_ops(Enum):
    # RV32-I
    ADDI  = auto()
    XORI  = auto()
    ORI   = auto()
    ANDI  = auto()
    SLLI  = auto()
    SRLI  = auto()
    SRAI  = auto()
    SLTI  = auto()
    SLTIU = auto()
    
    LB  = auto()
    LH  = auto()
    LW  = auto()
    LBU = auto()
    LHU = auto()
    
    JALR = auto()
    
    ECALL  = auto()
    EBREAK = auto()
    
    def __repr__(self):
        return f"I-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower()


class S_ops(Enum):
    # RV32-I
    SB = auto()
    SH = auto()
    SW = auto()
    
    def __repr__(self):
        return f"S-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower()


class B_ops(Enum):
    # RV32-I
    BEQ  = auto()
    BNE  = auto()
    BLT  = auto()
    BGE  = auto()
    BLTU = auto()
    BGEU = auto()
    
    def __repr__(self):
        return f"B-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower()


class U_ops(Enum):
    # RV32-I
    LUI = auto()
    AUIPC = auto()
        
    def __repr__(self):
        return f"U-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower()


class J_ops(Enum):
    # RV32-I
    JAL = auto()
    
    def __repr__(self):
        return f"J-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower()


# R type instruction
# +-----------+-------+------+---------+------------+----------+
# | funct7    | rs2   | rs1  | funct3  |  rd        |  opcode  |
# +-----------+-------+------+---------+------------+----------+
@dataclass
class R:
    op : R_ops
    rd : int
    rs1: int
    rs2: int
    # funct7 : int
    # rs2    : int
    # rs1    : int
    # funct3 : int
    # rd     : int
    # opcode : R_ops    


# I type instruction
# +-------------------+------+---------+------------+----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  opcode  |
# +-------------------+------+---------+------------+----------+
@dataclass
class I:
    op : I_ops
    rd : int
    rs1: int
    imm: int
    # opcode  : int
    # rd      : int
    # funct3  : int
    # rs1     : int
    # imm11_0 : int


# S type instruction
# +------------+------+------+---------+------------+----------+
# | imm[11:5]  | rs2  | rs1  | funct3  |  imm[4:0]  |  opcode  |
# +------------+------+------+---------+------------+----------+
@dataclass
class S:
    op : S_ops
    rs1: int
    rs2: int
    imm: int
    # opcode  : int
    # imm4_0  : int 
    # funct3  : int
    # rs1     : int
    # rs2     : int
    # imm11_5 : int


# B type instruction
# +---------------+------+------+---------+---------------+----------+
# | imm[12|10:5]  | rs2  | rs1  | funct3  |  imm[4:1|11]  |  opcode  |
# +---------------+------+------+---------+---------------+----------+
@dataclass
class B:
    op : B_ops
    rs1: int
    rs2: int
    imm: int
    # opcode     : int
    # imm4_1_11  : int
    # funct3     : int
    # rs1        : int
    # rs2        : int
    # imm12_10_5 : int


# U type instruction
# +------------------------------------+------------+----------+
# |            imm[31:12]              |  rd        |  opcode  |
# +------------------------------------+------------+----------+
@dataclass
class U:
    op : U_ops
    rd : int
    imm: int


# J type instruction
# +------------------------------------+------------+----------+
# |       imm[20|10:1|11|19:12]        |  rd        |  opcode  |
# +------------------------------------+------------+----------+
@dataclass
class J:
    op : J_ops
    rd : int
    imm: int
