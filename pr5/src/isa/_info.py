# NOTE: Done
# RISC-V Unpriviledged ISA, Page 608
# RV32I Instruction Set Listings
#
# inst[1:0] = 11
#
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
# | inst[4:2] |   000   |   001   |   010   |   011    |   100   |   101   |   110   |   111   |
# | inst[6:5] |         |         |         |          |         |         |         |         |
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
# |        00 |  LOAD   |         |         | MISC-MEM |  OP-IMM |  AUIPC  |         |         |
# |        01 |  STORE  |         |         |   AMO    |  OP     |  LUI    |         |         |
# |        10 |         |         |         |          |         |         |         |         |
# |        11 |  BRANCH |  JALR   |         |   JAL    |  SYSTEM |         |         |         |
# +-----------+---------+---------+---------+----------+---------+---------+---------+---------+
#
# The blank fields are illegal instructions in RV32-IMA-ZICSR


# NOTE: DONE
# Reg instruction
# +-----------+-------+------+---------+------------+-----------+
# | funct7    | rs2   | rs1  | funct3  |     rd     |  0110011  |
# +-----------+-------+------+---------+------------+-----------+

# NOTE: Done
# Imm instruction
# Base ISA Immediate Operations and JALR
# +-------------------+------+---------+------------+-----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  opcode   |
# +-------------------+------+---------+------------+-----------+

# NOTE: Done
# jalr instruction
# Base ISA Immediate Operations and JALR
# +-------------------+------+---------+------------+-----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  opcode   |
# +-------------------+------+---------+------------+-----------+

# NOTE: Done
# Load instruction
#  Base ISA Load operations
# +-------------------+------+---------+------------+-----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  0000011  |
# +-------------------+------+---------+------------+-----------+

# NOTE: Done
# Store instruction
#  Base ISA store operations
# +------------+------+------+---------+------------+-----------+
# | imm[11:5]  | rs2  | rs1  | funct3  |  imm[4:0]  |  0100011  |
# +------------+------+------+---------+------------+-----------+

# NOTE: Done
# Branch instruction
# Base ISA branch operations
# +---------------+------+------+---------+---------------+-----------+
# | imm[12|10:5]  | rs2  | rs1  | funct3  |  imm[4:1|11]  |  1100011  |
# +---------------+------+------+---------+---------------+-----------+

# NOTE: Done
# Upper Immediate instruction
# Base ISA U-type instructions (LUI, AUIPC)
# +------------------------------------+------------+----------+
# |            imm[31:12]              |     rd     |  opcode  |
# +------------------------------------+------------+----------+

# NOTE: Done
# Jump instruction
# Base ISA J-type instructions (JAL)
# +------------------------------------+------------+----------+
# |       imm[20|10:1|11|19:12]        |     rd     |  opcode  |
# +------------------------------------+------------+----------+

# NOTE: Done
# Misc Mem instruction
# Base ISA Misc Mem Instructions (FENCE, FENCE.TSO, PAUSE)
# +--------+---------+--------+-------+-------+------+-----------+
# |   fm   |  pred   | succ   |  rs1  |  000  |  rd  |  0001111  |
# +--------+---------+--------+-------+-------+------+-----------+

# NOTE: Done
# Atomic instruction
# Atomic Extension (R-type instructions)
# +--------+----+----+-------+------+---------+------------+-----------+
# | funct5 | aq | rl |  rs2  | rs1  |  010    |  rd        |  0101111  |
# +--------+----+----+-------+------+---------+------------+-----------+

# NOTE: Done
# Environment instruction
# Base ISA System Instructions (ECALL, EBREAK)
# Some of Priviledged ISA instructions (SRET, MRET, MNRET, WFI)
# +-----------------+--------+-------+----------+----------+-----------+
# |   funct7        |  rs2   |  rs1  |  funct3  |  rd      |  1110011  |
# +-----------------+--------+-------+----------+----------+-----------+

# NOTE: Done
# Zicsr instruction
# Zicsr Extension (R-type instructions)
# +--------------------------+-------+----------+----------+-----------+
# |            csr           | rs1   |  funct3  |  rd      |  1110011  |
# +--------------------------+-------+----------+----------+-----------+

#  NOTE: Done
# Zicsr Immediate instruction
# Zicsr Extension (I-type instructions)
# +--------------------------+-------+----------+----------+-----------+
# |            csr           | uimm  |  funct3  |  rd      |  1110011  |
# +--------------------------+-------+----------+----------+-----------+


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

# @dataclass
# class UnifiedInstruction:
#     op: OpCode
#     rs1: Optional[int]
#     rs2: Optional[int]
#     rd: Optional[int]
#     imm: Optional[int]








# const = Field(31, 7)
# """
# **For constant instruction**: Bits 31 to 7 of an instruction
# """
# Misc Mem instruction
# Base ISA Misc Mem Instructions (FENCE, FENCE.TSO, PAUSE)
# +--------+---------+--------+-------+-------+------+-----------+
# |   fm   |  pred   | succ   |  rs1  |  000  |  rd  |  0001111  |
# +--------+---------+--------+-------+-------+------+-----------+
# mm_fm_field = Field(31, 28)
# mm_pred_field = Field(27, 24)
# mm_succ_field = Field(23, 20)
# mm_const_field = const


# # Atomic instruction
# # Atomic Extension (R-type instructions)
# # +--------+----+----+-------+------+---------+------------+-----------+
# # | funct5 | aq | rl |  rs2  | rs1  |  010    |  rd        |  0101111  |
# # +--------+----+----+-------+------+---------+------------+-----------+
# a_fun5_field = Field(31, 27)
# a_aq_field = Field(26, 26)
# a_rl_field = Field(25, 25)


# # Environment instruction
# # Base ISA System Instructions (ECALL, EBREAK)
# # Some of Priviledged ISA instructions (SRET, MRET, MNRET, WFI)
# # +-----------------+--------+-------+----------+----------+-----------+
# # |   funct7        |  rs2   |  rs1  |  funct3  |  rd      |  1110011  |
# # +-----------------+--------+-------+----------+----------+-----------+
# sys_const_field = const


# # Upper Immediate instruction
# # Base ISA U-type instructions (LUI, AUIPC)
# # +------------------------------------+------------+----------+
# # |            imm[31:12]              |     rd     |  opcode  |
# # +------------------------------------+------------+----------+


# # Zicsr instruction
# # Zicsr Extension (R-type instructions)
# # +--------------------------+-------+----------+----------+-----------+
# # |            csr           | rs1   |  funct3  |  rd      |  1110011  |
# # +--------------------------+-------+----------+----------+-----------+
# csr_field = i_imm


# # Zicsr Immediate instruction
# # Zicsr Extension (I-type instructions)
# # +--------------------------+-------+----------+----------+-----------+
# # |            csr           | uimm  |  funct3  |  rd      |  1110011  |
# # +--------------------------+-------+----------+----------+-----------+
# csr_uimm_field = rs1
