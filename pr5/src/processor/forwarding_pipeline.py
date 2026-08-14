from dataclasses import dataclass
from enum import Enum, auto

from src.utils.logger import PR5Logger
from src.utils.stats import Statistics
from src.processor.base import *
from src.disassembler import disassemble_error
from src.isa.properties import *
from src.hardware.alu import *
from src.hardware.memory.hierarchy import MemoryHierarchy


@dataclass(frozen=True)
class PipelineLatches:
    """
    Various Latches for a pipelined processor.
    `None` represents a pipeline bubble.
    """

    pc_if: PC_IF_Latch
    if_id: Optional[IF_ID_Latch]
    id_ex: Optional[ID_EX_Latch]
    ex_mem: Optional[EX_MEM_Latch]
    mem_wb: Optional[MEM_WB_Latch]


class LatchControl(Enum):
    """
    Determines what should be done with a given pipeline latch.
    - `STALL`: Keep the latch value as is
    - `FLUSH`: Reset the latch to `None` (i.e. remove all information)
    - `CONTD`: Continue normal execution
    """

    STALL = auto()
    FLUSH = auto()
    CONTD = auto()


@dataclass(frozen=True)
class PipelineControl:
    """
    Information on which latches need to be flushed.
    - `True` means flush the latch
    - `False` means do not flush the latch
    """

    pc_if: LatchControl
    if_id: LatchControl
    id_ex: LatchControl
    ex_mem: LatchControl
    mem_wb: LatchControl


