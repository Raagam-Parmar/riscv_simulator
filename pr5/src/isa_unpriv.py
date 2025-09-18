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
# |        11 |  BRANCH |  JALR   |         |   JAL    |  SYSTEM |         |         |         |
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
# 
# The blank fields are illegal instructions in RV32-IMA-ZICSR


def verify_bit(bit: int):
    """Assert `bit` is either `0` or `1`"""
    assert 0 <= bit <= 1, f'Invalid bit {bit}'

def verify_2b_align(imm: int):
    """Assert `imm` is even"""
    assert imm & 0b1 == 0, f'Immediate not 2-byte aligned {imm}'

def verify_reg(reg: int):
    """Assert `reg` is in range `[0, 31]`"""
    assert 0 <= reg <= 31, f'Invalid register x{reg}'

def verify_imm12(imm: int):
    """Assert `imm` is in range `[-2048, 2047]`"""
    assert -2048 <= imm <= 2047, f'12-bit immediate out of range {imm}'

def verify_imm20(imm: int):
    """Assert `imm` is in range `[-524288, 524287]`"""
    assert -524288 <= imm <= 524287, f'20-bit immediate out of range {imm}'

def verify_uimm4(imm: int):
    """Assert `imm` is in range `[0, 15]`"""
    assert 0 <= imm <= 15, f'4-bit unsigned immediate out of range {imm}'

def verify_uimm5(imm: int):
    """Assert `imm` is in range `[0, 31]`"""
    assert 0 <= imm <= 31, f'5-bit unsigned immediate out of range {imm}'

def verify_uimm6(imm: int):
    """Assert `imm` is in range `[0, 63]`"""
    assert 0 <= imm <= 63, f'6-bit unsigned immediate out of range {imm}'

def verify_uimm12(imm: int):
    """Assert `imm` is in range `[0, 4095]`"""
    assert 0 <= imm <= 4095, f'12-bit unsigned immediate out of range {imm}'

def verify_uimm20(imm: int):
    """Assert `imm` is in range `[0, 1048575]`"""
    assert 0 <= imm <= 1048575, f'20-bit unsigned immediate out of range {imm}'


# Reg instruction
# +-----------+-------+------+---------+------------+-----------+
# | funct7    | rs2   | rs1  | funct3  |     rd     |  0110011  |
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
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Reg:
    op : Reg_ops
    rd : int
    rs1: int
    rs2: int
    
    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_reg(self.rs2)
    
    def __str__(self):
        # op    rd, rs1, rs2
        return f"{self.op} \tx{self.rd}, x{self.rs1}, x{self.rs2}"


# Imm instruction
# Base ISA Immediate Operations and JALR
# +-------------------+------+---------+------------+-----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  opcode   |
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
    
    JALR  = auto()
        
    def __str__(self):
        return self.name.lower()


@dataclass
class Imm:
    op : Imm_ops
    rd : int
    rs1: int
    imm: int
    # encoded as -2048 <= imm <= 2047  (2**11 = 2048)
    # actual same as encoded
    
    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_imm12(self.imm)
    
    def __str__(self):
        # op    rd, rs1, imm
        return f"{self.op} \tx{self.rd}, x{self.rs1}, {self.imm}"


# Load instruction
#  Base ISA Load operations
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
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Load:
    op : Load_ops
    rd : int
    rs1: int
    imm: int
    # encoded as -2048 <= imm <= 2047  (2**11 = 2048)
    # actual same as encoded
    
    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_imm12(self.imm)
    
    def __str__(self):
        # op    rd, imm(rs1)
        return f"{self.op} \tx{self.rd}, {self.imm}(x{self.rs1})"


# Store instruction
#  Base ISA store operations
# +------------+------+------+---------+------------+-----------+
# | imm[11:5]  | rs2  | rs1  | funct3  |  imm[4:0]  |  0100011  |
# +------------+------+------+---------+------------+-----------+
class Store_ops(Enum):
    # RV32-I
    SB = auto()
    SH = auto()
    SW = auto()
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Store:
    op : Store_ops
    rs1: int
    rs2: int
    imm: int
    # encoded as -2048 <= imm <= 2047   (2**11 = 2048)
    # actual same as encoded
    
    def __post_init__(self):
        verify_reg(self.rs1)
        verify_reg(self.rs2)
        verify_imm12(self.imm)
    
    def __str__(self):
        # op    rs2, imm(rs1)
        return f"{self.op} \tx{self.rs2}, {self.imm}(x{self.rs1})"


