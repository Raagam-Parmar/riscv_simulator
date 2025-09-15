from typing import Dict, Tuple, Callable, Optional

from isa import *
from isa_unpriv import *
from bits import signed_max

type funct3   = int
type funct5   = int
type funct7   = int
type opcode   = int
type inst32   = int
type mmconst  = int
type const    = int
type csr      = int


class InvalidInstruction(Exception):
    def __init__(self, inst: inst32):
        self.message = f"Invalid Instruction: {hex(inst)} , {bin(inst)}"
        super().__init__(self.message)


def sign_wrap(value: int, width: int) -> int:
    if value < 0:
        raise ValueError("sign_wrap: Value can not be negative.", value)
    
    if value > signed_max(width):
        return value - 2 ** width
    
    return value


@dataclass(frozen=True)
class Field:
    hi: int
    lo: int
    
    def extract(self, inst: inst32) -> int:
        width: int = self.hi - self.lo + 1
        field = (inst >> self.lo) & ((1 << width) - 1)
        return field


# RISC-V Standard Fields
OPCODE = Field(6, 0)
RD     = Field(11, 7)
FUNCT3 = Field(14, 12)
RS1    = Field(19, 15)
RS2    = Field(24, 20)
FUNCT7 = Field(31, 25)
CONST  = Field(31, 7)
MSB    = Field(31, 31)



# -----------------------------------------------------------------------------
# Load Instruction
# -----------------------------------------------------------------------------
I_IMM = Field(31, 20)
I_IMM_WIDTH = 12

load_tbl : Dict[funct3, Load_ops] = {
    0b000: Load_ops.LB,
    0b001: Load_ops.LH,
    0b010: Load_ops.LW,
    0b100: Load_ops.LBU,
    0b101: Load_ops.LHU
}

def decode_load(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)
    
    if fun3 not in load_tbl:
        return None

    rd  = RD.extract(inst)    
    rs1 = RS1.extract(inst)
    imm = sign_wrap(I_IMM.extract(inst), I_IMM_WIDTH)
    
    return Load(load_tbl[fun3], rd, rs1, imm)



# -----------------------------------------------------------------------------
# Store Instruction
# -----------------------------------------------------------------------------
S_IMM_11_5 = FUNCT7
S_IMM_4_0  = Field(11, 7)
S_IMM_WIDTH = 12

store_tbl : Dict[funct3, Store_ops] = {
    0b000: Store_ops.SB,
    0b001: Store_ops.SH,
    0b010: Store_ops.SW
}

def decode_store(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)
    
    if fun3 not in store_tbl:
        return None

    rs1     = RS1.extract(inst)
    rs2     = RS2.extract(inst)
    imm4_0  = S_IMM_4_0.extract(inst)
    imm11_5 = S_IMM_11_5.extract(inst)
    
    imm = imm11_5 << 5 | imm4_0
    imm = sign_wrap(imm, S_IMM_WIDTH)
    
    return Store(store_tbl[fun3], rs1, rs2, imm)



# -----------------------------------------------------------------------------
# Branch Instruction
# -----------------------------------------------------------------------------
B_IMM_12   = MSB
B_IMM_10_5 = Field(30, 25)
B_IMM_4_1  = Field(11, 8)
B_IMM_11   = Field(7, 7)
B_IMM_WIDTH = 13

branch_tbl : Dict[funct3, Branch_ops] = {
    0b000: Branch_ops.BEQ,
    0b001: Branch_ops.BNE,
    0b100: Branch_ops.BLT,
    0b101: Branch_ops.BGE,
    0b110: Branch_ops.BLTU,
    0b111: Branch_ops.BGEU
}

def decode_branch(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)
    
    if fun3 not in branch_tbl:
        return None
    
    rs1     = RS1.extract(inst)
    rs2     = RS2.extract(inst)
    imm12   = B_IMM_12.extract(inst)
    imm11   = B_IMM_11.extract(inst)
    imm10_5 = B_IMM_10_5.extract(inst)
    imm4_1  = B_IMM_4_1.extract(inst)
    
    imm = imm12 << 12 | imm11 << 11 | imm10_5 << 5 | imm4_1 << 1
    imm = sign_wrap(imm, B_IMM_WIDTH)
    
    return Branch(branch_tbl[fun3], rs1, rs2, imm)



# -----------------------------------------------------------------------------
# JALR
# -----------------------------------------------------------------------------
def decode_jalr(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)
    
    if fun3 != 0b000:
        return None
    
    rd   = RD.extract(inst)
    rs1  = RS1.extract(inst)
    imm  = sign_wrap(I_IMM.extract(inst), I_IMM_WIDTH)
    
    return Imm(Imm_ops.JALR, rd, rs1, imm)



