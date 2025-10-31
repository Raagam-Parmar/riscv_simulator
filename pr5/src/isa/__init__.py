"""
# RISC-V ISA Specifications

The opcode is the least significant 7-bits of an instruction.

`inst[0]` and `inst[6]` are the MSB and LSB of the opcode respectively.

`inst[0]` and `inst[1]` are always set
to `1`.

Below is the format table for the rest of the opcodes supported by the simulation
library. Unsuppported opcode cells are left blank.

## Opcodes

|           | inst[4:2] |   000   |   001   |   010   |    011    |   100   |   101   |   110   |   111   |
|-----------|-----------|---------|---------|---------|-----------|---------|---------|---------|---------|
| inst[6:5] |           |         |         |         |           |         |         |         |         |
|        00 |           |  LOAD   |         |         | MISC-MEM  |  OP-IMM |  AUIPC  |         |         |
|        01 |           |  STORE  |         |         |    AMO    |  OP     |  LUI    |         |         |
|        10 |           |         |         |         |           |         |         |         |         |
|        11 |           |  BRANCH |  JALR   |         |    JAL    |  SYSTEM |         |         |         |

See: [RV32/64G Instruction Set Listings](https://docs.riscv.org/reference/isa/unpriv/rv-32-64g.html)


## Instructions Listing (src.isa.enums)
"""

from .enums import *
from .formats import *
from .properties import *
from .tables import *
