from dataclasses import dataclass

from ram import RAM
from logger import PR5Logger
from stats import Statistics
from .processor import *


@dataclass(frozen=True)
class PipelineLatches:
    """
    Various Latches for a pipelined processor.
    """

    pc_if: PC_IF_Latch
    if_id: Optional[IF_ID_Latch]
    id_ex: Optional[ID_EX_Latch]
    ex_mem: Optional[EX_MEM_Latch]
    mem_wb: Optional[MEM_WB_Latch]


class PipelinedProcessor(Processor):
    def __init__(
        self, start: int, ram: RAM, logger: PR5Logger, stats: Statistics
    ):
        super().__init__(start, ram, logger)
        self.stats = stats

    # def hazard_detection(self, latches: PipelineLatches):

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
        state = PipelineLatches(
            pc_if=self.initialise_pc(),
            if_id=None,
            id_ex=None,
            ex_mem=None,
            mem_wb=None,
        )

        while i_cnt < num_insts:
            curr_pc_if = state.pc_if
            curr_if_id = state.if_id
            curr_id_ex = state.id_ex
            curr_ex_mem = state.ex_mem
            curr_mem_wb = state.mem_wb

            next_if_id = self.fetch(curr_pc_if)

            next_id_ex = None if curr_if_id is None else self.decode(
                curr_if_id)

            next_ex_mem = (
                None if curr_id_ex is None else self.execute(curr_id_ex)
            )

            next_mem_wb = (
                None if curr_ex_mem is None else self.mem_access(curr_ex_mem)
            )

            next_pc_if = (
                None if curr_ex_mem is None else self.update_pc(curr_ex_mem)
            )

            if curr_mem_wb is not None and next_pc_if is not None:
                self.writeback(curr_mem_wb)

            state = PipelineLatches(
                pc_if=next_pc_if,
                if_id=next_if_id,
                id_ex=next_id_ex,
                ex_mem=next_ex_mem,
                mem_wb=next_mem_wb,
            )
