"""
# B-Type Instruction

```
31                 25 24          20 19          15 14    12 11           7 6             0
+--------------------+--------------+--------------+--------+--------------+--------------+
|    imm[12|10:5]    |     rs2      |     rs1      | funct3 | imm[4:1|11]  |    opcode    |
+--------------------+--------------+--------------+--------+--------------+--------------+
```
"""

from src.utils.field import Field


b_imm_12 = Field(31, 31)
"""
**B-Type immediate[12]**: MSB of an instruction
"""


b_imm_10_5 = Field(30, 25)
"""
**B-Type immediate[10:5]**: Bits 30 to 25 of an instruction
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


b_imm_4_1 = Field(11, 8)
"""
**B-Type immediate[4:1]**: Bits 11 to 8 of an instruction
"""


b_imm_11 = Field(7, 7)
"""
**B-Type immediate[11]**: Bit 7 of an instruction
"""


opcode = Field(6, 0)
"""
**Instruction opcode**: Least significant 7 bits of an instruction
"""


b_imm_width = (b_imm_12.width + b_imm_10_5.width + b_imm_4_1.width + b_imm_11.width)
"""
Width of the B-type immediate field
"""
