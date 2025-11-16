"""
# Memory Loader
"""

from pathlib import Path
from typing import Union

from src.hardware.memory.ram32 import RAM32
from src.utils.cint import *


def load(ram: RAM32, r5ob_path: Union[str, Path], start_addr: int) -> int:
    """
    Load the binary at `r5ob_path` into `ram`, starting at address `start_addr`.

    :param ram: RAM to load the binary into
    :param r5ob_path: Path to the r5ob binary
    :param start_addr: RAM start address for loading binary

    :return: Number of bytes written to the RAM

    :raises AddressOutOfRange: If data to be loaded is larger than available memory
    """

    offset = start_addr

    with open(r5ob_path, "rb") as f:
        while byte := f.read(1):
            ram.write_byte(uint32(offset), uint8(byte[0]), incr=False)
            offset += 1

    return offset
