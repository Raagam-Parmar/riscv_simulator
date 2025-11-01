"""
# J-Type Instruction

```
31                                                        12 11           7 6             0
+-----------------------------------------------------------+--------------+--------------+
|                imm[20 | 10:1 | 11 | 19:12]                |      rd      |    opcode    |
+-----------------------------------------------------------+--------------+--------------+
```
"""

from src.utils.field import Field


j_imm_20 = Field(31, 31)
"""
**J-Type immediate[20]**: MSB of an instruction
"""


j_imm_10_1 = Field(30, 21)
"""
J-Type immediate[10:1]**: Bits 30 to 21 of an instruction
"""


j_imm_11 = Field(20, 20)
"""
J-Type immediate[11]**: Bit 20 of an instruction
"""


j_imm_19_12 = Field(19, 12)
"""
J-Type immediate[19:12]**: Bits 19 to 12 of an instruction
"""


rd = Field(11, 7)
"""
**Destination register**: Bits 11 to 7 of an instruction
"""


opcode = Field(6, 0)
"""
**Instruction opcode**: Least significant 7 bits of an instruction
"""


j_imm_width = (
    j_imm_20.width
    + j_imm_10_1.width
    + j_imm_11.width
    + j_imm_19_12.width
)
"""
Width of the J-type immediate field
"""
