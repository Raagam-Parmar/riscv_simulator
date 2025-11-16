from src.processor.base import Processor
from src.utils.logger import PR5Logger
from src.utils.stats import Statistics
from src.utils.cint import *
from src.hardware.memory.hierarchy import MemoryHierarchy


class SingleCycleProcessor(Processor):
    def __init__(self, start: UInt32, mem: MemoryHierarchy, logger: PR5Logger, stat: Statistics):
        super().__init__(start, mem, logger)
        self.stats = stat

    def run(self, num_insts: int) -> None:
        """
        Run the processor in a single cycle for each instruction.
        """

        i_cnt = 0
        pc_if = self.initialise_pc()

        while i_cnt < num_insts:
            if_id, if_id_late = self.fetch(pc_if)
            inst = self.decode(if_id)
            id_ex = self.operand_fetch(inst, if_id)
            ex_mem = self.execute(id_ex)
            mem_wb, mem_wb_late = self.mem_access(ex_mem)
            pc_if = self.update_pc(ex_mem)
            self.writeback(mem_wb)
            self.log_instruction(mem_wb, pc_if)

            i_cnt += 1

            late = if_id_late + mem_wb_late + 1

            self.stats.increment_instruction_count()
            self.stats.increment_clock_cycle(late)


        self.logr.info(f"Simulated {i_cnt} instructions")
