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


# R type instruction
# +-----------+-------+------+---------+------------+-----------+
# | funct7    | rs2   | rs1  | funct3  |  rd        |  0110011  |
# +-----------+-------+------+---------+------------+-----------+
class Reg_ops(Enum):
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
        return f"Reg Op:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Reg:
    op : Reg_ops
    rd : int
    rs1: int
    rs2: int
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \trs1:{self.rs1} \trs2:{self.rs2}"
    
    def __str__(self):
        return f"{self.op} \tx{self.rd}, x{self.rs1}, x{self.rs2}"


# I type instruction
# +-------------------+------+---------+------------+-----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  0010011  |
# +-------------------+------+---------+------------+-----------+
class Imm_ops(Enum):
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
    
    JALR = auto()
    
    ECALL  = auto()
    EBREAK = auto()
    
    def __repr__(self):
        return f"Imm Op:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Imm:
    op : Imm_ops
    rd : int
    rs1: int
    imm: int # -2048 <= imm <= 2047  (2**11 = 2048)
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \trs1:{self.rs1} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} \tx{self.rd}, x{self.rs1}, {self.imm}"


# Load instruction
# +-------------------+------+---------+------------+-----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  0000011  |
# +-------------------+------+---------+------------+-----------+
class Load_ops(Enum):
    # RV32-I
    LB  = auto()
    LH  = auto()
    LW  = auto()
    LBU = auto()
    LHU = auto()
    
    def __repr__(self):
        return f"Load Op:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Load:
    op : Load_ops
    rd: int
    rs1: int
    imm: int # -2048 <= imm <= 2047  (2**11 = 2048)
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \trs1:{self.rs1} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} \tx{self.rd}, {self.imm}(x{self.rs1})"


# S type instruction
# +------------+------+------+---------+------------+-----------+
# | imm[11:5]  | rs2  | rs1  | funct3  |  imm[4:0]  |  0100011  |
# +------------+------+------+---------+------------+-----------+
class Store_ops(Enum):
    # RV32-I
    SB = auto()
    SH = auto()
    SW = auto()
    
    def __repr__(self):
        return f"S-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Store:
    op : Store_ops
    rs1: int
    rs2: int
    imm: int # -2048 <= imm <= 2047   (2**11 = 2048)
    
    def __repr__(self):
        return f"Op:{self.op} \trs1:{self.rs1} \trs2:{self.rs2} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} \tx{self.rs2}, {self.imm}(x{self.rs1})"


# B type instruction
# +---------------+------+------+---------+---------------+-----------+
# | imm[12|10:5]  | rs2  | rs1  | funct3  |  imm[4:1|11]  |  1100011  |
# +---------------+------+------+---------+---------------+-----------+
class Branch_ops(Enum):
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


@dataclass
class Branch:
    op : Branch_ops
    rs1: int
    rs2: int
    imm: int # -2048 <= imm <= 2047   (2**11 = 2048)
    
    def __repr__(self):
        return f"Op:{self.op} \trs1:{self.rs1} \trs2:{self.rs2} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} \tx{self.rs1}, x{self.rs2}, {self.imm}"


# U type instruction
# +------------------------------------+------------+----------+
# |            imm[31:12]              |  rd        |  opcode  |
# +------------------------------------+------------+----------+
class Upper_ops(Enum):
    # RV32-I
    LUI = auto()
    AUIPC = auto()
        
    def __repr__(self):
        return f"U-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Upper:
    op : Upper_ops
    rd : int
    imm: int # 0 <= imm <= 1048575   (2**20 = 1048576)
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} \tx{self.rd}, {self.imm}"


# J type instruction
# +------------------------------------+------------+----------+
# |       imm[20|10:1|11|19:12]        |  rd        |  opcode  |
# +------------------------------------+------------+----------+
class Jump_ops(Enum):
    # RV32-I
    JAL = auto()
    
    def __repr__(self):
        return f"J-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Jump:
    op : Jump_ops
    rd : int
    imm: int # -524288 <= imm <= 524287   (2**19 = 524288)
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \timm:{self.imm}"
    
    def __str__(self):
        return f"{self.op} \tx{self.rd}, {self.imm}"


