from typing import Dict, Callable, Optional

from src.isa.instructions import *
from src.isa.formats.r_type import opcode


class InvalidInstruction(Exception):
    def __init__(self, inst: int):
        self.message = f"Invalid Instruction: {hex(inst)} , {bin(inst)}"
        super().__init__(self.message)


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


def disassemble(inst: int) -> Optional[Instruction]:
    """Disassemble a RISCV instruction.

    :param inst: Binary-encoded instruction

    :return: `None` if the instruction is invalid or unimplemented, otherwise the
    disassembled instruction
    """
    op = opcode.extract(inst)

    if opcode not in opcode_tbl:
        return None

    return opcode_tbl[op](inst)


def disassemble_error(inst: int) -> Instruction:
    """Disassemble a RISCV instruction or raise an error.

    :params inst: Binary-encoded instruction

    :return: Disassembled instruction

    :raises InvalidInstruction: if the instruction is invalid or unimplemented.
    """

    op = opcode.extract(inst)

    if op not in opcode_tbl:
        raise InvalidInstruction(inst)

    maybe_inst = opcode_tbl[op](inst)

    if not maybe_inst:
        raise InvalidInstruction(inst)

    return maybe_inst
