from abc import ABC, abstractmethod

from ram import RAM
from logger import PR5Logger
from utils.constants import XWIDTH

from decode.disassembler import disassemble_error
from isa.formats import *
from isa.enums import *
from .reg import *
from .pc import *
from decode.fields import *
from .alu_tables import *
from utils.bits import sign_extend


@dataclass
class PC_IF_Latch:
    pc: int


@dataclass
class IF_ID_Latch:
    inst: int
    pc: int


@dataclass(frozen=True)
class ID_EX_Latch:
    op: OpCode
    rs1: Optional[int]
    rs2: Optional[int]
    rd: Optional[int]
    imm: Optional[int]

    op1: int
    op2: int

    pc: int


@dataclass(frozen=True)
class EX_MEM_Latch:
    op: OpCode
    rs1: Optional[int]
    rs2: Optional[int]
    rd: Optional[int]
    imm: Optional[int]

    pc: int
    result: int


@dataclass(frozen=True)
class MEM_WB_Latch:
    op: OpCode
    # rs1: Optional[int]
    rs2: Optional[int]
    rd: Optional[int]
    # imm: Optional[int]

    result: int
    loaded_data: Optional[int]
    pc: int


class Processor(ABC):
    def __init__(self, init_pc: int, ram: RAM, logger: PR5Logger) -> None:
        self.init_pc = init_pc
        self.regfile = RegisterFile(XWIDTH, zero_reg=True)
        self.mem = ram
        self.logr = logger

    def initialise_pc(self):
        return PC_IF_Latch(self.init_pc)

    def fetch(self, pc_if_latch: PC_IF_Latch) -> IF_ID_Latch:
        """
        Fetch the instruction from memory, and update PC
        returns instruction
        """
        pc = pc_if_latch.pc

        try:
            instruction = self.mem.read_word(pc)
            self.logr.debug(f"[F] Fetched instruction {instruction:08x} @ {pc:08x}")
            return IF_ID_Latch(inst=instruction, pc=pc)

        except ValueError as e:
            self.logr.error(f"Error fetching instruction at {pc:08x}: {e}")
            exit()

    def decode(self, if_id_latch: IF_ID_Latch) -> ID_EX_Latch:
        dis = disassemble_error(if_id_latch.inst)

        self.logr.debug(dis)

        decoded = dis.get_unified()

        rs1 = decoded.rs1
        rs2 = decoded.rs2
        rd = decoded.rd
        v_imm = decoded.imm if decoded.imm else 0
        op = decoded.op

        v_rs1 = self.regfile.read(rs1) if rs1 is not None else 0
        v_rs2 = self.regfile.read(rs2) if rs2 is not None else 0

        self.logr.debug(f"rs1 = {rs1}, rs2 = {rs2}, imm = {hex(v_imm)}, op = {op}")
        v_pc = if_id_latch.pc

        try:
            op1, op2 = operands_tbl[op](v_rs1, v_rs2, v_imm, v_pc)
        except KeyError:
            raise NotImplementedError(f"Op not implemented in operands_tbl: {op}")

        self.logr.debug(f"op1: {op1}, op2: {op2}")

        return ID_EX_Latch(
            op=op,
            rs1=rs1,
            rs2=rs2,
            rd=rd,
            imm=v_imm,
            op1=op1,
            op2=op2,
            pc=if_id_latch.pc,
        )

    def execute(self, id_ex_latch: ID_EX_Latch) -> EX_MEM_Latch:
        """
        Execute the instruction
        decoded_instr, operand1 and operand2 are returned by previous stages
        returns the result of the operation
        """
        op1 = id_ex_latch.op1
        op2 = id_ex_latch.op2
        op = id_ex_latch.op

        result = function_tbl[op](op1, op2)
        self.logr.debug(f"Result of {op} is: {result}")

        return EX_MEM_Latch(
            op=op,
            rs1=id_ex_latch.rs1,
            rs2=id_ex_latch.rs2,
            rd=id_ex_latch.rd,
            imm=id_ex_latch.imm,
            result=result,
            pc=id_ex_latch.pc,
        )

    def update_pc(self, ex_mem_latch: EX_MEM_Latch) -> PC_IF_Latch:
        """
        Update PC to take a branch or jump
        """
        op = ex_mem_latch.op
        result = ex_mem_latch.result
        imm = ex_mem_latch.imm if ex_mem_latch.imm else 0
        pc = ex_mem_latch.pc

        self.logr.debug(isinstance(op, Branch_ops))

        if (op is Jump_ops.JAL) or (op is Imm_ops.JALR):
            next_pc = result
            self.logr.debug(f"Written {result} to next PC.")
            return PC_IF_Latch(pc=next_pc)

        if isinstance(op, Branch_ops):
            if result:
                next_pc = pc + imm
                self.logr.debug(f"PC += imm, {pc} --> {next_pc}")
                return PC_IF_Latch(pc=next_pc)
            else:
                next_pc = pc + 4
                self.logr.debug(f"PC += 4, {pc} --> {next_pc}")
                return PC_IF_Latch(pc=next_pc)
        else:
            next_pc = pc + 4
            self.logr.debug(f"PC += 4, {pc} --> {next_pc}")
            return PC_IF_Latch(pc=next_pc)

    def mem_access(self, ex_mem_latch: EX_MEM_Latch) -> MEM_WB_Latch:
        """
        Access memory based on the instruction.
        """
        op = ex_mem_latch.op
        addr = ex_mem_latch.result

        loaded_data = 0

        # Handle load instructions
        if isinstance(op, Load_ops):
            match op:
                case Load_ops.LBU:
                    loaded_data = self.mem.read_byte(addr)
                case Load_ops.LB:
                    loaded_data = sign_extend(self.mem.read_byte(addr), XWIDTH // 4)
                case Load_ops.LHU:
                    loaded_data = self.mem.read_halfword(addr)
                case Load_ops.LH:
                    loaded_data = sign_extend(self.mem.read_halfword(addr), XWIDTH // 2)
                case Load_ops.LW:
                    loaded_data = self.mem.read_word(addr)

            return MEM_WB_Latch(
                op=op,
                rs2=ex_mem_latch.rs2,
                rd=ex_mem_latch.rd,
                result=ex_mem_latch.result,
                loaded_data=loaded_data,
                pc=ex_mem_latch.pc,
            )

        # Handle store instructions
        if isinstance(op, Store_ops):
            rs2 = ex_mem_latch.rs2 if ex_mem_latch.rs2 else 0
            data = self.regfile.read(rs2)

            match op:
                case Store_ops.SB:
                    self.mem.write_byte(addr, data)
                case Store_ops.SH:
                    self.mem.write_halfword(addr, data)
                case Store_ops.SW:
                    self.mem.write_word(addr, data)

            return MEM_WB_Latch(
                op=op,
                rs2=ex_mem_latch.rs2,
                rd=ex_mem_latch.rd,
                result=ex_mem_latch.result,
                loaded_data=None,
                pc=ex_mem_latch.pc,
            )

        return MEM_WB_Latch(
            op=op,
            rs2=ex_mem_latch.rs2,
            rd=ex_mem_latch.rd,
            result=ex_mem_latch.result,
            loaded_data=None,
            pc=ex_mem_latch.pc,
        )

    def writeback(self, mem_wb_latch: MEM_WB_Latch, pc_if_latch: PC_IF_Latch) -> None:
        """
        Write the result of the operation back to the register.
        """
        # NOTE: CAUTION - Changing the outputs here will violate test cases
        result = mem_wb_latch.result
        op = mem_wb_latch.op
        rd = mem_wb_latch.rd if mem_wb_latch.rd else 0
        pc = mem_wb_latch.pc
        next_pc = pc_if_latch.pc

        # Branch instructions
        if isinstance(op, Branch_ops):
            self.logr.out(
                f"{pc:08x} | "
                + f"next_pc = {next_pc:08x} | "
                + f"x? = {0:08x} | "
                + f"mem[?] = {0:08x}"
            )
            return

        # Jump instruction
        if isinstance(op, Jump_ops) or op is Imm_ops.JALR:
            # Compute v_rd as pc + 4 parallely (in hardware this would be done
            # by an accelerator)
            v_rd = pc + 4

            self.regfile.write(rd, v_rd)
            self.logr.out(
                f"{pc:08x} | "
                + f"next_pc = {next_pc:08x} | "
                + f"x{rd} = {self.regfile.read(rd):08x} | "
                + f"mem[?] = {0:08x}"
            )
            return

        if isinstance(op, Load_ops):
            loaded_data = mem_wb_latch.loaded_data
            result = mem_wb_latch.result

            if not loaded_data:
                loaded_data = 0

            self.regfile.write(rd, loaded_data)

            self.logr.out(
                f"{pc:08x} | "
                + f"next_pc = {next_pc:08x} | "
                + f"x{rd} = {self.regfile.read(rd):08x} | "
                + f"mem[{result:08x}] => {loaded_data:08x}"
            )
            return

        if isinstance(op, Store_ops):
            result = mem_wb_latch.result
            rs2 = mem_wb_latch.rs2

            data = self.regfile.read(rs2 if rs2 else 0)

            self.logr.out(
                f"{pc:08x} | "
                + f"next_pc = {next_pc:08x} | "
                + f"x? = {0:08x} | "
                + f"mem[{result:08x}] <= {data:08x}"
            )
            return

        # if is_unimplemented(inst):
        #     self.logr.out(
        #         f"{self.curr_pc:08x} | "
        #         + f"next_pc = {self.pc:08x} | "
        #         + f"x? = {0:08x} | "
        #         + f"mem[?] = {0:08x} *unimplemented*"
        #     )
        #     return

        # All other instructions
        rd = mem_wb_latch.rd if mem_wb_latch.rd else 0
        self.regfile.write(rd, result)
        self.logr.out(
            f"{pc:08x} | "
            + f"next_pc = {next_pc:08x} | "
            + f"x{rd} = {self.regfile.read(rd):08x} | "
            + f"mem[?] = {0:08x}"
        )

    @abstractmethod
    def run(self, num_insts: int):
        """Run the processor. To be implemented by subclasses."""
        pass
