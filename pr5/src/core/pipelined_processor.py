from .processor import Processor


class PipelinedProcessor(Processor):
    def __init__(self, start, ram, logger, st):
        super().__init__(start, ram, logger)
        self.stats = st

        # NOTE: The following dictionary is only suggestive. You may wish to
        # use a different structure or names if deemed fit
        self.pipeline_regs = {
            "IF/ID": None,
            "ID/EX": None,
            "EX/MEM": None,
            "MEM/WB": None,
        }

    def run(self, num_insts):
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
        pass
