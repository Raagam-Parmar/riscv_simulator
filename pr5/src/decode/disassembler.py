from typing import Dict, Callable, Optional

from utils.bits import sign_extend
from isa.enums import *
from isa.formats import *
from isa.tables import *
from .fields import *


class InvalidInstruction(Exception):
    def __init__(self, inst: int):
        self.message = f"Invalid Instruction: {hex(inst)} , {bin(inst)}"
        super().__init__(self.message)


# def sign_wrap(value: int, width: int) -> int:
#     if value < 0:
#         raise ValueError("sign_wrap: Value can not be negative.", value)

#     if value > signed_max(width):
#         return value - 2**width

#     return value


# ---------------------------------------------------------------------------- #
# Load Instruction
# ---------------------------------------------------------------------------- #
def disassemble_load(inst: int) -> Optional[Instruction]:
    fun3 = funct3_field.extract(inst)

    if fun3 not in load_tbl:
        return None

    rd = rd_field.extract(inst)
    rs1 = rs1_field.extract(inst)
    imm = sign_extend(i_imm_field.extract(inst), i_imm_width)

    return Load(load_tbl[fun3], rd, rs1, imm)


# ---------------------------------------------------------------------------- #
# Store Instruction
# ---------------------------------------------------------------------------- #
def disassemble_store(inst: int) -> Optional[Instruction]:
    fun3 = funct3_field.extract(inst)

    if fun3 not in store_tbl:
        return None

    rs1 = rs1_field.extract(inst)
    rs2 = rs2_field.extract(inst)
    imm4_0 = s_imm_low_field.extract(inst)
    imm11_5 = s_imm_high_field.extract(inst)

    imm = imm11_5 << 5 | imm4_0
    imm = sign_extend(imm, s_imm_width)

    return Store(store_tbl[fun3], rs1, rs2, imm)


# ---------------------------------------------------------------------------- #
# Branch Instruction
# ---------------------------------------------------------------------------- #
def disassemble_branch(inst: int) -> Optional[Instruction]:
    fun3 = funct3_field.extract(inst)

    if fun3 not in branch_tbl:
        return None

    rs1 = rs1_field.extract(inst)
    rs2 = rs2_field.extract(inst)
    imm12 = b_imm_12_field.extract(inst)
    imm11 = b_imm_11_field.extract(inst)
    imm10_5 = b_imm_10_5_field.extract(inst)
    imm4_1 = b_immm_4_1_field.extract(inst)

    imm = imm12 << 12 | imm11 << 11 | imm10_5 << 5 | imm4_1 << 1
    imm = sign_extend(imm, b_imm_width)

    return Branch(branch_tbl[fun3], rs1, rs2, imm)


# ---------------------------------------------------------------------------- #
# JALR
# ---------------------------------------------------------------------------- #
def disassemble_jalr(inst: int) -> Optional[Instruction]:
    fun3 = funct3_field.extract(inst)

    if fun3 != 0b000:
        return None

    rd = rd_field.extract(inst)
    rs1 = rs1_field.extract(inst)
    imm = sign_extend(i_imm_field.extract(inst), i_imm_width)

    return Imm(Imm_ops.JALR, rd, rs1, imm)


# ---------------------------------------------------------------------------- #
# Misc Memory Instruction
# ---------------------------------------------------------------------------- #
def disassemble_misc_mem(inst: int) -> Optional[Instruction]:
    fun3 = funct3_field.extract(inst)

    const = mm_const_field.extract(inst)

    rd = rd_field.extract(inst)
    rs1 = rs1_field.extract(inst)
    succ = mm_succ_field.extract(inst)
    pred = mm_pred_field.extract(inst)
    fm = mm_fm_field.extract(inst)

    if fun3 != 0b000:
        return None

    mop = misc_mem_tbl[const] if const in misc_mem_tbl else Misc_mem_ops.FENCE

    return Misc_mem(mop, rd, rs1, succ, pred, fm)


# ---------------------------------------------------------------------------- #
# Atomic Instruction
# ---------------------------------------------------------------------------- #
def disassemble_amo(inst: int) -> Optional[Instruction]:
    fun3 = funct3_field.extract(inst)

    if fun3 != 0b010:
        return None

    fun5 = a_fun5_field.extract(inst)

    if fun5 not in amo_tbl:
        return None

    rs2 = rs2_field.extract(inst)

    if (fun5 == 0b00010) and (rs2 != 0b00000):
        return None

    rs1 = rs1_field.extract(inst)
    rd = rd_field.extract(inst)
    aq = a_aq_field.extract(inst)
    rl = a_rl_field.extract(inst)

    return Atomic(amo_tbl[fun5], rd, rs1, rs2, aq, rl)


# ---------------------------------------------------------------------------- #
# JAL
# ---------------------------------------------------------------------------- #
def disassemble_jal(inst: int) -> Optional[Instruction]:
    rd = rd_field.extract(inst)
    imm20 = j_imm_20_field.extract(inst)
    imm10_1 = j_imm_10_1_field.extract(inst)
    imm11 = j_imm_11_field.extract(inst)
    imm19_12 = j_imm_19_field.extract(inst)

    imm = imm20 << 20 | imm19_12 << 12 | imm11 << 11 | imm10_1 << 1
    imm = sign_extend(imm, j_imm_width)

    return Jump(Jump_ops.JAL, rd, imm)