# TODO add str repr for misc mem instructions
# Misc Mem instruction
# +--------+---------+--------+-------+-------+------+-----------+
# |   fm   |  pred   | succ   |  rs1  |  000  |  rd  |  0001111  |
# +--------+---------+--------+-------+-------+------+-----------+
class Misc_mem_ops(Enum):
    # RV32-I
    FENCE     = auto()
    FENCE_TSO = auto()
    PAUSE     = auto()
    
    def __repr__(self):
        return f"MM-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower().replace('_', '.')


@dataclass
class Misc_mem:
    op  : Misc_mem_ops
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
# +--------+----+----+-------+------+---------+------------+-----------+
# | funct5 | aq | rl |  rs2  | rs1  |  010    |  rd        |  0101111  |
# +--------+----+----+-------+------+---------+------------+-----------+
class Atomic_ops(Enum):
    # RV32-A
    LR_W       = auto()
    SC_W       = auto()
    AMOSWAP_W  = auto()
    AMOADD_W   = auto()
    AMOXOR_W   = auto()
    AMOAND_W   = auto()
    AMOOR_W    = auto()
    AMOMIN_W   = auto()
    AMOMAX_W   = auto()
    AMOMINU_W  = auto()
    AMOMAXU_W  = auto()

    def __repr__(self):
        return f"A-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower().replace('_', '.')


@dataclass
class Atomic:
    op : Atomic_ops
    rd : int
    rs1: int
    rs2: int
    aq : int
    rl : int
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \trs1:{self.rs1} \trs2:{self.rs2} \taq:{self.aq} \trl:{self.rl}"
    
    def __str__(self):
        # show = f"{self.op}" + (".aq" if self.aq else "") + (".rl" if self.rl else "")
        show = f"{self.op}"
        if self.aq and not self.rl:
            show += ".aq"
            
        if self.rl and not self.aq:
            show += ".rl"
        
        if self.aq and self.rl:
            show += ".aqrl"

        return f"{show} \tx{self.rd}, x{self.rs2}, (x{self.rs1})"


# System instruction
# +-----------------+--------+-------+----------+----------+-----------+
# |   funct7        |  rs2   |  rs1  |  funct3  |  rd      |  1110011  |
# +-----------------+--------+-------+----------+----------+-----------+
class System_ops(Enum):
    # RV32-I
    ECALL  = auto()
    EBREAK = auto()
    
    def __repr__(self):
        return f"SYS-OP:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class System:
    op : System_ops
    
    def __repr__(self):
        return f"Op:{self.op}"
    
    def __str__(self):
        return f"{self.op}"
    

# Zicsr instruction
# +--------------------------+-------+----------+----------+-----------+
# |            csr           | rs1   |  funct3  |  rd      |  1110011  |
# +--------------------------+-------+----------+----------+-----------+
class Csr(Enum):
    # Floating point CSRs
    fflags   = auto()
    frm      = auto()
    fcsr     = auto()
    
    # Counters and Timers
    cycle    = auto()
    time     = auto()
    instret  = auto()
    cycleh   = auto()
    timeh    = auto()
    instreth = auto()
    
    def __repr__(self):
        return f"Csr Code:{self.name}"
    
    def __str__(self):
        return self.name.lower()


class Zicsr_ops(Enum):
    CSRRW = auto()
    CSRRS = auto()
    CSRRC = auto()
    
    def __repr__(self):
        return f"Zicsr Op:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Zicsr:
    op : Zicsr_ops
    rd : int
    rs1: int
    # csr: Csr
    csr : int
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \trs1:{self.rs1} \tcsr:{self.csr}"
    
    def __str__(self):
        return f"{self.op} \tx{self.rd}, 0x{self.csr:03x}, x{self.rs1}"


# Zicsr instruction
# +--------------------------+-------+----------+----------+-----------+
# |            csr           | uimm  |  funct3  |  rd      |  1110011  |
# +--------------------------+-------+----------+----------+-----------+
class Zicsr_imm_ops(Enum):
    CSRRWI = auto()
    CSRRSI = auto()
    CSRRCI = auto()
    
    def __repr__(self):
        return f"Zicsr Imm Op:{self.name}"
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Zicsr_Imm:
    op  : Zicsr_imm_ops
    rd  : int
    uimm: int # 0 <= uimm <= 32   (2**5 = 32)
    # csr : Csr
    csr : int
    
    def __repr__(self):
        return f"Op:{self.op} \trd:{self.rd} \trs1:{self.uimm} \tcsr:{self.csr}"
    
    def __str__(self):
        return f"{self.op} \tx{self.rd}, {self.csr}, {self.uimm}"
