from ram import RAM
from .processor import Processor
from logger import PR5Logger
from stats import Statistics

class SingleCycleProcessor(Processor):
    def __init__(self, start: int, ram: RAM, logger: PR5Logger, stat: Statistics):
        super().__init__(start, ram, logger)
        self.stats = stat

    def run(self, num_insts: int) -> None:
        """
        Run the processor in a single cycle for each instruction.
        """

        i_cnt = 0
        pc_if = self.initialise_pc()

        while i_cnt < num_insts:
            if_id = self.fetch(pc_if)
            id_ex = self.decode(if_id)
            ex_mem = self.execute(id_ex)
            mem_wb = self.mem_access(ex_mem)
            pc_if = self.update_pc(ex_mem)
            self.writeback(mem_wb, pc_if)

            i_cnt += 1

            self.stats.increment_instruction_count()

        self.logr.info(f"Simulated {i_cnt} instructions")
