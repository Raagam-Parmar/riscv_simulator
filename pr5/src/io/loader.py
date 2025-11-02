"""
# Memory Loader
"""

from pathlib import Path
from typing import Union

import src.hardware.ram as ram


def load(ram: ram.RAM, r5ob_path: Union[str, Path], start_addr: int) -> int:
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
            ram.write_byte(offset, byte[0])
            offset += 1

    return offset
