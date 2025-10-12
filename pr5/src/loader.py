from pathlib import Path
from typing import Union

import ram


def load(ram: ram.RAM, r5ob_path: Union[str, Path], start: int) -> int:
    """Load int `ram` the contents of `r5ob` binary at path `r5ob_path`,
    starting at `start` address.

    Returns:
        int: Number of bytes written to the ram
    """

    offset = start

    with open(r5ob_path, "rb") as f:
        while byte := f.read(1):
            ram.write_byte(offset, byte[0])
            offset += 1

    return offset
