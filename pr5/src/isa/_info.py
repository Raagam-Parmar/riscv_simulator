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
