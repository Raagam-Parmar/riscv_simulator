# TODO register should not be 0 for data hazard
# TODO use my custom pretty printer instead of hex

from dataclasses import dataclass
from enum import Enum, auto

from src.hardware.ram import RAM
from src.utils.logger import PR5Logger
from src.utils.stats import Statistics
from src.processor.base import *
from src.disassembler import disassemble_error
from src.isa.properties import *


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


class PipelinedProcessor(Processor):
    def __init__(self, start: int, ram: RAM, logger: PR5Logger, stats: Statistics):
        super().__init__(start, ram, logger)
        self.stats = stats

    def _hazard_raw(self, latches: PipelineLatches) -> Optional[PipelineControl]:
        """
        Given the CPU state, checks if there is a RAW dependency.

        :param latches: The current state of the pipelined CPU

        :returns: The updation control signals for the five latches if a RAW hazard is
        detected, `None` otherwise.
        """

        if_id = latches.if_id
        id_ex = latches.id_ex
        ex_mem = latches.ex_mem

        if if_id is None:
            self.logr.debug("    No RAW Hazard")
            return None

        inst = if_id.inst
        dis = disassemble_error(inst)

        pipeline_control = PipelineControl(
            pc_if=LatchControl.STALL,
            if_id=LatchControl.STALL,
            id_ex=LatchControl.FLUSH,
            ex_mem=LatchControl.CONTD,
            mem_wb=LatchControl.CONTD,
        )

        if id_ex is not None and has_rd(id_ex.inst):
            if (has_rs1(dis) and (dis.rs1 == id_ex.inst.rd)) or (
                has_rs2(dis) and (dis.rs2 == id_ex.inst.rd)
            ):
                self.logr.debug("    RAW hazard: IF/ID and ID/EX")
                return pipeline_control

        if ex_mem is not None and has_rd(ex_mem.inst):
            if (has_rs1(dis) and (dis.rs1 == ex_mem.inst.rd)) or (
                has_rs2(dis) and (dis.rs2 == ex_mem.inst.rd)
            ):
                self.logr.debug("    RAW hazard: IF/ID and EX/MEM")
                return pipeline_control

        self.logr.debug("    No RAW hazard")
        return None

    def _hazard_control(self, latches: PipelineLatches) -> Optional[PipelineControl]:
        """
        Given a CPU state, checks if there is control hazard.

        :param latches: The current state of the pipelined CPU

        :returns: The updation control signals for the five latches if a control hazard
        is detected, `None` otherwise.
        """
        if_id = latches.if_id
        id_ex = latches.id_ex
        ex_mem = latches.ex_mem

        if if_id is not None:
            dis = disassemble_error(if_id.inst)
            if modifies_pc(dis):
                self.logr.debug("    Control hazard: PC modifying instruction in IF/ID")
                return PipelineControl(
                    pc_if=LatchControl.STALL,
                    if_id=LatchControl.FLUSH,
                    id_ex=LatchControl.CONTD,
                    ex_mem=LatchControl.CONTD,
                    mem_wb=LatchControl.CONTD,
                )

        if id_ex is not None and modifies_pc(id_ex.inst):
            self.logr.debug("    Control hazard: PC modifying instruction in ID/EX")
            return PipelineControl(
                pc_if=LatchControl.STALL,
                if_id=LatchControl.FLUSH,
                id_ex=LatchControl.FLUSH,
                ex_mem=LatchControl.CONTD,
                mem_wb=LatchControl.CONTD,
            )

        if ex_mem is not None and modifies_pc(ex_mem.inst):
            self.logr.debug("    Control hazard: PC modifying instruction in EX/MEM")
            return PipelineControl(
                pc_if=LatchControl.CONTD,
                if_id=LatchControl.FLUSH,
                id_ex=LatchControl.FLUSH,
                ex_mem=LatchControl.FLUSH,
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

        hazard_raw = self._hazard_raw(latches)
        hazard_control = self._hazard_control(latches)

        hazard_safe = PipelineControl(
            pc_if=LatchControl.CONTD,
            if_id=LatchControl.CONTD,
            id_ex=LatchControl.CONTD,
            ex_mem=LatchControl.CONTD,
            mem_wb=LatchControl.CONTD,
        )

        if hazard_raw:
            return hazard_raw

        if hazard_control:
            return hazard_control

        return hazard_safe

    def fetch_pipelined(
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

    def decode_pipelined(
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

    def execute_pipelined(
        self, latches: PipelineLatches, controls: PipelineControl
    ) -> Optional[EX_MEM_Latch]:
        """
        Given the current state of the CPU, and a summary of the updation controls,
        determines the next EX/MEM latch.

        :param latches: The current state of the CPU
        :param controls Updation controls for the pipeline
        """

        id_ex = latches.id_ex
        ex_mem = latches.ex_mem

        match controls.ex_mem:
            case LatchControl.STALL:
                self.logr.debug("[E] Stalling EX/MEM")
                return ex_mem

            case LatchControl.FLUSH:
                self.logr.debug("[E] Flushing EX/MEM")
                return None

            case LatchControl.CONTD:
                if id_ex is None:
                    self.logr.debug(f"[E] Bubble in EX/MEM")
                    return None

                return self.execute(id_ex)

    def mem_access_pipelined(
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

    def update_pc_pipelined(
        self, latches: PipelineLatches, controls: PipelineControl
    ) -> PC_IF_Latch:
        """
        Given the current state of the CPU, and a summary of the updation controls,
        determines the next PC/IF latch.

        :param latches: The current state of the CPU
        :param controls Updation controls for the pipeline
        """

        pc_if = latches.pc_if
        ex_mem = latches.ex_mem

        match controls.pc_if:
            case LatchControl.STALL:
                self.logr.debug("[U] Stalling PC/IF")
                return pc_if

            case LatchControl.FLUSH:
                raise RuntimeError(
                    "[Bug] Unreachable code path. PC/IF latch should never be flushed."
                )

            case LatchControl.CONTD:
                if ex_mem is None:
                    self.logr.debug(f"[U] Bubble in EX/MEM")
                    self.logr.debug(f"    Advancing: PC = PC + 4")
                    return PC_IF_Latch(pc=pc_if.pc + 4)

                if not modifies_pc(ex_mem.inst):
                    self.logr.debug(
                        f"[U] Discarding PC update of a non-jump instruction"
                    )
                    self.logr.debug(f"    Advancing: PC = PC + 4")
                    return PC_IF_Latch(pc=pc_if.pc + 4)

                return self.update_pc(ex_mem)

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

        pretty_pc_if = hex(curr_pc_if.pc) if curr_pc_if else "( )"
        pretty_if_id = hex(curr_if_id.pc) if curr_if_id else "( )"
        pretty_id_ex = hex(curr_id_ex.pc) if curr_id_ex else "( )"
        pretty_ex_mem = hex(curr_ex_mem.pc) if curr_ex_mem else "( )"
        pretty_mem_wb = hex(curr_mem_wb.pc) if curr_mem_wb else "( )"

        self.logr.debug(f"PC/IF  {pretty_pc_if}")
        self.logr.debug(f"IF/ID  {pretty_if_id}")
        self.logr.debug(f"ID/EX  {pretty_id_ex}")
        self.logr.debug(f"EX/MEM {pretty_ex_mem}")
        self.logr.debug(f"MEM/WB {pretty_mem_wb}")

    def run(self, num_insts: int):
        """
        Run a 5-stage pipelined processor.
        """
        # TODO: Complete this function in such a way that the statistics file
        # (stats.json) has the correct cycle count when the program is executed
        # on a simple 5-stage pipeline without any forwarding or bypass
        # mechanism implemented. Assume that the targetPC is generated after
        # the EX stage (there will be three wrong-path instructions in case of
        # a control hazard). You should change the interfaces of fetch(),
        # decode(), operand_fetch(), execute(), update_pc(), mem_access(), and
        # reg_write() functions of the Processor base class as needed, and
        # update the code of the SingleCycleProcessor appropriately. Refrain
        # from changing the output formats of the [OUT] messages printed from
        # the reg_write() function. You can ignore counting the number of
        # memory accesses for now.
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
            next_if_id = self.fetch_pipelined(latches, controls)
            next_id_ex = self.decode_pipelined(latches, controls)
            next_ex_mem = self.execute_pipelined(latches, controls)
            next_mem_wb = self.mem_access_pipelined(latches, controls)
            next_pc_if = self.update_pc_pipelined(latches, controls)

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
