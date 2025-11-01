"""
# I-Type Instruction

```
31                                20 19          15 14    12 11           7 6             0
+-----------------------------------+--------------+--------+--------------+--------------+
|             imm[11:0]             |     rs1      | funct3 |      rd      |    opcode    |
+-----------------------------------+--------------+--------+--------------+--------------+
```
"""

from src.utils.field import Field


i_imm = Field(31, 20)
"""
**I-Type immediate**: Bits 31 to 20 of an instruction
"""


funct7 = Field(31, 25)
"""
**7-bit function code**: Bits 31 to 25 of an instruction
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


i_imm_width = i_imm.width
"""
Width of the I-type immediate field
"""