# -----------------------------------------------------------------------------
# Misc Memory Instruction
# -----------------------------------------------------------------------------
MM_FM    = Field(31, 28)
MM_PRED  = Field(27, 24)
MM_SUCC  = Field(23, 20)
MM_CONST = CONST

misc_mem_tbl : Dict[mmconst, Misc_mem_ops] = {
    0x0020000: Misc_mem_ops.PAUSE,
    0x1066000: Misc_mem_ops.FENCE_TSO 
}

def decode_misc_mem(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)

    const = MM_CONST.extract(inst)

    rd = RD.extract(inst)
    rs1 = RS1.extract(inst)
    succ = MM_SUCC.extract(inst)
    pred = MM_PRED.extract(inst)
    fm = MM_FM.extract(inst)

    if fun3 != 0b000:
        return None
    
    mop = misc_mem_tbl[const] if const in misc_mem_tbl else Misc_mem_ops.FENCE
        
    return Misc_mem(mop, rd, rs1, succ, pred, fm)



# -----------------------------------------------------------------------------
# Atomic Instruction
# -----------------------------------------------------------------------------
A_FUN5 = Field(31, 27)
A_AQ   = Field(26, 26)
A_RL   = Field(25, 25)

amo_tbl : Dict[funct5, Atomic_ops] = {
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
    0b11100: Atomic_ops.AMOMAXU_W
}

def decode_amo(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)
    
    if fun3 != 0b010:
        return None
    
    fun5 = A_FUN5.extract(inst)
    
    if fun5 not in amo_tbl:
        return None
    
    rs2 = RS2.extract(inst)
    
    if (fun5 == 0b00010) and (rs2 != 0b00000):
        return None
    
    rs1 = RS1.extract(inst)
    rd  = RD.extract(inst)
    aq  = A_AQ.extract(inst)
    rl  = A_RL.extract(inst)
    
    return Atomic(amo_tbl[fun5], rd, rs1, rs2, aq, rl)



# -----------------------------------------------------------------------------
# JAL
# -----------------------------------------------------------------------------
J_IMM_20    = MSB
J_IMM_10_1  = Field(30, 21)
J_IMM_11    = Field(20, 20)
J_IMM_19_12 = Field(19, 12)
J_IMM_WIDTH = 21

def decode_jal(inst: inst32) -> Optional[Instruction]:
    rd       = RD.extract(inst)
    imm20    = J_IMM_20.extract(inst)
    imm10_1  = J_IMM_10_1.extract(inst)
    imm11    = J_IMM_11.extract(inst)
    imm19_12 = J_IMM_19_12.extract(inst)
    
    imm = imm20 << 20 | imm19_12 << 12 | imm11 << 11 | imm10_1 << 1
    imm = sign_wrap(imm, J_IMM_WIDTH)
    
    return Jump(Jump_ops.JAL, rd, imm)



# -----------------------------------------------------------------------------
# Imm Op Instruction
# -----------------------------------------------------------------------------
op_imm_f3_tbl : Dict[funct3, Imm_ops] = {
    0b000: Imm_ops.ADDI,
    0b010: Imm_ops.SLTI,
    0b011: Imm_ops.SLTIU,
    0b100: Imm_ops.XORI,
    0b110: Imm_ops.ORI,
    0b111: Imm_ops.ANDI
}

op_imm_f3_f7_tbl : Dict[Tuple[funct3, funct7], Imm_ops] = {
    (0b001, 0b0000000): Imm_ops.SLLI,
    (0b101, 0b0000000): Imm_ops.SRLI,
    (0b101, 0b0100000): Imm_ops.SRAI
}

def decode_op_imm(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)
    rd   = RD.extract(inst)
    rs1  = RS1.extract(inst)
    fun7 = FUNCT7.extract(inst)
    imm  = sign_wrap(I_IMM.extract(inst), I_IMM_WIDTH)
    
    if fun3 in op_imm_f3_tbl:
        return Imm(op_imm_f3_tbl[fun3], rd, rs1, imm)
    
    if (fun3, fun7) not in op_imm_f3_f7_tbl:
        return None
    
    return Imm(op_imm_f3_f7_tbl[(fun3, fun7)], rd, rs1, imm)



