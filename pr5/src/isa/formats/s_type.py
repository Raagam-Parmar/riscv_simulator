"""
# S-Type Instruction

```
31                 25 24          20 19          15 14    12 11           7 6             0
+--------------------+--------------+--------------+--------+--------------+--------------+
|     imm[11:5]      |     rs2      |     rs1      | funct3 |   imm[4:0]   |    opcode    |
+--------------------+--------------+--------------+--------+--------------+--------------+
```
"""

from src.utils.field import Field


s_imm_low = Field(11, 7)
"""
**S-Type lower immediate**: Bits 11 to 7 of an instruction
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


s_imm_high = Field(31, 25)
"""
**S-Type upper immediate**: Bits 31 to 25 of an instruction
"""


opcode = Field(6, 0)
"""
**Instruction opcode**: Least significant 7 bits of an instruction
"""


s_imm_width = s_imm_high.width + s_imm_low.width
"""
Width of the S-type immediate field
"""
