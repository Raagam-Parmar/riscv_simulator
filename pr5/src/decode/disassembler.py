from typing import Dict, Callable, Optional


from pr5.src.utils.bits import signed_max
from core.typs import inst32
from isa.types import *
from isa.enums import *
from isa.tables import *
from fields import *


class InvalidInstruction(Exception):
    def __init__(self, inst: inst32):
        self.message = f"Invalid Instruction: {hex(inst)} , {bin(inst)}"
        super().__init__(self.message)


def sign_wrap(value: int, width: int) -> int:
    if value < 0:
        raise ValueError("sign_wrap: Value can not be negative.", value)

    if value > signed_max(width):
        return value - 2**width

    return value


# ---------------------------------------------------------------------------- #
# Load Instruction
# ---------------------------------------------------------------------------- #
def decode_load(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)

    if fun3 not in load_tbl:
        return None

    rd = RD.extract(inst)
    rs1 = RS1.extract(inst)
    imm = sign_wrap(I_IMM.extract(inst), i_imm_width)

    return Load(load_tbl[fun3], rd, rs1, imm)


# ---------------------------------------------------------------------------- #
# Store Instruction
# ---------------------------------------------------------------------------- #
def decode_store(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)

    if fun3 not in store_tbl:
        return None

    rs1 = RS1.extract(inst)
    rs2 = RS2.extract(inst)
    imm4_0 = S_IMM_4_0.extract(inst)
    imm11_5 = S_IMM_11_5.extract(inst)

    imm = imm11_5 << 5 | imm4_0
    imm = sign_wrap(imm, s_imm_width)

    return Store(store_tbl[fun3], rs1, rs2, imm)


# ---------------------------------------------------------------------------- #
# Branch Instruction
# ---------------------------------------------------------------------------- #
def decode_branch(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)

    if fun3 not in branch_tbl:
        return None

    rs1 = RS1.extract(inst)
    rs2 = RS2.extract(inst)
    imm12 = B_IMM_12.extract(inst)
    imm11 = B_IMM_11.extract(inst)
    imm10_5 = B_IMM_10_5.extract(inst)
    imm4_1 = B_IMM_4_1.extract(inst)

    imm = imm12 << 12 | imm11 << 11 | imm10_5 << 5 | imm4_1 << 1
    imm = sign_wrap(imm, b_imm_width)

    return Branch(branch_tbl[fun3], rs1, rs2, imm)


# ---------------------------------------------------------------------------- #
# JALR
# ---------------------------------------------------------------------------- #
def decode_jalr(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)

    if fun3 != 0b000:
        return None

    rd = RD.extract(inst)
    rs1 = RS1.extract(inst)
    imm = sign_wrap(I_IMM.extract(inst), i_imm_width)

    return Imm(Imm_ops.JALR, rd, rs1, imm)


# ---------------------------------------------------------------------------- #
# Misc Memory Instruction
# ---------------------------------------------------------------------------- #
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


# ---------------------------------------------------------------------------- #
# Atomic Instruction
# ---------------------------------------------------------------------------- #
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
    rd = RD.extract(inst)
    aq = A_AQ.extract(inst)
    rl = A_RL.extract(inst)

    return Atomic(amo_tbl[fun5], rd, rs1, rs2, aq, rl)


# ---------------------------------------------------------------------------- #
# JAL
# ---------------------------------------------------------------------------- #
def decode_jal(inst: inst32) -> Optional[Instruction]:
    rd = RD.extract(inst)
    imm20 = J_IMM_20.extract(inst)
    imm10_1 = J_IMM_10_1.extract(inst)
    imm11 = J_IMM_11.extract(inst)
    imm19_12 = J_IMM_19_12.extract(inst)

    imm = imm20 << 20 | imm19_12 << 12 | imm11 << 11 | imm10_1 << 1
    imm = sign_wrap(imm, j_imm_width)

    return Jump(Jump_ops.JAL, rd, imm)


# ---------------------------------------------------------------------------- #
# Imm Op Instruction
# ---------------------------------------------------------------------------- #
def decode_op_imm(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)
    rd = RD.extract(inst)
    rs1 = RS1.extract(inst)
    fun7 = FUNCT7.extract(inst)
    imm = sign_wrap(I_IMM.extract(inst), i_imm_width)

    if fun3 in op_imm_f3_tbl:
        return Imm(op_imm_f3_tbl[fun3], rd, rs1, imm)

    if (fun3, fun7) not in op_imm_f3_f7_tbl:
        return None

    return Imm(op_imm_f3_f7_tbl[(fun3, fun7)], rd, rs1, imm)


# ---------------------------------------------------------------------------- #
# Reg Op Instruction
# ---------------------------------------------------------------------------- #
def decode_op(inst: inst32) -> Optional[Instruction]:
    fun3 = FUNCT3.extract(inst)
    fun7 = FUNCT7.extract(inst)

    pair = (fun3, fun7)

    if pair not in op_tbl:
        return None

    rd = RD.extract(inst)
    rs1 = RS1.extract(inst)
    rs2 = RS2.extract(inst)

    return Reg(op_tbl[pair], rd, rs1, rs2)


# ---------------------------------------------------------------------------- #
# Zicsr Instruction
# ---------------------------------------------------------------------------- #
def decode_zicsr(inst: inst32, fun3: funct3) -> Optional[Instruction]:
    rs1 = RS1.extract(inst)
    csr = CSR.extract(inst)
    rd = RD.extract(inst)

    return Zicsr(zicsr_tbl[fun3], rd, rs1, csr)


# ---------------------------------------------------------------------------- #
# Zicsr Immediate Instruction
# ---------------------------------------------------------------------------- #
def decode_zicsr_imm(inst: inst32, fun3: funct3) -> Optional[Instruction]:
    imm = CSR_UIMM.extract(inst)
    csr = CSR.extract(inst)
    rd = RD.extract(inst)

    return Zicsr_Imm(zicsr_imm_tbl[fun3], rd, csr, imm)


# ---------------------------------------------------------------------------- #
# System Instruction
# ---------------------------------------------------------------------------- #
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


# ---------------------------------------------------------------------------- #
# AUIPC
# ---------------------------------------------------------------------------- #
def decode_auipc(inst: inst32) -> Optional[Instruction]:
    rd = RD.extract(inst)
    imm = U_IMM.extract(inst)

    return Upper(Upper_ops.AUIPC, rd, imm)


# ---------------------------------------------------------------------------- #
# LUI
# ---------------------------------------------------------------------------- #
def decode_lui(inst: inst32) -> Optional[Instruction]:
    rd = RD.extract(inst)
    imm = U_IMM.extract(inst)

    return Upper(Upper_ops.LUI, rd, imm)


# ---------------------------------------------------------------------------- #
# Opcode Map
# ---------------------------------------------------------------------------- #
opcode_tbl: Dict[int, Callable[[inst32], Optional[Instruction]]] = {
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
    0b0110111: decode_lui,
}


# ---------------------------------------------------------------------------- #
# Disassembler
# ---------------------------------------------------------------------------- #
def dis(inst: inst32) -> Optional[Instruction]:
    opcode = OPCODE.extract(inst)

    if opcode not in opcode_tbl:
        return None

    return opcode_tbl[opcode](inst)
