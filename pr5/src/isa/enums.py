"""
# RISC-V Instruction Opcodes
Enumeration classes defining opcodes for all RISC-V instruction types.

|      Enum       | Format |               Description                    |
|-----------------|--------|----------------------------------------------|
| `Reg_ops`       |   R    | register-register instruction                |
| `Imm_ops`       |   I    | register-immediate instruction               |
| `Jalr_ops`      |   I    | jump-and-link-register instruction           |
| `Load_ops`      |   I    | memory load instruction                      |
| `Store_ops`     |   S    | memory store instruction                     |
| `Branch_ops`    |   B    | conditional branch instruction               |
| `Upper_ops`     |   U    | upper immediate instruction                  |
| `Jal_ops`       |   J    | jump-and-link instruction                    |
| `Misc_mem_ops`  |        | miscellaneous memory instruction             |
| `Atomic_ops`    |   R    | atomic instruction                           |
| `System_ops`    |   I    | system / environment instruction             |
| `Zicsr_ops`     |   R    | CSR modifying register-register instruction  |
| `Zicsr_imm_ops` |        | CSR modifying register-immediate instruction |
"""

from typing import Union
from enum import Enum, auto


class Reg_ops(Enum):
    """
    Opcodes for register-register instructions.

    ###  Format
    ```
    31             25 24   20 19   15 14      12 11            7 6         0
    +----------------+-------+-------+----------+---------------+-----------+
    |     funct7     |  rs2  |  rs1  |  funct3  |      rd       |  0110011  |
    +----------------+-------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `ADD`
    - `SUB`
    - `XOR`
    - `OR`
    - `AND`
    - `SLL`
    - `SRL`
    - `SRA`
    - `SLT`
    - `SLTU`

    ### Opcodes (RV32-M)
    - `MUL`
    - `MULH`
    - `MULHSU`
    - `MULHU`
    - `DIV`
    - `DIVU`
    - `REM`
    - `REMU`
    """

    ADD = auto()
    SUB = auto()
    XOR = auto()
    OR = auto()
    AND = auto()
    SLL = auto()
    SRL = auto()
    SRA = auto()
    SLT = auto()
    SLTU = auto()

    MUL = auto()
    MULH = auto()
    MULHSU = auto()
    MULHU = auto()
    DIV = auto()
    DIVU = auto()
    REM = auto()
    REMU = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class Imm_ops(Enum):
    """
    Opcodes for register-immediate instructions.

    ### Format
    ```
    31                     20 19   15 14      12 11            7 6         0
    +------------------------+-------+----------+---------------+-----------+
    |       imm[11:0]        |  rs1  |  funct3  |      rd       |  0010011  |
    +------------------------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `ADDI`
    - `XORI`
    - `ORI`
    - `ANDI`
    - `SLLI`
    - `SRLI`
    - `SRAI`
    - `SLTI`
    - `SLTIU`
    """

    ADDI = auto()
    XORI = auto()
    ORI = auto()
    ANDI = auto()
    SLLI = auto()
    SRLI = auto()
    SRAI = auto()
    SLTI = auto()
    SLTIU = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class Jalr_ops(Enum):
    """
    Opcode for JALR instruction.

    ### Format
    ```
    31                     20 19   15 14      12 11            7 6         0
    +------------------------+-------+----------+---------------+-----------+
    |       imm[11:0]        |  rs1  |  funct3  |      rd       |  1100111  |
    +------------------------+-------+----------+---------------+-----------+
    ```

    ### Opcode (RV32-I)
    - `JALR`
    """

    JALR = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class Load_ops(Enum):
    """
    Opcodes for memory-load instruction.

    ### Format
    ```
    31                     20 19   15 14      12 11            7 6         0
    +------------------------+-------+----------+---------------+-----------+
    |       imm[11:0]        |  rs1  |  funct3  |      rd       |  0000011  |
    +------------------------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `LB`
    - `LH`
    - `LW`
    - `LBU`
    - `LHU`
    """

    LB = auto()
    LH = auto()
    LW = auto()
    LBU = auto()
    LHU = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class Store_ops(Enum):
    """
    Opcodes for memory-store instruction.

    ### Format
    ```
    31             25 24   20 19   15 14      12 11            7 6         0
    +----------------+-------+-------+----------+---------------+-----------+
    |   imm[11:5]    |  rs2  |  rs1  |  funct3  |   imm[4:0]    |  0100011  |
    +----------------+-------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `SB`
    - `SH`
    - `SW`
    """

    SB = auto()
    SH = auto()
    SW = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class Branch_ops(Enum):
    """
    Opcodes for branch instruction.

    ### Format
    ```
    31             25 24   20 19   15 14      12 11            7 6         0
    +----------------+-------+-------+----------+---------------+-----------+
    |  imm[12|10:5]  |  rs2  |  rs1  |  funct3  |  imm[4:1|11]  |  1100011  |
    +----------------+-------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `BEQ`
    - `BNE`
    - `BLT`
    - `BGE`
    - `BLTU`
    - `BGEU`
    """

    BEQ = auto()
    BNE = auto()
    BLT = auto()
    BGE = auto()
    BLTU = auto()
    BGEU = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class Upper_ops(Enum):
    """
    Opcodes for branch instruction.

    ### Format

    ```
    31                                        12 11            7 6         0
    +-------------------------------------------+---------------+-----------+
    |                imm[31:12]                 |       rd      |  opcode   |
    +-------------------------------------------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `LUI` (opcode `0110111`)
    - `AUIPC` (opcode `0010111`)
    """

    LUI = auto()
    AUIPC = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class Jal_ops(Enum):
    """
    Opcode for JAL instruction.

    ### Format
    ```
    31                                        12 11            7 6         0
    +-------------------------------------------+---------------+-----------+
    |          imm[20|10:1|11|19:12]            |       rd      |  1101111  |
    +-------------------------------------------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `JAL`
    """

    JAL = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class Misc_mem_ops(Enum):
    """
    Opcodes for miscellaneous memory instructions.

    ### Format
    ```
    31    28 27    24 23   20 19   15 14      12 11            7 6         0
    +-------+--------+-------+-------+----------+---------------+-----------+
    |  fm   |  pred  | succ  |  rs1  |  funct3  |  imm[4:1|11]  |  0001111  |
    +-------+--------+-------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `FENCE`
    - `FENCE_TSO`
    - `PAUSE`
    """

    FENCE = auto()
    FENCE_TSO = auto()
    PAUSE = auto()

    def __str__(self):
        return self.name.lower().replace("_", ".")

    def __repr__(self):
        return str(self)


