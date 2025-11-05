from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

from src.hardware.ram32 import RAM32
from src.utils.logger import PR5Logger
from src.utils.constants import XWIDTH

from src.disassembler import disassemble_error
from src.isa.instructions import *
from src.isa.properties import *
from src.isa.opcodes import *
from src.hardware.reg import *
from src.hardware.alu import alu
from src.utils.cint import *

# TODO Remove regfile read in store stage
# instead pass the v_rs2 value down the pipeline


class PCSource(Enum):
    PLUS_4 = auto()
    IMM = auto()
    BRANCH_TARGET = auto()


@dataclass(frozen=True)
class PC_IF_Latch:
    """
    Program Counter/Fetch Latch

    Holds:
    - Program counter
    """

    pc: UInt32


@dataclass(frozen=True)
class IF_ID_Latch:
    """
    Fetch/Decode Latch

    Holds:
    - Program counter
    - Fetched instruction
    """

    inst: UInt32
    pc: UInt32


@dataclass(frozen=True)
class ID_EX_Latch:
    """
    Decode/Execute Latch

    Holds:
    - Decoded instruction
    - Fetched operands
        - `op1` (`rs1` or `pc`)
        - `op2` (`rs2` or `imm`)
    - Program counter
    """

    inst: Instruction

    op1: UInt32
    """`rs1` or `pc`"""

    op2: UInt32
    """`rs2` or `imm`"""

    pc: UInt32


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

    pc: UInt32
    result: UInt32


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

    result: UInt32
    loaded_data: Optional[UInt32]
    pc: UInt32


