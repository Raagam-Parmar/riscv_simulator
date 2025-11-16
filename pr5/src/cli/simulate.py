import argparse
import os
import logging
import sys

import src.io.loader as loader
import src.utils.logger as logger
from src.utils import stats
from src.processor import SingleCycleProcessor, PipelinedProcessor, ForwardingPipelined
from src.utils.constants import BASE_ADDR
from src.cli.configure import ConfigReader
from src.hardware.memory.cache.cache import CacheType
from src.hardware.memory.hierarchy import MemoryHierarchy
from src.processor import ProcType
from src.utils.cint import *


def parse_args():
    parser = argparse.ArgumentParser(description="pr5 Simulator")

    parser.add_argument("r5ob_path", type=str, help="Path to the input r5ob file")

    parser.add_argument(
        "--config", type=str, help="Path to config file"
    )

    parser.add_argument(
        "--stats_file", type=str, help="Statistics output file"
    )

    parser.add_argument(
        "--num_insts",
        type=int,
        help="Number of instructions to simulate",
    )

    parser.add_argument(
        "--start",
        type=lambda x: int(x, 16),
        help="Start PC in hex (e.g. 0x80000000)",
    )

    parser.add_argument("--log_level", type=str, help="Logging level")

    parser.add_argument(
        "--proc",
        type=str,
        help="Processor to use for simulation (SingleCycleProcessor / PipelinedProcessor / FPipelinedProcessor)",
    )

    return parser.parse_args()


def run_simulation():
    loggr = logger.setup()
    cmd = "python3 " + " ".join(sys.argv)
    loggr.info(f"Running: {cmd}")

    args = parse_args()

    if not os.path.isfile(args.r5ob_path):
        loggr.error(f"Error: Executable file '{args.r5ob_path}' does not exist.")
        sys.exit(1)

    stat = stats.Statistics(loggr)
    config = ConfigReader(args.config)

    stats_file = config.get_stats_file()
    num_insts = config.get_num_insts()
    start = config.get_start()
    log_level = config.get_log_level()
    proc_type = config.get_processor_type()

    if args.stats_file is not None:
        stats_file = args.stats_file

    if args.num_insts is not None:
        num_insts = args.num_insts

    if args.start is not None:
        start = args.start

    if args.log_level is not None:
        log_level = args.log_level

    if args.proc is not None:
        if args.proc == "SingleCycleProcessor":
            proc_type = ProcType.SINGLE_CYCLE
        elif args.proc == "PipelinedProcessor":
            proc_type = ProcType.STALL_PIPELINE
        elif args.proc == "FPipelinedProcessor":
            proc_type = ProcType.FWD_PIPELINE
        else:
            raise NameError(
                f"Unknown processor {args.proc}, allowed processors: SingleCycleProcessor / PipelinedProcessor"
            )

    r5ob_path = args.r5ob_path

    l1i_config = config.get_cache_config(CacheType.L1I)
    l1d_config = config.get_cache_config(CacheType.L1D)
    l2_config = config.get_cache_config(CacheType.L2)
    ram_config = config.get_ram_config()

    mem = MemoryHierarchy(l1i_config, l1d_config, l2_config, ram_config, loggr, stat)

    loader.load(mem.ram, args.r5ob_path, BASE_ADDR)

    match proc_type:
        case ProcType.SINGLE_CYCLE:
            processor = SingleCycleProcessor(UInt32(start), mem, loggr, stat)
        case ProcType.STALL_PIPELINE:
            processor = PipelinedProcessor(UInt32(start), mem, loggr, stat)
        case ProcType.FWD_PIPELINE:
            processor = ForwardingPipelined(UInt32(start), mem, loggr, stat)

    loggr.info(f"Start address: {hex(start)}")
    loggr.info(f"Executable path: {r5ob_path}")
    loggr.info(f"Number of instructions: {num_insts}")

    loggr.setLevel(logging.getLevelNamesMapping()[log_level])

    processor.run(num_insts)

    stat.write_statistics(stats_file)  # TODO


if __name__ == "__main__":
    run_simulation()