class Atomic_ops(Enum):
    """
    Opcodes for atomic instructions.

    ### Format
    ```
    31     27  26   25  24   20 19   15 14      12 11          7 6         0
    +--------+----+----+-------+-------+----------+-------------+-----------+
    | funct5 | aq | rl |  rs2  |  rs1  |  funct3  |     rd      |  0101111  |
    +--------+----+----+-------+-------+----------+-------------+-----------+
    ```

    ### Opcodes (RV32-A)
    - `LR_W` - Load reserved
    - `SC_W` - Store conditional
    - `AMOSWAP_W`
    - `AMOADD_W`
    - `AMOXOR_W`
    - `AMOAND_W`
    - `AMOOR_W`
    - `AMOMIN_W`
    - `AMOMAX_W`
    - `AMOMINU_W`
    - `AMOMAXU_W`
    """

    LR_W = auto()
    SC_W = auto()
    AMOSWAP_W = auto()
    AMOADD_W = auto()
    AMOXOR_W = auto()
    AMOAND_W = auto()
    AMOOR_W = auto()
    AMOMIN_W = auto()
    AMOMAX_W = auto()
    AMOMINU_W = auto()
    AMOMAXU_W = auto()

    def __str__(self):
        return self.name.lower().replace("_", ".")

    def __repr__(self):
        return str(self)


class System_ops(Enum):
    """
    Opcodes for system instructions.

    ###  Format
    ```
    31             25 24   20 19   15 14      12 11            7 6         0
    +----------------+-------+-------+----------+---------------+-----------+
    |     funct7     |  rs2  |  rs1  |  funct3  |      rd       |  1110011  |
    +----------------+-------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (RV32-I)
    - `ECALL`
    - `EBREAK`

    ### Opcodes (Priviledged RV32)
    - `SRET`
    - `MRET`
    - `MNRET`
    - `WFI`
    """

    ECALL = auto()
    EBREAK = auto()

    SRET = auto()
    MRET = auto()
    MNRET = auto()

    WFI = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class Zicsr_ops(Enum):
    """
    Opcodes for CSR manipulating register-immediate instructions.

    ### Format
    ```
    31                     20 19   15 14      12 11            7 6         0
    +------------------------+-------+----------+---------------+-----------+
    |          csr           |  rs1  |  funct3  |      rd       |  1110011  |
    +------------------------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (Priviledged RV32)
    - `CSRRW`
    - `CSRRS`
    - `CSRRC`
    """

    CSRRW = auto()
    CSRRS = auto()
    CSRRC = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)



class Zicsr_imm_ops(Enum):
    """
    Opcodes for CSR manipulating register-immediate instructions.

    ### Format
    ```
    31                     20 19   15 14      12 11            7 6         0
    +------------------------+-------+----------+---------------+-----------+
    |          csr           | uimm  |  funct3  |      rd       |  1110011  |
    +------------------------+-------+----------+---------------+-----------+
    ```

    ### Opcodes (Priviledged RV32)
    - `CSRRWI`
    - `CSRRSI`
    - `CSRRCI`
    """

    CSRRWI = auto()
    CSRRSI = auto()
    CSRRCI = auto()

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)



OpCode = Union[
    Reg_ops,
    Imm_ops,
    Jalr_ops,
    Load_ops,
    Store_ops,
    Branch_ops,
    Upper_ops,
    Jal_ops,
    Misc_mem_ops,
    Atomic_ops,
    System_ops,
    Zicsr_ops,
    Zicsr_imm_ops,
]
"""
List of all suppported opcodes by the simulation library.
- `Reg_ops`
- `Imm_ops`
- `Jalr_ops`
- `Load_ops`
- `Store_ops`
- `Branch_ops`
- `Upper_ops`
- `Jal_ops`
- `Misc_mem_ops`
- `Atomic_ops`
- `System_ops`
- `Zicsr_ops`
- `Zicsr_imm_ops`
"""
