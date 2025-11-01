from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

from src.hardware.ram import RAM
from src.utils.logger import PR5Logger
from src.utils.constants import XWIDTH

from src.disassembler import disassemble_error
from src.isa.instructions import *
from src.isa.opcodes import *
from src.hardware.reg import *
from src.hardware.alu_tables import *
from src.utils.bits import sign_extend

# TODO Remove regfile read in store stage
# instead pass the v_rs2 value down the pipeline


class UnimplementedExecution(Exception):
    def __init__(self, inst: Instruction):
        self.message = f"Execution of instruction '{inst}' is not implemented."
        super().__init__(self.message)


class PCSource(Enum):
    PLUS_4 = auto()
    IMM = auto()
    ALU_OUT = auto()


@dataclass(frozen=True)
class PC_IF_Latch:
    """
    Program Counter/Fetch Latch

    Holds:
    - Program counter
    """

    pc: int


@dataclass(frozen=True)
class IF_ID_Latch:
    """
    Fetch/Decode Latch

    Holds:
    - Program counter
    - Fetched instruction
    """

    inst: int
    pc: int


@dataclass(frozen=True)
class ID_EX_Latch:
    """
    Decode/Execute Latch

    Holds:
    - Decoded instruction
    - Fetched operands
    - Program counter
    """

    inst: Instruction

    op1: int
    op2: int

    pc: int


@dataclass(frozen=True)
class EX_MEM_Latch:
    """
    Execute/Memory Access Latch

    Holds:
    - Decoded instruction
    - ALU Result
    - Program counter
    """

    inst: Instruction

    pc: int
    result: int


@dataclass(frozen=True)
class MEM_WB_Latch:
    """
    Memory Access/Writeback stage

    Holds:
    - Decoded instruction
    - ALU Result
    - Load-data (for Load instruction)
    - Program counter
    """

    inst: Instruction

    result: int
    loaded_data: Optional[int]
    pc: int


