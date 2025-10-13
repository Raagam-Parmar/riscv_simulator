#!/usr/bin/env python3
import argparse
import os
import logging
from enum import Enum, auto

import sys
import ram
import loader
import logger

# import statistics
import stats

from core.single_cycle_processor import SingleCycleProcessor
from core.pipelined_processor import PipelinedProcessor
from utils.constants import BYTE_WIDTH, XWIDTH, BASE_ADDR


def parse_args():
    parser = argparse.ArgumentParser(description="pr5 Simulator")

    parser.add_argument(
        "--start",
        type=lambda x: int(x, 16),
        required=True,
        help="Start PC in hex (e.g. 0x80000000)",
    )

    parser.add_argument("r5ob_path", type=str, help="Path to the input r5ob file")

    parser.add_argument(
        "--num_insts",
        type=int,
        default=1000,
        help="Number of instructions to simulate (default: 1000)",
    )

    parser.add_argument(
        "--proc",
        type=str,
        required=True,
        help="Select processor type (single / pipelined)",
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

    mem = ram.RAM(BYTE_WIDTH, XWIDTH, loggr)
    loader.load(mem, args.r5ob_path, BASE_ADDR)

    if args.proc == "single":
        processor = SingleCycleProcessor(args.start, mem, loggr, stat)
    elif args.proc == "pipelined":
        processor = PipelinedProcessor(args.start, mem, loggr, stat)
    else:
        raise NameError(
            f"Unknown processor {args.proc}, allowed processors: single / pipelined"
        )

    loggr.info(f"Start address: {hex(args.start)}")
    loggr.info(f"Executable path: {args.r5ob_path}")
    loggr.info(f"Number of instructions: {args.num_insts}")

    loggr.setLevel(logging.DEBUG)

    processor.run(args.num_insts)

    stat.write_statistics("stats.json")


if __name__ == "__main__":
    run_simulation()