# ---------------------------------------------------------------------------- #
# Imm Op Instruction
# ---------------------------------------------------------------------------- #
def disassemble_op_imm(inst: int) -> Optional[Instruction]:
    fun3 = funct3_field.extract(inst)
    rd = rd_field.extract(inst)
    rs1 = rs1_field.extract(inst)
    fun7 = fun7_field.extract(inst)
    imm = sign_extend(i_imm_field.extract(inst), i_imm_width)

    # TODO Fix constraints for SRAI, SLLI, SRLI

    if fun3 in op_imm_f3_tbl:
        return Imm(op_imm_f3_tbl[fun3], rd, rs1, imm)

    if (fun3, fun7) not in op_imm_f3_f7_tbl:
        return None

    opcode = op_imm_f3_f7_tbl[(fun3, fun7)]

    if opcode is Imm_ops.SLLI or opcode is Imm_ops.SRLI or opcode is Imm_ops.SRAI:
        return Imm(op_imm_f3_f7_tbl[(fun3, fun7)], rd, rs1, imm & 0b11111)

    return Imm(opcode, rd, rs1, imm)


# ---------------------------------------------------------------------------- #
# Reg Op Instruction
# ---------------------------------------------------------------------------- #
def disassemble_op(inst: int) -> Optional[Instruction]:
    fun3 = funct3_field.extract(inst)
    fun7 = fun7_field.extract(inst)

    pair = (fun3, fun7)

    if pair not in op_tbl:
        return None

    rd = rd_field.extract(inst)
    rs1 = rs1_field.extract(inst)
    rs2 = rs2_field.extract(inst)

    return Reg(op_tbl[pair], rd, rs1, rs2)


# ---------------------------------------------------------------------------- #
# Zicsr Instruction
# ---------------------------------------------------------------------------- #
def disassemble_zicsr(inst: int, fun3: funct3) -> Optional[Instruction]:
    rs1 = rs1_field.extract(inst)
    csr = csr_field.extract(inst)
    rd = rd_field.extract(inst)

    return Zicsr(zicsr_tbl[fun3], rd, rs1, csr)


# ---------------------------------------------------------------------------- #
# Zicsr Immediate Instruction
# ---------------------------------------------------------------------------- #
def disassemble_zicsr_imm(inst: int, fun3: funct3) -> Optional[Instruction]:
    imm = csr_uimm_field.extract(inst)
    csr = csr_field.extract(inst)
    rd = rd_field.extract(inst)

    return Zicsr_Imm(zicsr_imm_tbl[fun3], rd, csr, imm)


# ---------------------------------------------------------------------------- #
# System Instruction
# ---------------------------------------------------------------------------- #
def disassemble_system(inst: int) -> Optional[Instruction]:
    sys_const = sys_const_field.extract(inst)

    if sys_const in system_tbl:
        return System(system_tbl[sys_const])

    fun3 = funct3_field.extract(inst)

    if fun3 in zicsr_tbl:
        return disassemble_zicsr(inst, fun3)

    if fun3 in zicsr_imm_tbl:
        return disassemble_zicsr_imm(inst, fun3)

    return None


# ---------------------------------------------------------------------------- #
# AUIPC
# ---------------------------------------------------------------------------- #
def disassemble_auipc(inst: int) -> Optional[Instruction]:
    rd = rd_field.extract(inst)
    imm = u_imm_field.extract(inst)

    return Upper(Upper_ops.AUIPC, rd, imm)


# ---------------------------------------------------------------------------- #
# LUI
# ---------------------------------------------------------------------------- #
def disassemble_lui(inst: int) -> Optional[Instruction]:
    rd = rd_field.extract(inst)
    imm = u_imm_field.extract(inst)

    return Upper(Upper_ops.LUI, rd, imm)


# ---------------------------------------------------------------------------- #
# Opcode Map
# ---------------------------------------------------------------------------- #
opcode_tbl: Dict[int, Callable[[int], Optional[Instruction]]] = {
    0b0000011: disassemble_load,
    0b0100011: disassemble_store,
    0b1100011: disassemble_branch,
    0b1100111: disassemble_jalr,
    0b0001111: disassemble_misc_mem,
    0b0101111: disassemble_amo,
    0b1101111: disassemble_jal,
    0b0010011: disassemble_op_imm,
    0b0110011: disassemble_op,
    0b1110011: disassemble_system,
    0b0010111: disassemble_auipc,
    0b0110111: disassemble_lui,
}


# ---------------------------------------------------------------------------- #
# Disassembler
# ---------------------------------------------------------------------------- #
def disassemble(inst: int) -> Optional[Instruction]:
    """Disassemble a RISCV instruction.

    Returns `None` if the instruction is invalid or unimplemented.
    """
    opcode = opcode_field.extract(inst)

    if opcode not in opcode_tbl:
        return None

    return opcode_tbl[opcode](inst)


def disassemble_error(inst: int) -> Instruction:
    """Disassemble a RISCV instruction.

    Raises `InvalidInstruction` if the instruction is invalid or unimplemented.
    """

    opcode = opcode_field.extract(inst)

    if opcode not in opcode_tbl:
        raise InvalidInstruction(inst)

    maybe_inst = opcode_tbl[opcode](inst)

    if not maybe_inst:
        raise InvalidInstruction(inst)

    return maybe_inst
