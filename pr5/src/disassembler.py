from typing import Dict, Tuple, Callable

from isa import *
import bits

type funct3   = int
type funct5   = int
type funct7   = int
type opcode   = int
type inst32   = int
type mmconst  = int
type sysconst = int


class InvalidInstruction(Exception):
    def __init__(self, inst: inst32):
        self.message = f"Invalid Instruction: {hex(inst)} , {bin(inst)}"
        super().__init__(self.message)


def sign_wrap(value: int, width: int) -> int:
    if value < 0:
        raise ValueError("sign_wrap: Value can not be negative.", value)
    
    if value > bits.signed_max(width):
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
OP_1_0 = Field(1, 0)
OP_4_2 = Field(4, 2)
OP_6_5 = Field(6, 5)
RD     = Field(11, 7)
FUNCT3 = Field(14, 12)
RS1    = Field(19, 15)
RS2    = Field(24, 20)
FUNCT7 = Field(31, 25)

# I-type Fields
I_IMM = Field(31, 20)
I_IMM_WIDTH = 12

# S-type Fields
S_IMM_11_5 = Field(31, 25)
S_IMM_4_0  = Field(11, 7)
S_IMM_WIDTH = 12

# B-type Fields
B_IMM_12   = Field(31, 31)
B_IMM_10_5 = Field(30, 25)
B_IMM_4_1  = Field(11, 8)
B_IMM_11   = Field(7, 7)
B_IMM_WIDTH = 12

# U-type Fields
U_IMM = Field(31, 12)

# J-type Fields
J_IMM_20    = Field(31, 31)
J_IMM_10_1  = Field(30, 21)
J_IMM_11    = Field(20, 20)
J_IMM_19_12 = Field(19, 12)
J_IMM_WIDTH = 20

# Misc-Mem Fields
MM_FM    = Field(31, 28)
MM_PRED  = Field(27, 24)
MM_SUCC  = Field(23, 20)
MM_CONST = Field(31, 7)

# Atomic Fields
A_FUN5 = Field(31, 27)
A_AQ   = Field(26, 26)
A_RL   = Field(25, 25)

# System Fields
SYS_CONST = Field(31, 7)


'''
we have a global map, which would hold what? mapping from the instructions
to their ast counterparts.

say i read the instruction.
the rightmost 2 bits are NOT 11
i throw an error: illegal isntruction.

otherwise i read the bits [4:2] and bits [6:5]
i also have a 2d hashtable, where the outermost layer stores the mapping
for inst[4:2], and it holds a mapping to another hasntable which 
holds mapping from inst[6:5] to the desired instruction.

this makes it easier for me to throw error if the inst[4:2] is 010, 110 or 111
as those are illegal in our case.
'''

load_tbl : Dict[funct3, I_ops] = {
    0b000: I_ops.LB,
    0b001: I_ops.LH,
    0b010: I_ops.LW,
    0b100: I_ops.LBU,
    0b101: I_ops.LHU
}

store_tbl : Dict[funct3, S_ops] = {
    0b000: S_ops.SB,
    0b001: S_ops.SH,
    0b010: S_ops.SW
}

branch_tbl : Dict[funct3, B_ops] = {
    0b000: B_ops.BEQ,
    0b001: B_ops.BNE,
    0b100: B_ops.BLT,
    0b101: B_ops.BGE,
    0b110: B_ops.BLTU,
    0b111: B_ops.BGEU
}

amo_tbl : Dict[funct5, A_ops] = {
    0b00010: A_ops.LR_W,
    0b00011: A_ops.SC_W,
    0b00001: A_ops.AMOSWAP_W,
    0b00000: A_ops.AMOADD_W,
    0b00100: A_ops.AMOXOR_W,
    0b01100: A_ops.AMOAND_W,
    0b01000: A_ops.AMOOR_W,
    0b10000: A_ops.AMOMIN_W,
    0b10100: A_ops.AMOMAX_W,
    0b11000: A_ops.AMOMINU_W,
    0b11100: A_ops.AMOMAXU_W
}

