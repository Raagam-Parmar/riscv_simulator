from abc import ABC, abstractmethod
from .fu import *

# from .riscv_tables import *

from ram import RAM
from logger import PR5Logger
from utils.constants import XWIDTH

# from typs import inst32
from decode.disassembler import disassemble_error
from isa.formats import *
from isa.enums import *
from .reg import *
from .pc import *
from decode.fields import *
from .alu_tables import *
from utils.bits import sign_extend


@dataclass
class IF_ID_Latch:
    inst: int


@dataclass(frozen=True)
class ID_EX_Latch:
    decoded: UnifiedInstruction
    op1: int
    op2: int


@dataclass(frozen=True)
class EX_MEM_Latch:
    decoded: UnifiedInstruction
    result: int


@dataclass(frozen=True)
class MEM_WB_Latch:
    decoded: UnifiedInstruction
    result: int
    loaded_data: Optional[int]


class Processor(ABC):
    def __init__(self, start: int, ram: RAM, logger: PR5Logger) -> None:

        # self.pc      = ProgramCounter(start)
        self.pc: int = start
        self.curr_pc: int = 0
        self.regfile = RegisterFile(XWIDTH, zero_reg=True)
        self.mem = ram
        self.logr = logger

    def fetch(self) -> IF_ID_Latch:
        """
        Fetch the instruction from memory, and update PC
        returns instruction
        """
        try:
            self.curr_pc = self.pc
            instruction = self.mem.read_word(self.curr_pc)
            self.logr.debug(f"got instruction {instruction:08x} at {self.curr_pc:08x}")
            return IF_ID_Latch(inst=instruction)
        except ValueError as e:
            self.logr.error(f"Error fetching instruction at {self.curr_pc:08x}: {e}")
            exit()

    def decode(self, if_id_latch: IF_ID_Latch) -> ID_EX_Latch:
        dis = disassemble_error(if_id_latch.inst)

        self.logr.debug(dis)

        decoded = dis.get_unified()

        rs1 = decoded.rs1
        rs2 = decoded.rs2
        v_imm = decoded.imm if decoded.imm else 0
        op = decoded.op

        v_rs1 = self.regfile.read(rs1) if rs1 is not None else 0
        v_rs2 = self.regfile.read(rs2) if rs2 is not None else 0

        self.logr.debug(f"rs1 = {rs1}, rs2 = {rs2}, imm = {hex(v_imm)}, op = {op}")
        v_pc = self.curr_pc

        # op1, op2 = operands_tbl.get(opcode, (None, None))(
        #     v_rs1, v_rs2, v_imm, v_pc
        # )

        try:
            op1, op2 = operands_tbl[op](v_rs1, v_rs2, v_imm, v_pc)
        except KeyError:
            raise NotImplementedError(f"Op not implemented in operands_tbl: {op}")

        # # NOTE: Modified
        # if op1 >= 0x80000000:
        #     op1 = op1 - (1 << 32)

        # # NOTE: Modified
        # if op2 >= 0x80000000 :
        #     op2 = op2 - (1 << 32)

        self.logr.debug(f"op1: {op1}, op2: {op2}")

        return ID_EX_Latch(decoded=decoded, op1=op1, op2=op2)

    def execute(self, id_ex_latch: ID_EX_Latch) -> EX_MEM_Latch:
        """
        Execute the instruction
        decoded_instr, operand1 and operand2 are returned by previous stages
        returns the result of the operation
        """
        # TODO: alu_function is incomplete. Complete it (without modifying fu.py)
        # NOTE: Modified

        decoded = id_ex_latch.decoded
        op1 = id_ex_latch.op1
        op2 = id_ex_latch.op2

        result = function_tbl[decoded.op](op1, op2)
        self.logr.debug(f"Result of {decoded.op} is: {result}")

        return EX_MEM_Latch(decoded=decoded, result=result)

    def update_pc(self, ex_mem_latch: EX_MEM_Latch) -> None:
        """
        Update PC to take a branch or jump
        """
        # NOTE: Modified
        decoded = ex_mem_latch.decoded
        op = decoded.op
        result = ex_mem_latch.result
        imm = decoded.imm if decoded.imm else 0
        
        self.logr.debug(isinstance(op, Branch_ops))
        
        if (op is Jump_ops.JAL) or (op is Imm_ops.JALR):
            self.pc = result
            self.logr.debug(f'Written {result} to next PC.')
        elif isinstance(op, Branch_ops):
            if result:
                self.logr.debug(f'PC += imm, {self.curr_pc} --> {self.curr_pc + imm}')
                self.pc = self.curr_pc + imm
            else:
                self.logr.debug(f'PC += 4, {self.curr_pc} --> {self.curr_pc + 4}')
                self.pc = self.curr_pc + 4
        else:
            self.logr.debug(f'PC += 4, {self.curr_pc} --> {self.curr_pc + 4}')
            self.pc = self.curr_pc + 4

    def mem_access(self, ex_mem_latch: EX_MEM_Latch) -> MEM_WB_Latch:
        """
        Access memory based on the instruction.
        """
        decoded = ex_mem_latch.decoded
        op = decoded.op
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
                decoded=decoded, result=ex_mem_latch.result, loaded_data=loaded_data
            )

        # Handle store instructions
        if isinstance(op, Store_ops):
            rs2 = decoded.rs2 if decoded.rs2 else 0
            data = self.regfile.read(rs2)

            match op:
                case Store_ops.SB:
                    self.mem.write_byte(addr, data)
                case Store_ops.SH:
                    self.mem.write_halfword(addr, data)
                case Store_ops.SW:
                    self.mem.write_word(addr, data)

            return MEM_WB_Latch(
                decoded=decoded, result=ex_mem_latch.result, loaded_data=None
            )

        return MEM_WB_Latch(
            decoded=decoded, result=ex_mem_latch.result, loaded_data=None
        )

    def writeback(self, mem_wb_latch: MEM_WB_Latch) -> None:
        """
        Write the result of the operation back to the register.
        """
        # NOTE: CAUTION - Changing the outputs here will violate test cases
        decoded = mem_wb_latch.decoded
        result = mem_wb_latch.result
        op = decoded.op
        rd = decoded.rd if decoded.rd else 0

        # Branch instructions
        if isinstance(op, Branch_ops):
            self.logr.out(
                f"{self.curr_pc:08x} | "
                + f"next_pc = {self.pc:08x} | "
                + f"x? = {0:08x} | "
                + f"mem[?] = {0:08x}"
            )
            return

        # Jump instruction
        if isinstance(op, Jump_ops) or op is Imm_ops.JALR:
            # Compute v_rd as pc + 4 parallely (in hardware this would be done 
            # by an accelerator)
            v_rd = self.curr_pc + 4
            
            self.regfile.write(rd, v_rd)
            self.logr.out(
                f"{self.curr_pc:08x} | "
                + f"next_pc = {self.pc:08x} | "
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
                f"{self.curr_pc:08x} | "
                + f"next_pc = {self.pc:08x} | "
                + f"x{rd} = {self.regfile.read(rd):08x} | "
                + f"mem[{result:08x}] => {loaded_data:08x}"
            )
            return

        if isinstance(op, Store_ops):
            decoded = mem_wb_latch.decoded
            result = mem_wb_latch.result
            rs2 = decoded.rs2

            data = self.regfile.read(rs2 if rs2 else 0)

            self.logr.out(
                f"{self.curr_pc:08x} | "
                + f"next_pc = {self.pc:08x} | "
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
        rd = decoded.rd if decoded.rd else 0
        self.regfile.write(rd, result)
        self.logr.out(
            f"{self.curr_pc:08x} | "
            + f"next_pc = {self.pc:08x} | "
            + f"x{rd} = {self.regfile.read(rd):08x} | "
            + f"mem[?] = {0:08x}"
        )

    @abstractmethod
    def run(self, num_insts: int):
        """Run the processor. To be implemented by subclasses."""
        pass
