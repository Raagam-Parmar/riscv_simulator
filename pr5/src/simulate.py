#!/usr/bin/env python3
import argparse
import os
import sys
import ram
import loader
import logger

def parse_args():
    parser = argparse.ArgumentParser(description="pr5 Simulator")
    parser.add_argument('--start', type=lambda x: int(x, 16), required=True,
                        help='Start PC in hex (e.g. 0x80000000)')
    parser.add_argument('r5ob_path', type=str,
                        help='Path to the input r5ob file')
    parser.add_argument('--num_insts', type=int, default=1000,
                        help='Number of instructions to simulate (default: 1000)')
    return parser.parse_args()

def run_simulation():

    loggr = logger.setup()
    args = parse_args()

    if not os.path.isfile(args.r5ob_path):
        loggr.error(f"Error: Executable file '{args.r5ob_path}' does not exist.")
        sys.exit(1)

    mem = ram.RAM(loggr)
    loader.load(mem, args.r5ob_path)
    mem.dump(0x80000000, 0x80000010)

    loggr.info(f"Start address: {hex(args.start)}")
    loggr.info(f"Executable path: {args.r5ob_path}")
    loggr.info(f"Number of instructions: {args.num_insts}")


if __name__ == "__main__":
    run_simulation()
