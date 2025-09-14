from dataclasses import dataclass
from enum import Enum, auto

# See: https://github.com/riscv/riscv-isa-manual/releases/download/riscv-isa-release-82895c4-2025-09-11/riscv-unprivileged.pdf
# Reference last updated: 3 days ago
# 
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
# |        11 |  BRANCH |  JALR   |         |   JAL    |  SYSTEM |         |         |         |
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
# 
# The blank fields are illegal instructions in RV32-IMA

'''
misc-mem
system
'''


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
    MUL    = auto()
    MULH   = auto()
    MULHSU = auto()
    MULHU  = auto()
    DIV    = auto()
    DIVU   = auto() 
    REM    = auto()
    REMU   = auto()    
        
    def __repr__(self):
        return f"R-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower()


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


class M_ops(Enum):
    # RV32-I
    FENCE     = auto()
    FENCE_TSO = auto()
    PAUSE     = auto()
    
    def __repr__(self):
        return f"MM-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower().replace('_', '.')


class A_ops(Enum):
    # RV32-A
    LR_W      = auto()
    SC_W      = auto()
    AMOSWAP_W = auto()
    AMOADD_W  = auto()
    AMOXOR_W  = auto()
    AMOAND_W  = auto()
    AMOOR_W   = auto()
    AMOMIN_W  = auto()
    AMOMAX_W  = auto()
    AMOMINU_W  = auto()
    AMOMAXU_W  = auto()

    def __repr__(self):
        return f"A-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower().replace('_', '.')


class E_ops(Enum):
    # RV32-I
    ECALL  = auto()
    EBREAK = auto()
    
    def __repr__(self):
        return f"SYS-OP:{self.name}"
    
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
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \trs1:{self.rs1} \trs2:{self.rs2}"
    
    def __str__(self):
        return f"{self.op} x{self.rd}, x{self.rs1}, x{self.rs2}"


# I type instruction
# +-------------------+------+---------+------------+----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  opcode  |
# +-------------------+------+---------+------------+----------+
@dataclass
class I:
    op : I_ops
    rd : int
    rs1: int
    imm: int # -2048 <= imm <= 2047  (2**11 = 2048)
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \trs1:{self.rs1} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} x{self.rd}, x{self.rs1}, {self.imm}"


# S type instruction
# +------------+------+------+---------+------------+----------+
# | imm[11:5]  | rs2  | rs1  | funct3  |  imm[4:0]  |  opcode  |
# +------------+------+------+---------+------------+----------+
@dataclass
class S:
    op : S_ops
    rs1: int
    rs2: int
    imm: int # -2048 <= imm <= 2047   (2**11 = 2048)
    
    def __repr__(self):
        return f"Op:{self.op} \trs1:{self.rs1} \trs2:{self.rs2} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} x{self.rs2}, {self.imm}(x{self.rs1})"


# B type instruction
# +---------------+------+------+---------+---------------+----------+
# | imm[12|10:5]  | rs2  | rs1  | funct3  |  imm[4:1|11]  |  opcode  |
# +---------------+------+------+---------+---------------+----------+
@dataclass
class B:
    op : B_ops
    rs1: int
    rs2: int
    imm: int # -2048 <= imm <= 2047   (2**11 = 2048)
    
    def __repr__(self):
        return f"Op:{self.op} \trs1:{self.rs1} \trs2:{self.rs2} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} x{self.rs1}, x{self.rs2}, {self.imm}"


# U type instruction
# +------------------------------------+------------+----------+
# |            imm[31:12]              |  rd        |  opcode  |
# +------------------------------------+------------+----------+
@dataclass
class U:
    op : U_ops
    rd : int
    imm: int # 0 <= imm <= 1048575   (2**20 = 1048576)
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} x{self.rd}, {self.imm}"


# J type instruction
# +------------------------------------+------------+----------+
# |       imm[20|10:1|11|19:12]        |  rd        |  opcode  |
# +------------------------------------+------------+----------+
@dataclass
class J:
    op : J_ops
    rd : int
    imm: int # -524288 <= imm <= 524287   (2**19 = 524288)
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} x{self.rd}, {self.imm}"


# TODO add docs and str repr for misc mem instructions
@dataclass
class M:
    op  : M_ops
    rd  : int
    rs1 : int
    succ: int
    pred: int
    fm  : int
    
    def __repr__(self):
        return f"OP:{self.op} \trd:{self.rd} \trs1:{self.rs1} \tsucc:{self.succ} \tpred:{self.pred} \tfm:{self.fm}"
    
    def __str__(self):
        return f"TODO"


# Atomic instruction
# +--------+----+----+-------+------+---------+------------+----------+
# | funct5 | aq | rl | rs2   | rs1  | funct3  |  rd        |  opcode  |
# +--------+----+----+-------+------+---------+------------+----------+
@dataclass
class A:
    op : A_ops
    rd : int
    rs1: int
    rs2: int
    aq : int
    rl : int
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \trs1:{self.rs1} \trs2:{self.rs2} \taq:{self.aq} \trl:{self.rl}"
    
    def __str__(self):
        show = f"{self.op}" + (".aq" if self.aq else "") + (".rl" if self.rl else "")
        return f"{show} x{self.rd}, x{self.rs2}, (x{self.rs1})"


# System instruction
# +--------------------------+-------+-------+----------+-----------+
# |     00000000000(0/1)     | 00000 |  000  |  00000   |  1110011  |
# +--------------------------+-------+-------+----------+-----------+
@dataclass
class E:
    op : E_ops
    
    def __repr__(self):
        return f"Op:{self.op}"
    
    def __str__(self):
        return f"{self.op}"
    

type Instruction = R | I | S | B | U | J | M | A | E
