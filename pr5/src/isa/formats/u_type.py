"""
# U-Type Instruction

```
31                                                        12 11           7 6             0
+-----------------------------------------------------------+--------------+--------------+
|                          imm[31:12]                       |      rd      |    opcode    |
+-----------------------------------------------------------+--------------+--------------+
```
"""

from src.utils.field import Field


u_imm = Field(31, 12)
"""
**U-Type immediate**: Bits 31 to 12 of an instruction
"""


rd = Field(11, 7)
"""
**Destination register**: Bits 11 to 7 of an instruction
"""


opcode = Field(6, 0)
"""
**Instruction opcode**: Least significant 7 bits of an instruction
"""


u_imm_width = u_imm.width
"""
Width of the U-type immediate field
"""
