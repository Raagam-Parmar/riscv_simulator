from typing import Tuple

from dataclasses import dataclass
from enum import Enum, auto

from ram import RAM
from logger import PR5Logger
from stats import Statistics
from .processor import *
from decode.disassembler import disassemble_error, InvalidInstruction
from isa.properties import *


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


# class Hazard(Enum):
#     NO_HAZARD = auto()
#     READ_AFTER_WRITE = auto()
#     BRANCH = auto()


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
            return None

        inst = if_id.inst
        dis = disassemble_error(inst)

        pipeline_control = PipelineControl(
            pc_if=LatchControl.STALL,
            if_id=LatchControl.STALL,
            id_ex=LatchControl.CONTD,
            ex_mem=LatchControl.CONTD,
            mem_wb=LatchControl.CONTD,
        )

        if id_ex is not None and has_rd(id_ex.inst):
            if (has_rs1(dis) and (dis.rs1 == id_ex.inst.rd)) or (
                has_rs2(dis) and (dis.rs2 == id_ex.inst.rd)
            ):
                return pipeline_control

        if ex_mem is not None and has_rd(ex_mem.inst):
            if (has_rs1(dis) and (dis.rs1 == ex_mem.inst.rd)) or (
                has_rs2(dis) and (dis.rs2 == ex_mem.inst.rd)
            ):
                return pipeline_control

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
                return PipelineControl(
                    pc_if=LatchControl.STALL,
                    if_id=LatchControl.FLUSH,
                    id_ex=LatchControl.CONTD,
                    ex_mem=LatchControl.CONTD,
                    mem_wb=LatchControl.CONTD,
                )

        if id_ex is not None and modifies_pc(id_ex.inst):
            return PipelineControl(
                pc_if=LatchControl.STALL,
                if_id=LatchControl.FLUSH,
                id_ex=LatchControl.FLUSH,
                ex_mem=LatchControl.CONTD,
                mem_wb=LatchControl.CONTD,
            )

        if ex_mem is not None and modifies_pc(ex_mem.inst):
            return PipelineControl(
                pc_if=LatchControl.STALL,
                if_id=LatchControl.FLUSH,
                id_ex=LatchControl.FLUSH,
                ex_mem=LatchControl.FLUSH,
                mem_wb=LatchControl.CONTD,
            )

        return None

    # TODO branch OF jump. introduce bubbles, dont flush.

    def hazard_detection_unit(self, latches: PipelineLatches) -> PipelineControl:
        """
        Given a CPU state, detects the possible hazards.

        :param latches: The current state of the pipelined CPU

        :returns: The updation control signals for the five latches.
        """

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

    def decode_pipelined(
        self,
        latches: PipelineLatches,
    ) -> Optional[ID_EX_Latch]:
        # decode the instruction and also check for a RAW / Load-read hazard, in
        # case of which return None, otherwise return the next latch object.
        if_id = latches.if_id
        id_ex = latches.id_ex
        ex_mem = latches.ex_mem

        if if_id is None:
            self.logr.debug("[D] Nothing to decode")
            return None

        inst = if_id.inst
        try:
            dis = disassemble_error(inst)
        except InvalidInstruction as e:
            print(e)
            print(if_id.pc)
            exit(1)

        self.logr.debug(f"[D] Decoded instruction {dis}")

        if id_ex is not None and has_rd(id_ex.inst):
            if (has_rs1(dis) and (dis.rs1 == id_ex.inst.rd)) or (
                has_rs2(dis) and (dis.rs2 == id_ex.inst.rd)
            ):
                self.logr.debug(f"    (o) Bubble introduced in ID/EX")
                return None

        if ex_mem is not None and has_rd(ex_mem.inst):
            if (has_rs1(dis) and (dis.rs1 == ex_mem.inst.rd)) or (
                has_rs2(dis) and (dis.rs2 == ex_mem.inst.rd)
            ):
                self.logr.debug(f"    (o) Bubble introduced in ID/EX")
                return None

        next_id_ex = self.operand_fetch(dis, if_id)
        return next_id_ex

    def execute_pipelined(self, latches: PipelineLatches) -> Optional[EX_MEM_Latch]:
        id_ex = latches.id_ex

        if id_ex is None:
            self.logr.debug(f"[E] Nothing to compute")
            return None

        return self.execute(id_ex)

    def mem_access_pipelined(self, latches: PipelineLatches) -> Optional[MEM_WB_Latch]:
        ex_mem = latches.ex_mem

        if ex_mem is None:
            self.logr.debug(f"[M] Nothing for memory access")
            return None

        return self.mem_access(ex_mem)

    def update_pc_pipelined(self, latches: PipelineLatches) -> PC_IF_Latch:
        pc = latches.pc_if.pc
        ex_mem = latches.ex_mem

        if ex_mem is None:
            self.logr.debug(f"[U] PC = PC + 4")
            return PC_IF_Latch(pc=pc + 4)

        return self.update_pc(ex_mem)

    def writeback_pipelined(self, latches: PipelineLatches) -> None:
        mem_wb = latches.mem_wb

        if mem_wb is None:
            self.logr.debug(f"[W] Nothing to writeback")
            return

        self.writeback(mem_wb)

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
            curr_pc_if = latches.pc_if

            self.logr.debug(f"+------- CC {i_cnt} -------+")

            next_if_id = self.fetch(curr_pc_if)
            self.writeback_pipelined(latches)
            next_id_ex = self.decode_pipelined(latches)
            next_ex_mem = self.execute_pipelined(latches)
            next_mem_wb = self.mem_access_pipelined(latches)
            next_pc_if = self.update_pc_pipelined(latches)

            if self._hazard_control(latches):
                # Flush the previous three instructions in case of a branch instruction
                next_if_id = None
                next_id_ex = None
                next_ex_mem = None
                self.logr.debug("[H] Branch detected at EX/MEM")
                self.logr.debug("    Flushing latches (a) IF/ID (b) ID/EX (c) EX/MEM")

            latches = PipelineLatches(
                pc_if=next_pc_if,
                if_id=next_if_id,
                id_ex=next_id_ex,
                ex_mem=next_ex_mem,
                mem_wb=next_mem_wb,
            )

            self.logr.debug("")

            i_cnt = i_cnt + 1
