"""
# R-Type Instruction

```
31                 25 24          20 19          15 14    12 11           7 6             0
+--------------------+--------------+--------------+--------+--------------+--------------+
|       funct7       |     rs2      |     rs1      | funct3 |      rd      |    opcode    |
+--------------------+--------------+--------------+--------+--------------+--------------+
```
"""

from src.utils.field import Field


funct7 = Field(31, 25)
"""
**7-bit function code**: Bits 31 to 25 of an instruction
"""


rs2 = Field(24, 20)
"""
**Second source register**: Bits 24 to 20 of an instruction
"""


rs1 = Field(19, 15)
"""
**First source register**: Bits 19 to 15 of an instruction
"""


funct3 = Field(14, 12)
"""
**3-bit function code**: Bits 14 to 12 of an instruction
"""


rd = Field(11, 7)
"""
**Destination register**: Bits 11 to 7 of an instruction
"""


opcode = Field(6, 0)
"""
**Instruction opcode**: Least significant 7 bits of an instruction
"""