op_imm_f3_tbl : Dict[funct3, I_ops] = {
    0b000: I_ops.ADDI,
    0b010: I_ops.SLTI,
    0b011: I_ops.SLTIU,
    0b100: I_ops.XORI,
    0b110: I_ops.ORI,
    0b111: I_ops.ANDI
}

op_imm_f3_f7_tbl : Dict[Tuple[funct3, funct7], I_ops] = {
    (0b001, 0b0000000): I_ops.SLLI,
    (0b101, 0b0000000): I_ops.SRLI,
    (0b101, 0b0100000): I_ops.SRAI
}

op_tbl : Dict[Tuple[funct3, funct7], R_ops] = {
    # RV32-I
    (0b000, 0b0000000): R_ops.ADD,
    (0b000, 0b0100000): R_ops.SUB,
    (0b001, 0b0000000): R_ops.SLL,
    (0b010, 0b0000000): R_ops.SLT,
    (0b011, 0b0000000): R_ops.SLTU,
    (0b100, 0b0000000): R_ops.XOR,
    (0b101, 0b0000000): R_ops.SRL,
    (0b101, 0b0100000): R_ops.SRA,
    (0b110, 0b0000000): R_ops.OR,
    (0b111, 0b0000000): R_ops.AND,
    
    # RV32-M
    (0b000, 0b0000001): R_ops.MUL,
    (0b001, 0b0000001): R_ops.MULH,
    (0b010, 0b0000001): R_ops.MULHSU,
    (0b011, 0b0000001): R_ops.MULHSU,
    (0b100, 0b0000001): R_ops.DIV,
    (0b101, 0b0000001): R_ops.DIVU,
    (0b110, 0b0000001): R_ops.REM,
    (0b111, 0b0000001): R_ops.REMU
}

misc_mem_tbl : Dict[mmconst, M_ops] = {
    0x0020000: M_ops.PAUSE,
    0x1066000: M_ops.FENCE_TSO 
}

system_tbl : Dict[sysconst, E_ops] = {
    0x0000: E_ops.ECALL,
    0x2000: E_ops.EBREAK
}


def decode_load(inst: inst32) -> Instruction:
    fun3 = FUNCT3.extract(inst)
    
    if fun3 not in load_tbl:
        raise InvalidInstruction(inst)

    rd  = RD.extract(inst)    
    rs1 = RS1.extract(inst)
    imm = I_IMM.extract(inst)
    
    return I(load_tbl[fun3], rd, rs1, sign_wrap(imm, I_IMM_WIDTH))


def decode_store(inst: inst32) -> Instruction:
    fun3 = FUNCT3.extract(inst)
    
    if fun3 not in store_tbl:
        raise InvalidInstruction(inst)

    rs1     = RS1.extract(inst)
    rs2     = RS2.extract(inst)
    imm4_0  = S_IMM_4_0.extract(inst)
    imm11_5 = S_IMM_11_5.extract(inst)
    
    imm = imm11_5 << 5 | imm4_0
    
    return S(store_tbl[fun3], rs1, rs2, sign_wrap(imm, S_IMM_WIDTH))


def decode_branch(inst: inst32) -> Instruction:
    fun3 = FUNCT3.extract(inst)
    
    if fun3 not in branch_tbl:
        raise InvalidInstruction(inst)
    
    rs1     = RS1.extract(inst)
    rs2     = RS2.extract(inst)
    imm12   = B_IMM_12.extract(inst)
    imm11   = B_IMM_11.extract(inst)
    imm10_5 = B_IMM_10_5.extract(inst)
    imm4_1  = B_IMM_4_1.extract(inst)
    
    imm = imm12 << 12 | imm11 << 11 | imm10_5 << 5 | imm4_1 << 1
    
    return B(branch_tbl[fun3], rs1, rs2, sign_wrap(imm, B_IMM_WIDTH))


def decode_jalr(inst: inst32) -> Instruction:
    fun3 = FUNCT3.extract(inst)
    
    if fun3 != 0b000:
        raise InvalidInstruction(inst)
    
    rd   = RD.extract(inst)
    rs1  = RS1.extract(inst)
    imm  = I_IMM.extract(inst)
    
    return I(I_ops.JALR, rd, rs1, sign_wrap(imm, I_IMM_WIDTH))