# Branch instruction
# Base ISA branch operations
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
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Branch:
    op : Branch_ops
    rs1: int
    rs2: int
    # encoded as -2048 <= imm <= 2047   (2**11 = 2048)
    # actual  as -4096 <= imm <= 4095   (2**12 = 4096) (evens only)
    imm: int
    
    def __post_init__(self):
        verify_reg(self.rs1)
        verify_reg(self.rs2)
        verify_2b_align(self.imm)
        verify_imm12(self.imm // 2)
    
    def __str__(self):
        # op    rs1, rs2, imm
        return f"{self.op} \tx{self.rs1}, x{self.rs2}, {hex(self.imm)}"


# Upper Immediate instruction
# Base ISA U-type instructions (LUI, AUIPC)
# +------------------------------------+------------+----------+
# |            imm[31:12]              |     rd     |  opcode  |
# +------------------------------------+------------+----------+
class Upper_ops(Enum):
    # RV32-I
    LUI = auto()
    AUIPC = auto()
        
    def __str__(self):
        return self.name.lower()


@dataclass
class Upper:
    op : Upper_ops
    rd : int
    imm: int
    # encoded as 0 <= imm <= 1048575   (2**20 = 1048576)
    # actual same as encoded [TODO TEST]
    
    def __post_init__(self):
        verify_reg(self.rd)
        verify_uimm20(self.imm)
    
    def __str__(self):
        # op    rd, imm
        return f"{self.op} \tx{self.rd}, {hex(self.imm)}"


# Jump instruction
# Base ISA J-type instructions (JAL)
# +------------------------------------+------------+----------+
# |       imm[20|10:1|11|19:12]        |     rd     |  opcode  |
# +------------------------------------+------------+----------+
class Jump_ops(Enum):
    # RV32-I
    JAL = auto()
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Jump:
    op : Jump_ops
    rd : int
    imm: int
    # encoded as -524288 <= imm <= 524287   (2**19 = 524288)
    # actual  as -1048575 <= imm <= 1048576 (2**20 = 1048576) (evens only)
    
    def __post_init__(self):
        verify_reg(self.rd)
        verify_imm20(self.imm // 2)
        verify_2b_align(self.imm)
    
    def __str__(self):
        # op    rd, imm
        return f"{self.op} \tx{self.rd}, {hex(self.imm)}"


# Misc Mem instruction
# Base ISA Misc Mem Instructions (FENCE, FENCE.TSO, PAUSE)
# +--------+---------+--------+-------+-------+------+-----------+
# |   fm   |  pred   | succ   |  rs1  |  000  |  rd  |  0001111  |
# +--------+---------+--------+-------+-------+------+-----------+
class Misc_mem_ops(Enum):
    # RV32-I
    FENCE     = auto()
    FENCE_TSO = auto()
    PAUSE     = auto()
    
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
    
    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_uimm4(self.succ)
        verify_uimm4(self.pred)
        verify_uimm4(self.fm)
    
    def __str__(self):
        if self.op != Misc_mem_ops.FENCE:
            return f"{self.op}"
        
        pred = ""
        succ = ""
        
        for i in reversed(range(4)):
            if (self.pred >> i) & 0b1:
                if i == 3: pred += "i"
                if i == 2: pred += "o"
                if i == 1: pred += "r"
                if i == 0: pred += "w"
            
            if (self.succ >> i) & 0b1:
                if i == 3: succ += "i"
                if i == 2: succ += "o"
                if i == 1: succ += "r"
                if i == 0: succ += "w"

        return f"{self.op} {pred}, {succ}"


# Atomic instruction
# Atomic Extension (R-type instructions)
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
    
    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_reg(self.rs2)
        verify_bit(self.aq)
        verify_bit(self.rl)
    
    def __str__(self):
        show = f"{self.op}"
        
        if self.aq and not self.rl:
            show += ".aq"
            
        elif self.rl and not self.aq:
            show += ".rl"
        
        elif self.aq and self.rl:
            show += ".aqrl"

        return f"{show} \tx{self.rd}, x{self.rs2}, (x{self.rs1})"


# Environment instruction
# Base ISA System Instructions (ECALL, EBREAK)
# Some of Priviledged ISA instructions (SRET, MRET, MNRET, WFI)
# +-----------------+--------+-------+----------+----------+-----------+
# |   funct7        |  rs2   |  rs1  |  funct3  |  rd      |  1110011  |
# +-----------------+--------+-------+----------+----------+-----------+
class System_ops(Enum):
    # RV32-I
    ECALL  = auto()
    EBREAK = auto()
    
    # RV32 Privledged ISA
    SRET = auto()
    MRET = auto()
    MNRET = auto()
    
    WFI = auto()
    
    def __str__(self):
        return self.name.lower()


@dataclass
class System:
    op : System_ops
        
    def __str__(self):
        # op
        return f"{self.op}"
    

# Zicsr instruction
# Zicsr Extension (R-type instructions)
# +--------------------------+-------+----------+----------+-----------+
# |            csr           | rs1   |  funct3  |  rd      |  1110011  |
# +--------------------------+-------+----------+----------+-----------+
class Zicsr_ops(Enum):
    CSRRW = auto()
    CSRRS = auto()
    CSRRC = auto()
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Zicsr:
    op : Zicsr_ops
    rd : int
    rs1: int
    csr: int
    
    def __post_init__(self):
        verify_reg(self.rd)
        verify_reg(self.rs1)
        verify_uimm12(self.csr)
    
    def __str__(self):
        # op    rd, csr, rs1
        return f"{self.op} \tx{self.rd}, 0x{self.csr:03x}, x{self.rs1}"


# Zicsr Immediate instruction
# Zicsr Extension (I-type instructions)
# +--------------------------+-------+----------+----------+-----------+
# |            csr           | uimm  |  funct3  |  rd      |  1110011  |
# +--------------------------+-------+----------+----------+-----------+
class Zicsr_imm_ops(Enum):
    CSRRWI = auto()
    CSRRSI = auto()
    CSRRCI = auto()
    
    def __str__(self):
        return self.name.lower()


@dataclass
class Zicsr_Imm:
    op  : Zicsr_imm_ops
    rd  : int
    csr : int
    uimm: int
    # encoded as 0 <= uimm <= 32   (2**5 = 32)
    # actual same as encoded
    
    def __post_init__(self):
        verify_reg(self.rd)
        verify_uimm5(self.uimm)
        verify_uimm12(self.csr)
    
    def __str__(self):
        # op    rd, csr, uimm
        return f"{self.op} \tx{self.rd}, 0x{self.csr:03x}, {self.uimm}"