# -----------------------------------------------------------------------------
# Reg Op Instruction
# -----------------------------------------------------------------------------
op_tbl : Dict[Tuple[funct3, funct7], Reg_ops] = {
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
    (0b111, 0b0000001): Reg_ops.REMU
}

def decode_op(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)
    fun7 = FUNCT7.extract(inst)
    
    pair = (fun3, fun7)
    
    if pair not in op_tbl:
        return None
    
    rd  = RD.extract(inst)
    rs1 = RS1.extract(inst)
    rs2 = RS2.extract(inst)
    
    return Reg(op_tbl[pair], rd, rs1, rs2)



# -----------------------------------------------------------------------------
# Zicsr Instruction
# -----------------------------------------------------------------------------
CSR       = I_IMM

zicsr_tbl : Dict[funct3, Zicsr_ops] = {
    0b001: Zicsr_ops.CSRRW,
    0b010: Zicsr_ops.CSRRS,
    0b011: Zicsr_ops.CSRRC
}

def decode_zicsr(inst: inst32, fun3: funct3) -> Optional[Instruction]:
    rs1 = RS1.extract(inst)
    csr = CSR.extract(inst)
    rd  = RD.extract(inst)
    
    return Zicsr(zicsr_tbl[fun3], rd, rs1, csr)



# -----------------------------------------------------------------------------
# Zicsr Immediate Instruction
# -----------------------------------------------------------------------------
CSR_UIMM  = RS1

zicsr_imm_tbl : Dict[funct3, Zicsr_imm_ops] = {
    0b101: Zicsr_imm_ops.CSRRWI,
    0b110: Zicsr_imm_ops.CSRRSI,
    0b111: Zicsr_imm_ops.CSRRCI
}

def decode_zicsr_imm(inst: inst32, fun3: funct3) -> Optional[Instruction]:
    imm = CSR_UIMM.extract(inst)
    csr = CSR.extract(inst)
    rd  = RD.extract(inst)
    
    return Zicsr_Imm(zicsr_imm_tbl[fun3], rd, csr, imm)    



# -----------------------------------------------------------------------------
# System Instruction
# -----------------------------------------------------------------------------
SYS_CONST = CONST

system_tbl : Dict[const, System_ops] = {
    0x0000: System_ops.ECALL,
    0x2000: System_ops.EBREAK,
    
    # RV32 Priviledged ISA
    0x204000: System_ops.SRET,
    0x604000: System_ops.MRET,
    0xe04000: System_ops.MNRET,
    
    0x20a000: System_ops.WFI
}

def decode_system(inst: inst32) -> Optional[Instruction]:
    sys_const = SYS_CONST.extract(inst)
    
    if sys_const in system_tbl:
        return System(system_tbl[sys_const])
    
    fun3 = FUNCT3.extract(inst)
    
    if fun3 in zicsr_tbl:
        return decode_zicsr(inst, fun3)
    
    if fun3 in zicsr_imm_tbl:
        return decode_zicsr_imm(inst, fun3)
    
    return None
    


# -----------------------------------------------------------------------------
# AUIPC
# -----------------------------------------------------------------------------
U_IMM = Field(31, 12)

def decode_auipc(inst: inst32) -> Optional[Instruction]:
    rd  = RD.extract(inst)
    imm = U_IMM.extract(inst)
    
    return Upper(Upper_ops.AUIPC, rd, imm)



# -----------------------------------------------------------------------------
# LUI
# -----------------------------------------------------------------------------
def decode_lui(inst: inst32) -> Optional[Instruction]:
    rd  = RD.extract(inst)
    imm = U_IMM.extract(inst)
    
    return Upper(Upper_ops.LUI, rd, imm)



# -----------------------------------------------------------------------------
# Opcode Map
# -----------------------------------------------------------------------------
opcode_tbl : Dict[int, Callable[[inst32], Optional[Instruction]]] = {
    0b0000011: decode_load,
    0b0100011: decode_store,
    0b1100011: decode_branch,
    0b1100111: decode_jalr,
    0b0001111: decode_misc_mem,
    0b0101111: decode_amo,
    0b1101111: decode_jal,
    0b0010011: decode_op_imm,
    0b0110011: decode_op,
    0b1110011: decode_system,
    0b0010111: decode_auipc,
    0b0110111: decode_lui
}



# -----------------------------------------------------------------------------
# Disassembler
# -----------------------------------------------------------------------------
def dis(inst: inst32) -> Optional[Instruction]:
    opcode = OPCODE.extract(inst)
    
    if opcode not in opcode_tbl:
        return None
    
    return opcode_tbl[opcode] (inst)