def decode_misc_mem(inst: inst32) -> Instruction:
    fun3 = FUNCT3.extract(inst)

    const = MM_CONST.extract(inst)

    rd = RD.extract(inst)
    rs1 = RS1.extract(inst)
    succ = MM_SUCC.extract(inst)
    pred = MM_PRED.extract(inst)
    fm = MM_FM.extract(inst)

    if fun3 != 0b000:
        raise InvalidInstruction(inst)
    
    mop = misc_mem_tbl[const] if const in misc_mem_tbl else M_ops.FENCE
        
    return M(mop, rd, rs1, succ, pred, fm)


def decode_amo(inst: inst32) -> Instruction:
    fun3 = FUNCT3.extract(inst)
    
    if fun3 != 0b010:
        raise InvalidInstruction(inst)
    
    fun5 = A_FUN5.extract(inst)
    
    if fun5 not in amo_tbl:
        raise InvalidInstruction(inst)
    
    rs2 = RS2.extract(inst)
    
    if (fun5 == 0b00010) and (rs2 != 0b00000):
        raise InvalidInstruction(inst)
    
    rs1 = RS1.extract(inst)
    rd  = RD.extract(inst)
    aq  = A_AQ.extract(inst)
    rl  = A_RL.extract(inst)
    
    return A(amo_tbl[fun5], rd, rs1, rs2, aq, rl)


def decode_jal(inst: inst32) -> Instruction:
    rd       = RD.extract(inst)
    imm20    = J_IMM_20.extract(inst)
    imm10_1  = J_IMM_10_1.extract(inst)
    imm11    = J_IMM_11.extract(inst)
    imm19_12 = J_IMM_19_12.extract(inst)
    
    imm = imm20 << 20 | imm19_12 << 12 | imm11 << 11 | imm10_1 << 1
    
    return J(J_ops.JAL, rd, imm)


def decode_op_imm(inst: inst32) -> Instruction:
    fun3 = FUNCT3.extract(inst)
    rd   = RD.extract(inst)
    rs1  = RS1.extract(inst)
    imm  = I_IMM.extract(inst)
    fun7 = FUNCT7.extract(inst)
    
    if fun3 in op_imm_f3_tbl:
        return I(op_imm_f3_tbl[fun3], rd, rs1, sign_wrap(imm, I_IMM_WIDTH))
    
    if (fun3, fun7) not in op_imm_f3_f7_tbl:
        raise InvalidInstruction(inst)
    
    return I(op_imm_f3_f7_tbl[(fun3, fun7)], rd, rs1, sign_wrap(imm, I_IMM_WIDTH))


def decode_op(inst: inst32) -> Instruction:
    fun3 = FUNCT3.extract(inst)
    fun7 = FUNCT7.extract(inst)
    
    pair = (fun3, fun7)
    
    if pair not in op_tbl:
        raise InvalidInstruction(inst)
    
    rd  = RD.extract(inst)
    rs1 = RS1.extract(inst)
    rs2 = RS2.extract(inst)
    
    return R(op_tbl[pair], rd, rs1, rs2)


def decode_system(inst: inst32) -> Instruction:
    sys_const = SYS_CONST.extract(inst)
    
    if sys_const not in system_tbl:
        raise InvalidInstruction(inst)
    
    return E(system_tbl[sys_const])


def decode_auipc(inst: inst32) -> Instruction:
    rd  = RD.extract(inst)
    imm = U_IMM.extract(inst)
    
    return U(U_ops.AUIPC, rd, imm)


def decode_lui(inst: inst32) -> Instruction:
    rd  = RD.extract(inst)
    imm = U_IMM.extract(inst)
    
    return U(U_ops.LUI, rd, imm)


opcode_tbl : Dict[int, Callable[[inst32], Instruction]] = {
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


def dis(inst: inst32) -> Instruction:
    opcode = OPCODE.extract(inst)
    
    if opcode not in opcode_tbl:
        raise InvalidInstruction(inst)
    
    return opcode_tbl[opcode] (inst)
