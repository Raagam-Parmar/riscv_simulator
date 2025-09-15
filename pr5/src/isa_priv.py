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
# The blank fields are illegal instructions in RV32-IMA-ZICSR


# System instruction
# +-----------------+--------+-------+----------+----------+-----------+
# |   funct7        |  rs2   |  rs1  |  funct3  |  rd      |  1110011  |
# +-----------------+--------+-------+----------+----------+-----------+



# ----------------------------------------------------------------------
# Trap-Return Instructions
# ----------------------------------------------------------------------
class TrapRet_ops(Enum):
    SRET = auto()
    MRET = auto()
    MNRET = auto()
    
    def __repr__(self):
        return f"TrapRet Op:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class TrapRet:
    op : TrapRet_ops

    def __repr__(self):
        return f"TrapRet Op:{self.op}"
    
    def __str__(self):
        return f"{self.op}"


# ----------------------------------------------------------------------
# Interrupt-Management Instructions
# ----------------------------------------------------------------------
class IntManag_ops(Enum):
    WFI = auto()
    
    def __repr__(self):
        return f"IntManag Op:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class IntManag:
    op : IntManag_ops

    def __repr__(self):
        return f"IntManag Op:{self.op}"
    
    def __str__(self):
        return f"{self.op}"


# ----------------------------------------------------------------------
# Supervisor Memory Management Instructions
# ----------------------------------------------------------------------
class Supervisor_ops(Enum):
    SFENCE_VMA = auto()
    
    def __repr__(self):
        return f"SupMem Op:{self.name}"
    
    def __str__(self):
        return self.name.lower().replace('_', '.')


@dataclass
class Supervisor:
    op : Supervisor_ops
    rs1: int
    rs2: int

    def __repr__(self):
        return f"Supervisor Op:{self.op} \trs1:{self.rs1} \trs2:{self.rs2}"
    
    def __str__(self):
        return f"{self.op} x{self.rs1}, x{self.rs2}"


# ----------------------------------------------------------------------
# Hypervisor Memory-Management Instructions
# ----------------------------------------------------------------------
class HypervisorMM_ops(Enum):
    HFENCE_VVMA = auto()
    HFENCE_GVMA = auto()
    
    def __repr__(self):
        return f"HypervisorMM Op:{self.name}"
    
    def __str__(self):
        return self.name.lower().replace('_', '.')


@dataclass
class HypervisorMM:
    op : Supervisor_ops
    rs1: int
    rs2: int

    def __repr__(self):
        return f"HypervisorMM Op:{self.op} \trs1:{self.rs1} \trs2:{self.rs2}"
    
    def __str__(self):
        return f"{self.op} x{self.rs1}, x{self.rs2}"


# ----------------------------------------------------------------------
# Hypervisor Virtual-Machine Load and Store Instructions
# ----------------------------------------------------------------------
class HypervisorVM_ops(Enum):
    HLV_B   = auto()
    HLV_BU  = auto()
    HLV_H   = auto()
    HLV_HU  = auto()
    HLV_W   = auto()
    HLVX_HU = auto()
    HLVX_WU = auto()
    HSV_B   = auto()
    HSV_H   = auto()
    HSV_W   = auto()
    
    def __repr__(self):
        return f"HypervisorVM Op:{self.name}"
    
    def __str__(self):
        return self.name.lower().replace('_', '.')


@dataclass
class HypervisorVM:
    op : HypervisorVM_ops
    rd : int
    rs1: int

    def __repr__(self):
        return f"HypervisorVM Op:{self.op} \trs1:{self.rs1} \trs2:{self.rs2}"
    
    def __str__(self):
        return f"{self.op} x{self.rs1}, x{self.rs2}"


# ----------------------------------------------------------------------
# Svinval Memory-Management Extension
# ----------------------------------------------------------------------
class Svinval_ops(Enum):
    SINVAL_VMA      = auto()
    SFENCE_W_INVAL  = auto()
    SFENCE_INVAL_IR = auto()
    HINVAL_VVMA     = auto()
    HINVAL_GVMA     = auto()


@dataclass
class Svinval:
    op : Svinval_ops
    rs1: int
    rs2: int

    def __repr__(self):
        return f"Hypervisor Op:{self.op} \trs1:{self.rs1} \trs2:{self.rs2}"
    
    def __str__(self):
        return f"{self.op} x{self.rs1}, x{self.rs2}"


    


    

# # R type instruction
# # +-----------+-------+------+---------+------------+-----------+
# # | funct7    | rs2   | rs1  | funct3  |  rd        |  0110011  |
# # +-----------+-------+------+---------+------------+-----------+
# class Reg_ops(Enum):
#     # RV32-I
#     ADD  = auto()
#     SUB  = auto()
#     XOR  = auto()
#     OR   = auto()
#     AND  = auto()
#     SLL  = auto()
#     SRL  = auto()
#     SRA  = auto()
#     SLT  = auto()
#     SLTU = auto()
    
#     # RV32-M
#     MUL    = auto()
#     MULH   = auto()
#     MULHSU = auto()
#     MULHU  = auto()
#     DIV    = auto()
#     DIVU   = auto() 
#     REM    = auto()
#     REMU   = auto()    
        
#     def __repr__(self):
#         return f"Reg Op:{self.name}"
    
#     def __str__(self):
#         return self.name.lower()


# @dataclass
# class Reg:
#     op : Reg_ops
#     rd : int
#     rs1: int
#     rs2: int
    
#     def __repr__(self):
#         return f"Op:{self.op} \trd:{self.rd} \trs1:{self.rs1} \trs2:{self.rs2}"
    
#     def __str__(self):
#         return f"{self.op} \tx{self.rd}, x{self.rs1}, x{self.rs2}"
