from ram import RAM
from .processor import Processor
from logger import PR5Logger


class SingleCycleProcessor(Processor):
    def __init__(self, start: int, ram: RAM, logger: PR5Logger):
        super().__init__(start, ram, logger)

    def run(self, num_insts: int) -> None:
        """
        Run the processor in a single cycle for each instruction.
        """

        i_cnt = 0
        while i_cnt < num_insts:
            l1 = self.fetch()

            # if instruction is None:
            #     break

            l2 = self.decode(l1)
            l3 = self.execute(l2)
            l4 = self.mem_access(l3)
            self.update_pc(l3)
            self.writeback(l4)
            
            i_cnt += 1

        self.logr.info(f"Simulated {i_cnt} instructions")