class Processor(ABC):
    def __init__(self, init_pc: int, ram: RAM, logger: PR5Logger) -> None:
        """
        Creates a new processor.

        :param init_pc: Initial program counter
        :param ram: Instruction and data memory
        :param logger: CPU events logger
        """
        self.init_pc = init_pc
        self.regfile = RegisterFile(XWIDTH, zero_reg=True)
        self.mem = ram
        self.logr = logger

    def initialise_pc(self):
        """
        Initialize the program counter with its initial value.
        """
        return PC_IF_Latch(self.init_pc)

    def fetch(self, pc_if_latch: PC_IF_Latch) -> IF_ID_Latch:
        """
        Fetch the instruction in the latch.

        :param pc_if_latch: Latch containing program counter

        :returns: Latch containing fetched instruction and program counter

        :raises ValueError: If the fetch is unsuccessful
        """
        pc = pc_if_latch.pc

        try:
            instruction = self.mem.read_word(pc)
            self.logr.debug(f"[F] Fetched instruction {instruction:08x} at PC {pc:08x}")
            return IF_ID_Latch(inst=instruction, pc=pc)

        except ValueError as e:
            self.logr.error(f"Error fetching instruction at {pc:08x}: {e}")
            exit()

    def decode(self, if_id_latch: IF_ID_Latch) -> Instruction:
        """
        Decode the instruction.

        :param if_id_latch: Latch containing fetched instruction and program
        counter

        :returns: Decoded instruction

        :raises InvalidInstruction: If the instruction is invalid or unsupported
        """
        dis = disassemble_error(if_id_latch.inst)
        self.logr.debug(f"[D] Decoded instruction {dis}")
        return dis

    def operand_fetch(self, inst: Instruction, if_id: IF_ID_Latch) -> ID_EX_Latch:
        """
        Fetch the required operands for a decoded instruction

        :param inst: Decoded instruction
        :param if_id: Latch containing fetched instruction and program
        counter

        :returns: Latch containing decoded instructions, fetched operands and pc

        :raises UnimplementedExecution: If execution of the instruction is unimplemented
        """

        match inst:
            case Reg_reg():
                op1 = self.regfile.read(inst.rs1)
                op2 = self.regfile.read(inst.rs2)

                if inst.op is Reg_reg_ops.SUB:
                    op2 = -1 * op2

            case Reg_imm() | Store() | Load() | Jalr():
                op1 = self.regfile.read(inst.rs1)
                op2 = inst.imm

            case Branch():
                op1 = self.regfile.read(inst.rs1)
                op2 = self.regfile.read(inst.rs2)

                match inst.op:
                    case Branch_ops.BLTU | Branch_ops.BGEU:
                        pass
                    case _:
                        op1 = sign_extend(op1, XWIDTH)
                        op2 = sign_extend(op2, XWIDTH)

            case Upper_imm():
                match inst.op:
                    case Upper_imm_ops.LUI:
                        # NOTE imm << 12
                        # e_sll functional unit used
                        op1 = inst.imm
                        op2 = 12
                    case Upper_imm_ops.AUIPC:
                        # NOTE pc + (imm << 12)
                        # e_auipc functional unit used
                        op1 = if_id.pc
                        op2 = inst.imm

            case Jal():
                # NOTE pc + imm
                # e_add functional unit used
                op1 = if_id.pc
                op2 = inst.imm

            case _:
                raise UnimplementedExecution(inst)

        self.logr.debug(f"    Fetched operands")
        self.logr.debug(f"     - op1 = {op1}")
        self.logr.debug(f"     - op2 = {op2}")

        return ID_EX_Latch(
            inst=inst,
            op1=op1,
            op2=op2,
            pc=if_id.pc,
        )

    def execute(self, id_ex_latch: ID_EX_Latch) -> EX_MEM_Latch:
        """
        Execute the instruction.

        :param id_ex_latch: Latch containing decoded instructions, fetched
        operands and pc

        :returns: Latch containing decoded instruction, execution result and pc
        """
        op1 = id_ex_latch.op1
        op2 = id_ex_latch.op2
        op = id_ex_latch.inst.op

        result = function_tbl[op](op1, op2)
        self.logr.debug(f"[E] ALU Result of {op} is: {hex(result)}")

        return EX_MEM_Latch(
            inst=id_ex_latch.inst,
            result=result,
            pc=id_ex_latch.pc,
        )

    def update_pc(self, ex_mem_latch: EX_MEM_Latch) -> PC_IF_Latch:
        """
        Update the program counter to either branch/jump or take PC + 4.

        :param ex_mem_latch: Latch containing decoded instruction, execution
        result and pc

        :returns: Latch containing the new program counter value
        """
        inst = ex_mem_latch.inst
        result = ex_mem_latch.result
        pc = ex_mem_latch.pc

        next_pc = pc + 4
        pc_src = PCSource.PLUS_4

        match inst:
            case Branch():
                imm = inst.imm
                # Result is true if and only if the branch is taken
                if result:
                    # Branch taken
                    next_pc = pc + imm
                    pc_src = PCSource.IMM

            case Jal() | Jalr():
                next_pc = result
                pc_src = PCSource.ALU_OUT

            case _:
                pass

        match pc_src:
            case PCSource.PLUS_4:
                self.logr.debug(f"[U] PC = PC + 4")
            case PCSource.IMM:
                self.logr.debug(f"[U] PC = PC + imm")
            case PCSource.ALU_OUT:
                self.logr.debug(f"[U] PC = alu_result")

        self.logr.debug(f"    {hex(pc)} -> {hex(next_pc)}")

        return PC_IF_Latch(pc=next_pc)

    def mem_access(self, ex_mem_latch: EX_MEM_Latch) -> MEM_WB_Latch:
        """
        Perform memory access for the instruction.

        :param ex_mem_latch: Latch containing decoded instruction, execution
        result and pc

        :returns: Latch containing decoded instruction, execution result, pc and
        loaded data for writeback
        """
        inst = ex_mem_latch.inst

        match inst:
            case Load():
                addr = ex_mem_latch.result
                loaded_data = 0

                match inst.op:
                    case Load_ops.LBU:
                        loaded_data = self.mem.read_byte(addr)
                    case Load_ops.LB:
                        loaded_data = sign_extend(self.mem.read_byte(addr), XWIDTH // 4)
                    case Load_ops.LHU:
                        loaded_data = self.mem.read_halfword(addr)
                    case Load_ops.LH:
                        loaded_data = sign_extend(
                            self.mem.read_halfword(addr), XWIDTH // 2
                        )
                    case Load_ops.LW:
                        loaded_data = self.mem.read_word(addr)

                self.logr.debug(
                    f"[M] Retrieved data {loaded_data} from memory address {addr}"
                )

                return MEM_WB_Latch(
                    inst=inst,
                    result=ex_mem_latch.result,
                    loaded_data=loaded_data,
                    pc=ex_mem_latch.pc,
                )

            case Store():
                addr = ex_mem_latch.result
                loaded_data = 0

                rs2 = inst.rs2 if inst.rs2 else 0
                data = self.regfile.read(rs2)

                match inst.op:
                    case Store_ops.SB:
                        self.mem.write_byte(addr, data)
                    case Store_ops.SH:
                        self.mem.write_halfword(addr, data)
                    case Store_ops.SW:
                        self.mem.write_word(addr, data)

                self.logr.debug(
                    f"[M] Stored data {data} to memory address {addr}"
                )

                return MEM_WB_Latch(
                    inst=inst,
                    result=ex_mem_latch.result,
                    loaded_data=None,
                    pc=ex_mem_latch.pc,
                )

            case _:
                self.logr.debug(
                    f"[M] Idle"
                )

                return MEM_WB_Latch(
                    inst=inst,
                    result=ex_mem_latch.result,
                    loaded_data=None,
                    pc=ex_mem_latch.pc,
                )

    def log_instruction(
        self, mem_wb_latch: MEM_WB_Latch, pc_if_latch: PC_IF_Latch
    ) -> None:
        # TODO Make documentation better.
        # TODO Check if the data structures need refinement
        """
        Log the executed instruction, given the current state and next pc value
        """
        # NOTE: CAUTION - Changing the outputs here will violate test cases
        result = mem_wb_latch.result
        inst = mem_wb_latch.inst
        pc = mem_wb_latch.pc
        next_pc = pc_if_latch.pc

        # current_ps | next_pc | optional rd | optional memory write

        match inst:
            case Branch() | System():
                self.logr.out(
                    f"{pc:08x} | "
                    + f"next_pc = {next_pc:08x} | "
                    + f"x? = {0:08x} | "
                    + f"mem[?] = {0:08x}"
                )
                return

            case Load():
                loaded_data = mem_wb_latch.loaded_data
                result = mem_wb_latch.result
                rd = inst.rd

                if loaded_data is None:
                    loaded_data = 0

                self.logr.out(
                    f"{pc:08x} | "
                    + f"next_pc = {next_pc:08x} | "
                    + f"x{rd} = {self.regfile.read(rd):08x} | "
                    + f"mem[{result:08x}] => {loaded_data:08x}"
                )
                return

            case Store():
                result = mem_wb_latch.result
                rs2 = inst.rs2

                data = self.regfile.read(rs2 if rs2 else 0)

                self.logr.out(
                    f"{pc:08x} | "
                    + f"next_pc = {next_pc:08x} | "
                    + f"x? = {0:08x} | "
                    + f"mem[{result:08x}] <= {data:08x}"
                )
                return

            case _:
                # rd = mem_wb_latch.rd if mem_wb_latch.rd else 0
                rd = inst.rd
                self.logr.out(
                    f"{pc:08x} | "
                    + f"next_pc = {next_pc:08x} | "
                    + f"x{rd} = {self.regfile.read(rd):08x} | "
                    + f"mem[?] = {0:08x}"
                )

    def writeback(self, mem_wb_latch: MEM_WB_Latch) -> None:
        """
        Write the result of the operation back to the register.

        :param mem_wb_latch: Latch containing decoded instruction, execution
        result, pc and loaded data for writeback
        :param pc_if_latch: Latch containing the new program counter value
        """
        result = mem_wb_latch.result
        inst = mem_wb_latch.inst
        pc = mem_wb_latch.pc

        match inst:
            case Load():
                loaded_data = mem_wb_latch.loaded_data
                rd = inst.rd
                result = mem_wb_latch.result

                if loaded_data is None:
                    loaded_data = 0

                self.regfile.write(rd, loaded_data)
                self.logr.debug(f"[W] Written {hex(loaded_data)} to x{rd}")

                return

            case Jal() | Jalr():
                rd = inst.rd
                v_rd = pc + 4
                self.regfile.write(rd, v_rd)
                return

            case Reg_imm():
                rd = inst.rd
                v_rd = result

                self.regfile.write(rd, v_rd)
                self.logr.debug(f"[W] Written {hex(v_rd)} to x{rd}")

                return

            case Store() | Branch() | System():
                self.logr.debug(f"[W] Idle")
                return

            case _:
                rd = inst.rd
                self.regfile.write(rd, result)
                self.logr.debug(f"[W] Written {hex(result)} to x{rd}")

                return

    @abstractmethod
    def run(self, num_insts: int):
        """
        Run the processor. To be implemented by subclasses.
        """
        pass
