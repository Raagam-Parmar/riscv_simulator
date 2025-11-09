"""
# RISC-V Processors
"""

from enum import Enum, auto

from src.processor.single_cycle import SingleCycleProcessor
from src.processor.stalling_pipeline import PipelinedProcessor
from src.processor.forwarding_pipeline import ForwardingPipelined


class ProcType(Enum):
    """
    Processor types
    - `SINGLE_CYCLE` : Single cycle processor
    - `STALL_PIPELINE` : Pipelined processor, stalls upon detecting hazards
    - `FWD_PIPELINE` : Pipelined processor, with bypassing and early branch-target
                      generation
    """

    SINGLE_CYCLE = auto()
    STALL_PIPELINE = auto()
    FWD_PIPELINE = auto()


__all__ = [
    "SingleCycleProcessor",
    "PipelinedProcessor",
    "ForwardingPipelined",
    "ProcType",
]