class Processor(ABC):
    def __init__(self, init_pc: UInt32, ram: RAM32, logger: PR5Logger) -> None:
        """
        Creates a new processor.

        :param init_pc: Initial program counter
        :param ram: Instruction and data memory
        :param logger: CPU events logger
        """
        self.init_pc = init_pc
        self.regfile = RegisterFile32(XWIDTH, zero_reg=True)
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
            self.logr.debug(f"[F] Fetched instruction {instruction} at PC {uint32(pc)}")
            return IF_ID_Latch(inst=instruction, pc=pc)

        except ValueError as e:
            self.logr.error(f"Error fetching instruction at {pc}: {e}")
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
        The operands are in the order:
        - `op1`: `rs1` or `pc`
        - `op1`: `rs2` or `imm`

        :param inst: Decoded instruction
        :param if_id: Latch containing fetched instruction and program
        counter

        :returns: Latch containing decoded instructions, fetched operands and pc

        :raises UnimplementedExecution: If execution of the instruction is unimplemented
        """

        op1: UInt32
        op2: UInt32

        match inst:
            case Reg_reg() | Branch():
                op1 = self.regfile.read(inst.rs1)
                op2 = self.regfile.read(inst.rs2)

            case Reg_imm() | Store() | Load() | Jalr():
                op1 = self.regfile.read(inst.rs1)
                op2 = uint32(inst.imm)

            case Upper_imm():
                match inst.op:
                    # The left shifting is done by the immediate generation unit
                    # not the ALU
                    case Upper_imm_ops.LUI:
                        op1 = uint32(0)
                        op2 = uint32(inst.imm << 12)  # TODO Magic number 12
                    case Upper_imm_ops.AUIPC:
                        op1 = if_id.pc
                        op2 = uint32(inst.imm << 12)  # TODO Magic number 12

            case Jal():
                op1 = if_id.pc
                op2 = uint32(inst.imm)

            case Misc_mem() | Atomic() | Env() | Zicsr_reg_imm() | Zicsr_reg_reg():
                raise UnimplementedExecution(inst)

        self.logr.debug(f"    Fetched operands and immediate generated:")
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
        inst = id_ex_latch.inst
        op = inst.op

        result = alu(op1, op2, op)

        if result is None:
            raise UnimplementedExecution(inst)

        self.logr.debug(f"[E] ALU Result of {op} is: {result}")

        return EX_MEM_Latch(
            inst=inst,
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

        next_pc = pc + uint32(4)
        pc_src = PCSource.PLUS_4

        match inst:
            case Branch():
                imm = inst.imm
                if result != 0:
                    # Branch taken
                    next_pc = pc + uint32(imm)
                    pc_src = PCSource.IMM

            case Jal() | Jalr():
                next_pc = result
                pc_src = PCSource.BRANCH_TARGET

            case (
                Reg_reg()
                | Reg_imm()
                | Load()
                | Store()
                | Upper_imm()
                | Misc_mem()
                | Atomic()
                | Env()
                | Zicsr_reg_reg()
                | Zicsr_reg_imm()
            ):
                pass

        match pc_src:
            case PCSource.PLUS_4:
                self.logr.debug(f"[U] PC = PC + 4")
            case PCSource.IMM:
                self.logr.debug(f"[U] PC = PC + imm")
            case PCSource.BRANCH_TARGET:
                self.logr.debug(f"[U] PC = alu_result")

        self.logr.debug(f"    {uint32(pc)} -> {uint32(next_pc)}")

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
                loaded_data: UInt32 = uint32(0)

                match inst.op:
                    case Load_ops.LBU:
                        loaded_data = uint32(self.mem.read_byte(addr))
                    case Load_ops.LB:
                        loaded_data = sext_uint32(self.mem.read_byte(addr))
                    case Load_ops.LHU:
                        loaded_data = uint32(self.mem.read_halfword(addr))
                    case Load_ops.LH:
                        loaded_data = sext_uint32(self.mem.read_halfword(addr))
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
                loaded_data: UInt32 = uint32(0)

                rs2 = inst.rs2 if inst.rs2 else 0
                data = self.regfile.read(rs2)

                match inst.op:
                    case Store_ops.SB:
                        self.mem.write_byte(addr, uint8(data))
                    case Store_ops.SH:
                        self.mem.write_halfword(addr, uint16(data))
                    case Store_ops.SW:
                        self.mem.write_word(addr, data)

                self.logr.debug(f"[M] Stored data {data} to memory address {addr}")

                return MEM_WB_Latch(
                    inst=inst,
                    result=ex_mem_latch.result,
                    loaded_data=None,
                    pc=ex_mem_latch.pc,
                )

            case (
                Reg_reg()
                | Reg_imm()
                | Jalr()
                | Branch()
                | Upper_imm()
                | Jal()
                | Misc_mem()
                | Atomic()
                | Env()
                | Zicsr_reg_reg()
                | Zicsr_reg_imm()
            ):
                self.logr.debug(f"[M] Idle")

                return MEM_WB_Latch(
                    inst=inst,
                    result=ex_mem_latch.result,
                    loaded_data=None,
                    pc=ex_mem_latch.pc,
                )

    def log_instruction(
        self, mem_wb_latch: MEM_WB_Latch, pc_if_latch: PC_IF_Latch
    ) -> None:
        # TODO Check if the data structures need refinement
        """
        Log the executed instruction, given the current state and next pc value, in the
        format:

        current_pc | next_pc | optional rd | optional memory write
        """
        # NOTE: CAUTION - Changing the outputs here will violate test cases
        result = mem_wb_latch.result
        inst = mem_wb_latch.inst
        pc = mem_wb_latch.pc
        next_pc = pc_if_latch.pc

        match inst:
            case Branch() | Env():
                self.logr.out(
                    f"{int(pc):08x} | "
                    + f"next_pc = {int(next_pc):08x} | "
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
                    f"{int(pc):08x} | "
                    + f"next_pc = {int(next_pc):08x} | "
                    + f"x{rd} = {int(self.regfile.read(rd)):08x} | "
                    + f"mem[{int(result):08x}] => {int(loaded_data):08x}"
                )
                return

            case Store():
                result = mem_wb_latch.result
                rs2 = inst.rs2

                data = self.regfile.read(rs2 if rs2 else 0)

                self.logr.out(
                    f"{int(pc):08x} | "
                    + f"next_pc = {int(next_pc):08x} | "
                    + f"x? = {0:08x} | "
                    + f"mem[{int(result):08x}] <= {int(data):08x}"
                )
                return

            case (
                Reg_reg()
                | Reg_imm()
                | Jalr()
                | Upper_imm()
                | Jal()
                | Misc_mem()
                | Atomic()
                | Zicsr_reg_reg()
                | Zicsr_reg_imm()
            ):
                rd = inst.rd
                self.logr.out(
                    f"{int(pc):08x} | "
                    + f"next_pc = {int(next_pc):08x} | "
                    + f"x{rd} = {int(self.regfile.read(rd)):08x} | "
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
                    loaded_data = uint32(0)

                self.regfile.write(rd, loaded_data)
                self.logr.debug(f"[W] Written {loaded_data} to x{rd}")

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
                self.logr.debug(f"[W] Written {v_rd} to x{rd}")

                return

            case Store() | Branch() | Env():
                self.logr.debug(f"[W] Idle")
                return

            case (
                Reg_reg()
                | Upper_imm()
                | Misc_mem()
                | Atomic()
                | Zicsr_reg_reg()
                | Zicsr_reg_imm()
            ):
                rd = inst.rd
                self.regfile.write(rd, result)
                self.logr.debug(f"[W] Written {result} to x{rd}")

                return

    @abstractmethod
    def run(self, num_insts: int):
        """
        Run the processor. To be implemented by subclasses.
        """
        pass