class ForwardingPipelined(Processor):
    def __init__(
        self, start: UInt32, mem: MemoryHierarchy, logger: PR5Logger, stats: Statistics
    ):
        super().__init__(start, mem, logger)
        self.stats = stats

    def execute_pipelined(self, latches: PipelineLatches) -> Optional[EX_MEM_Latch]:
        id_ex = latches.id_ex
        ex_mem = latches.ex_mem
        mem_wb = latches.mem_wb

        if id_ex is None:
            self.logr.debug("[FWD1] Bubble in ID/EX. Nothing to forward for.")
            return None

        op1 = id_ex.op1
        op2 = id_ex.op2

        self.logr.debug("[FWD1] Forwarding paths in priority EX/MEM > MEM/WB to EX")

        if (
            ex_mem is not None
            and has_rd(ex_mem.inst)
            and has_rs1(id_ex.inst)
            and ex_mem.inst.rd == id_ex.inst.rs1
            and id_ex.inst.rs1 != 0
        ):
            # EX <-- rs1 --- EX/MEM
            op1 = ex_mem.result
            self.logr.debug(f"       EX <-- rs1 = x{id_ex.inst.rs1} --- EX/MEM")
            self.logr.debug(f"       op1 = v_rs1 = {op1}")

        elif (
            mem_wb is not None
            and has_rd(mem_wb.inst)
            and has_rs1(id_ex.inst)
            and mem_wb.inst.rd == id_ex.inst.rs1
            and id_ex.inst.rs1 != 0
            and (not isinstance(id_ex.inst, (Upper_imm, Jal)))
        ):
            # EX <-- rs1 --- . ----------- MEM/WB
            if isinstance(mem_wb.inst, Load):
                op1 = mem_wb.loaded_data or uint32(0)  # TODO Fix this.
            else:
                op1 = mem_wb.result

            self.logr.debug(
                f"       EX <-- rs1 = x{id_ex.inst.rs1} --- . ----------- MEM/WB"
            )
            self.logr.debug(f"       op1 = v_rs1 = {op1}")

        else:
            self.logr.debug("       Can not forward for rs1")
            pass

        if (
            ex_mem is not None
            and has_rd(ex_mem.inst)
            and has_rs2(id_ex.inst)
            and ex_mem.inst.rd == id_ex.inst.rs2
            and id_ex.inst.rs2 != 0
            and isinstance(id_ex.inst, (Reg_reg, Branch))
        ):
            # EX <-- rs2 --- EX/MEM
            op2 = ex_mem.result
            self.logr.debug(f"       EX <-- rs2 = x{id_ex.inst.rs2} --- EX/MEM")
            self.logr.debug(f"       op2 = v_r2 = {op2}")

        elif (
            mem_wb is not None
            and has_rd(mem_wb.inst)
            and has_rs2(id_ex.inst)
            and mem_wb.inst.rd == id_ex.inst.rs2
            and id_ex.inst.rs2 != 0
            and isinstance(id_ex.inst, Reg_reg)
        ):
            # EX <-- rs2 --- . ----------- EX/MEM
            if isinstance(mem_wb.inst, Load):
                op2 = mem_wb.loaded_data or uint32(0)  # TODO Fix this.
            else:
                op2 = mem_wb.result

            self.logr.debug(
                f"       EX <-- rs2 = x{id_ex.inst.rs2} --- . ----------- MEM/WB"
            )
            self.logr.debug(f"       op2 = v_r2 = {op2}")

        else:
            self.logr.debug("       Can not forward for rs2")
            pass

        id_ex_forwarded = ID_EX_Latch(inst=id_ex.inst, op1=op1, op2=op2, pc=id_ex.pc)

        return self.execute(id_ex_forwarded)

    def update_pc_pipelined(self, latches: PipelineLatches) -> PC_IF_Latch:
        pc_if = latches.pc_if
        if_id = latches.if_id
        ex_mem = latches.ex_mem

        if if_id is None:
            self.logr.debug("[U] Bubble in EX/MEM")
            self.logr.debug(f"    Advancing: PC = PC + 4")
            return PC_IF_Latch(pc=pc_if.pc + 4)

        if_id_inst = disassemble_error(if_id.inst)
        pc = if_id.pc if modifies_pc(if_id_inst) else pc_if.pc

        next_pc = pc + uint32(4)
        pc_src = PCSource.PLUS_4

        cmp1: UInt32
        cmp2: UInt32

        self.logr.debug(f"[FWD2] Checking for forwarding paths from EX/MEM to ID")

        match if_id_inst:
            case Branch():
                op = if_id_inst.op
                imm = if_id_inst.imm
                pc = if_id.pc

                rs1 = if_id_inst.rs1
                rs2 = if_id_inst.rs2

                cmp1 = self.regfile.read(rs1)
                cmp2 = self.regfile.read(rs2)

                if (
                    ex_mem is not None
                    and has_rs1(if_id_inst)
                    and has_rd(ex_mem.inst)
                    and if_id_inst.rs1 == ex_mem.inst.rd
                    and if_id_inst.rs1 != 0
                ):
                    self.logr.debug(f"       Forwarding for rs1:x{if_id_inst.rs1}")
                    cmp1 = ex_mem.result

                if (
                    ex_mem is not None
                    and has_rs2(if_id_inst)
                    and has_rd(ex_mem.inst)
                    and if_id_inst.rs2 == ex_mem.inst.rd
                    and if_id_inst.rs2 != 0
                ):
                    self.logr.debug(f"       Forwarding for rs2:x{if_id_inst.rs2}")
                    cmp2 = ex_mem.result

                branch_taken = target_pc(cmp1, cmp2, op)
                self.logr.debug(f"       Branch taken: {branch_taken}")

                if branch_taken != 0:
                    next_pc = pc + uint32(imm)
                    pc_src = PCSource.IMM
                    self.logr.debug(f"       Rewritten next_pc by Branch")

            case Jalr():
                op1 = self.regfile.read(if_id_inst.rs1)
                op2 = uint32(if_id_inst.imm)

                if (
                    ex_mem is not None
                    and has_rd(ex_mem.inst)
                    and ex_mem.inst.rd == if_id_inst.rs1
                    and ex_mem.inst.rd != 0
                ):
                    self.logr.debug(f"       Forwarding for x{ex_mem.inst.rd}")
                    self.logr.debug(ex_mem)
                    op1 = ex_mem.result

                next_pc = target_pc(op1, op2, if_id_inst.op)
                self.logr.debug(
                    f"       [jalr] Target PC = op1 + op2 = {op1} + {op2} = {next_pc}"
                )
                pc_src = PCSource.BRANCH_TARGET
                self.logr.debug(f"       Rewritten next_pc by Jalr")

            case Jal():
                op1 = if_id.pc
                op2 = uint32(if_id_inst.imm)
                next_pc = target_pc(op1, op2, if_id_inst.op)
                pc_src = PCSource.BRANCH_TARGET
                self.logr.debug(f"       Rewritten next_pc by Jal")

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

    def _load_use_dependency(self, inst1: Instruction, inst2: Instruction) -> bool:
        """
        Checks if there is a load-use dependency, i.e., is `inst2` a load instruction,
        and `inst1` trying to read from the non-zero destination register of `inst2`?

        :param inst1: Dependent instruction
        :param inst2: Independent instruction

        :return: `True` if dependent, else `False`
        """

        if not isinstance(inst2, Load):
            return False

        if inst2.rd == 0:
            return False

        return (has_rs1(inst1) and inst1.rs1 == inst2.rd) or (
            has_rs2(inst1) and inst1.rs2 == inst2.rd
        )

    def _write_jump_dependency(self, inst1: Instruction, inst2: Instruction) -> bool:
        """
        Checks if there is a write-branch dependency, i.e, is `inst1` a branch
        instruction, and `inst2` writes to a non-zero destination register, which
        is also read by `inst1`?

        :param inst1: Dependent Instruction
        :param inst2: Independent Instruction

        :return: `True` if dependent, else `False`
        """

        if modifies_pc(inst1) and has_rd(inst2) and inst2.rd != 0:
            match inst1:
                case Branch():
                    return inst1.rs1 == inst2.rd or inst1.rs2 == inst2.rd
                case Jalr():
                    return inst1.rs1 == inst2.rd
                case Jal():
                    return False

        return False

    def _load_jump_dependency(self, inst1: Instruction, inst2: Instruction) -> bool:
        """
        Checks if there is a load-branch dependency, i.e., is `inst1` a branch
        instruction, and `inst2` a load instruction, such that `inst1` is reading
        a non-zero destination register of `inst2`?

        :param isnt1: Dependent Instruction
        :param inst2: Independent Instruction

        :return: `True` is dependent, else `False`
        """

        if modifies_pc(inst1) and isinstance(inst2, Load) and inst2.rd != 0:
            match inst1:
                case Branch():
                    return inst1.rs1 == inst2.rd or inst1.rs2 == inst2.rd
                case Jalr():
                    return inst1.rs1 == inst2.rd
                case Jal():
                    return False

        return False

    def _hazard_data(self, latches: PipelineLatches) -> Optional[PipelineControl]:
        """
        Given the CPU state, checks if there is a data hazard.

        :param latches: The current state of the pipelined CPU

        :returns: The updation control signals for the five latches if a RAW hazard is
        detected, `None` otherwise.
        """

        if_id = latches.if_id
        id_ex = latches.id_ex
        ex_mem = latches.ex_mem

        if if_id is None:
            self.logr.debug("    No data Hazard")
            return None

        inst = if_id.inst
        if_id_inst = disassemble_error(inst)

        stall_by_id_ex = PipelineControl(
            pc_if=LatchControl.STALL,
            if_id=LatchControl.STALL,
            id_ex=LatchControl.FLUSH,
            ex_mem=LatchControl.CONTD,
            mem_wb=LatchControl.CONTD,
        )

        if id_ex is not None:
            if self._load_use_dependency(if_id_inst, id_ex.inst):
                self.logr.debug("    Data Hazard: Load-use, IF/ID depends on ID/EX")
                return stall_by_id_ex

            if self._write_jump_dependency(if_id_inst, id_ex.inst):
                self.logr.debug("    Data Hazard: Write-branch, IF/ID depends on ID/EX")
                return stall_by_id_ex

        if ex_mem is not None:
            if self._load_jump_dependency(if_id_inst, ex_mem.inst):
                self.logr.debug("    Data Hazard: Load-branch, IF/ID depends on EX/MEM")
                return stall_by_id_ex

        self.logr.debug("    No data hazard")
        return None

    def _hazard_control(self, latches: PipelineLatches) -> Optional[PipelineControl]:
        """
        Given a CPU state, checks if there is control hazard.

        :param latches: The current state of the pipelined CPU

        :returns: The updation control signals for the five latches if a control hazard
        is detected, `None` otherwise.
        """
        if_id = latches.if_id

        if if_id is not None:
            if_id_inst = disassemble_error(if_id.inst)
            if modifies_pc(if_id_inst):
                self.logr.debug("    Control hazard: PC modifying instruction in IF/ID")
                return PipelineControl(
                    pc_if=LatchControl.CONTD,
                    if_id=LatchControl.FLUSH,
                    id_ex=LatchControl.CONTD,
                    ex_mem=LatchControl.CONTD,
                    mem_wb=LatchControl.CONTD,
                )

        self.logr.debug("    No control hazard")
        return None

    def hazard_detection_unit(self, latches: PipelineLatches) -> PipelineControl:
        """
        Given a CPU state, detects the possible hazards.

        :param latches: The current state of the pipelined CPU

        :returns: The updation control signals for the five latches.
        """

        self.logr.debug("[H] Detected hazards:")

        hazard_data = self._hazard_data(latches)
        hazard_control = self._hazard_control(latches)

        hazard_safe = PipelineControl(
            pc_if=LatchControl.CONTD,
            if_id=LatchControl.CONTD,
            id_ex=LatchControl.CONTD,
            ex_mem=LatchControl.CONTD,
            mem_wb=LatchControl.CONTD,
        )

        if hazard_data is not None:
            return hazard_data

        if hazard_control is not None:
            return hazard_control

        return hazard_safe

    def fetch_controlled(
        self, latches: PipelineLatches, controls: PipelineControl
    ) -> Optional[IF_ID_Latch]:
        """
        Given the current state of the CPU, and a summary of the updation controls,
        determines the next IF/ID latch.

        :param latches: The current state of the CPU
        :param controls Updation controls for the pipeline
        """

        pc_if = latches.pc_if
        if_id = latches.if_id

        match controls.if_id:
            case LatchControl.STALL:
                self.logr.debug("[F] Stalling IF/ID")
                return if_id

            case LatchControl.FLUSH:
                self.logr.debug("[F] Flushing IF/ID")
                return None

            case LatchControl.CONTD:
                return self.fetch(pc_if)

    def decode_controlled(
        self, latches: PipelineLatches, controls: PipelineControl
    ) -> Optional[ID_EX_Latch]:
        """
        Given the current state of the CPU, and a summary of the updation controls,
        determines the next ID/EX latch.

        :param latches: The current state of the CPU
        :param controls Updation controls for the pipeline
        """

        if_id = latches.if_id
        id_ex = latches.id_ex

        match controls.id_ex:
            case LatchControl.STALL:
                self.logr.debug("[D] Stalling ID/EX")
                return id_ex

            case LatchControl.FLUSH:
                self.logr.debug("[D] Flushing ID/EX")
                return None

            case LatchControl.CONTD:
                if if_id is None:
                    self.logr.debug("[D] Bubble in ID/EX")
                    return None

                dis = self.decode(if_id)
                return self.operand_fetch(dis, if_id)

    def execute_controlled(
        self, latches: PipelineLatches, controls: PipelineControl
    ) -> Optional[EX_MEM_Latch]:
        """
        Given the current state of the CPU, and a summary of the updation controls,
        determines the next EX/MEM latch.

        :param latches: The current state of the CPU
        :param controls Updation controls for the pipeline
        """

        ex_mem = latches.ex_mem

        match controls.ex_mem:
            case LatchControl.STALL:
                self.logr.debug("[E] Stalling EX/MEM")
                return ex_mem

            case LatchControl.FLUSH:
                self.logr.debug("[E] Flushing EX/MEM")
                return None

            case LatchControl.CONTD:
                return self.execute_pipelined(latches)

    def mem_access_controlled(
        self, latches: PipelineLatches, controls: PipelineControl
    ) -> Optional[MEM_WB_Latch]:
        """
        Given the current state of the CPU, and a summary of the updation controls,
        determines the next MEM/WB latch.

        :param latches: The current state of the CPU
        :param controls Updation controls for the pipeline
        """

        ex_mem = latches.ex_mem
        mem_wb = latches.mem_wb

        match controls.mem_wb:
            case LatchControl.STALL:
                self.logr.debug("[M] Stalling MEM/WB")
                return mem_wb

            case LatchControl.FLUSH:
                self.logr.debug("[M] Flushing MEM/WB")
                return None

            case LatchControl.CONTD:
                if ex_mem is None:
                    self.logr.debug(f"[M] Bubble in MEM/WBs")
                    return None

                return self.mem_access(ex_mem)

    def update_pc_controlled(
        self, latches: PipelineLatches, controls: PipelineControl
    ) -> PC_IF_Latch:
        """
        Given the current state of the CPU, and a summary of the updation controls,
        determines the next PC/IF latch.

        :param latches: The current state of the CPU
        :param controls Updation controls for the pipeline
        """

        pc_if = latches.pc_if

        match controls.pc_if:
            case LatchControl.STALL:
                self.logr.debug("[U] Stalling PC/IF")
                return pc_if

            case LatchControl.FLUSH:
                raise RuntimeError(
                    "[Bug] Unreachable code path. PC/IF latch should never be flushed."
                )

            case LatchControl.CONTD:
                return self.update_pc_pipelined(latches)

    def writeback_pipelined(self, latches: PipelineLatches) -> None:
        """
        Given the current state of the CPU, performs register-file writeback.

        :param latches: The current state of the CPU
        """

        mem_wb = latches.mem_wb

        if mem_wb is None:
            self.logr.debug(f"[W] Bubble in MEM/WB")
            return

        self.writeback(mem_wb)

    def pretty_pipeline(self, latches: PipelineLatches) -> None:
        curr_pc_if = latches.pc_if
        curr_if_id = latches.if_id
        curr_id_ex = latches.id_ex
        curr_ex_mem = latches.ex_mem
        curr_mem_wb = latches.mem_wb

        pretty_pc_if = uint32(curr_pc_if.pc) if curr_pc_if else "( )"
        pretty_if_id = uint32(curr_if_id.pc) if curr_if_id else "( )"
        pretty_id_ex = uint32(curr_id_ex.pc) if curr_id_ex else "( )"
        pretty_ex_mem = uint32(curr_ex_mem.pc) if curr_ex_mem else "( )"
        pretty_mem_wb = uint32(curr_mem_wb.pc) if curr_mem_wb else "( )"

        self.logr.debug(f"PC/IF  {pretty_pc_if}")
        self.logr.debug(f"IF/ID  {pretty_if_id}")
        self.logr.debug(f"ID/EX  {pretty_id_ex}")
        self.logr.debug(f"EX/MEM {pretty_ex_mem}")
        self.logr.debug(f"MEM/WB {pretty_mem_wb}")

    def run(self, num_insts: int):
        """
        Run a 5-stage pipelined processor with forwarding.
        """

        i_cnt = 0
        latches = PipelineLatches(
            pc_if=self.initialise_pc(),
            if_id=None,
            id_ex=None,
            ex_mem=None,
            mem_wb=None,
        )

        while i_cnt < num_insts:
            curr_mem_wb = latches.mem_wb

            self.logr.debug(f"+------- CC {self.stats.clock_cycles} -------+")

            self.pretty_pipeline(latches)

            controls = self.hazard_detection_unit(latches)

            self.writeback_pipelined(latches)
            next_if_id = self.fetch_controlled(latches, controls)
            next_id_ex = self.decode_controlled(latches, controls)
            next_pc_if = self.update_pc_controlled(latches, controls)
            next_ex_mem = self.execute_controlled(latches, controls)
            next_mem_wb = self.mem_access_controlled(latches, controls)

            if curr_mem_wb is not None:
                self.log_instruction(curr_mem_wb, next_pc_if)

            self.logr.debug("")

            latches = PipelineLatches(
                pc_if=next_pc_if,
                if_id=next_if_id,
                id_ex=next_id_ex,
                ex_mem=next_ex_mem,
                mem_wb=next_mem_wb,
            )

            self.stats.increment_clock_cycle()

            if curr_mem_wb is not None:
                i_cnt = i_cnt + 1
                self.stats.increment_instruction_count()
