from typing import Dict, Callable, Optional, Union

from src.isa.instructions import *
from src.utils.field import Field
from src.utils.cint import UInt32


class InvalidInstruction(Exception):
    def __init__(self, inst: UInt32):
        self.message = f"Invalid Instruction: {inst}"
        super().__init__(self.message)


_opcode = Field(6, 0)
"""
**Instruction opcode**: Least significant 7 bits of an instruction
"""


def decode_system(inst: int) -> Union[Zicsr_reg_reg, Zicsr_reg_imm, Env, None]:
    """
    Decodes a 32-bit instruction into a `System` instruction if possible, otherwise
    returns `None`.
    """

    env = decode_env(inst)
    zicsr_rr = decode_zicsr_reg_reg(inst)
    zicsr_ri = decode_zicsr_reg_imm(inst)

    if env:
        return env

    if zicsr_rr:
        return zicsr_rr

    if zicsr_ri:
        return zicsr_ri

    return None


opcode_tbl: Dict[int, Callable[[int], Optional[Instruction]]] = {
    0b0000011: decode_load,
    0b0100011: decode_store,
    0b1100011: decode_branch,
    0b1100111: decode_jalr,
    0b0001111: decode_misc_mem,
    0b0101111: decode_amo,
    0b1101111: decode_jal,
    0b0010011: decode_reg_imm,
    0b0110011: decode_reg_reg,
    0b1110011: decode_system,
    0b0010111: decode_auipc,
    0b0110111: decode_lui,
}


def disassemble(inst: UInt32) -> Optional[Instruction]:
    """
    Disassemble a RISCV instruction

    :param inst: Binary-encoded instruction

    :return: `None` if the instruction is invalid or unimplemented, otherwise the
    disassembled instruction
    """

    op = _opcode.extract(int(inst))

    if op not in opcode_tbl:
        return None

    return opcode_tbl[op](int(inst))


def disassemble_error(inst: UInt32) -> Instruction:
    """
    Disassemble a RISCV instruction or raise an error

    :params inst: Binary-encoded instruction

    :return: Disassembled instruction

    :raises InvalidInstruction: if the instruction is invalid or unimplemented.
    """

    op = _opcode.extract(int(inst))

    if op not in opcode_tbl:
        raise InvalidInstruction(inst)

    maybe_inst = opcode_tbl[op](int(inst))

    if not maybe_inst:
        raise InvalidInstruction(inst)

    return maybe_inst
