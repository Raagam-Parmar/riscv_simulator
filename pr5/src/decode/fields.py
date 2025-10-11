class Field:
    def __init__(self, hi: int, lo: int):
        self.hi = hi
        self.lo = lo

        w = hi - lo + 1
        self.width: int = w
        self.mask: int = (1 << w) - 1

    def extract(self, word: int) -> int:
        return (word >> self.lo) & self.mask


# RISC-V Standard Fields
# +-----------+-------+-------+--------+------+----------+
# |  funct7   |  rs2  |  rs1  | funct3 |  rd  |  opcode  |
# +|----------+-------+-------+--------+------+----------+
#  ^ MSB
opcode_field = Field(6, 0)
rd_field = Field(11, 7)
funct3_field = Field(14, 12)
rs1_field = Field(19, 15)
rs2_field = Field(24, 20)
fun7_field = Field(31, 25)
const_field = Field(31, 7)
msb_field = Field(31, 31)


# Imm instruction
# Base ISA Immediate Operations and JALR
# +-------------------+------+---------+------------+-----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  opcode   |
# +-------------------+------+---------+------------+-----------+

# Load instruction
#  Base ISA Load operations
# +-------------------+------+---------+------------+-----------+
# | imm [11:0]        | rs1  | funct3  |  rd        |  0000011  |
# +-------------------+------+---------+------------+-----------+
i_imm_field = Field(31, 20)
i_imm_width = i_imm_field.width


# Store instruction
#  Base ISA store operations
# +------------+------+------+---------+------------+-----------+
# | imm[11:5]  | rs2  | rs1  | funct3  |  imm[4:0]  |  0100011  |
# +------------+------+------+---------+------------+-----------+
s_imm_high_field = fun7_field
s_imm_low_field = Field(11, 7)
s_imm_width = s_imm_high_field.width + s_imm_low_field.width


# Branch instruction
# Base ISA branch operations
# +---------------+------+------+---------+---------------+-----------+
# | imm[12|10:5]  | rs2  | rs1  | funct3  |  imm[4:1|11]  |  1100011  |
# +---------------+------+------+---------+---------------+-----------+
b_imm_12_field = msb_field
b_imm_10_5_field = Field(30, 25)
b_immm_4_1_field = Field(11, 8)
b_imm_11_field = Field(7, 7)
b_imm_width = (
    b_imm_12_field.width
    + b_imm_10_5_field.width
    + b_immm_4_1_field.width
    + b_imm_11_field.width
)

# Misc Mem instruction
# Base ISA Misc Mem Instructions (FENCE, FENCE.TSO, PAUSE)
# +--------+---------+--------+-------+-------+------+-----------+
# |   fm   |  pred   | succ   |  rs1  |  000  |  rd  |  0001111  |
# +--------+---------+--------+-------+-------+------+-----------+
mm_fm_field = Field(31, 28)
mm_pred_field = Field(27, 24)
mm_succ_field = Field(23, 20)
mm_const_field = const_field


# Atomic instruction
# Atomic Extension (R-type instructions)
# +--------+----+----+-------+------+---------+------------+-----------+
# | funct5 | aq | rl |  rs2  | rs1  |  010    |  rd        |  0101111  |
# +--------+----+----+-------+------+---------+------------+-----------+
a_fun5_field = Field(31, 27)
a_aq_field = Field(26, 26)
a_rl_field = Field(25, 25)


# Jump instruction
# Base ISA J-type instructions (JAL)
# +------------------------------------+------------+----------+
# |       imm[20|10:1|11|19:12]        |     rd     |  opcode  |
# +------------------------------------+------------+----------+
j_imm_20_field = msb_field
j_imm_10_1_field = Field(30, 21)
j_imm_11_field = Field(20, 20)
j_imm_19_field = Field(19, 12)
j_imm_width = (
    j_imm_20_field.width
    + j_imm_10_1_field.width
    + j_imm_11_field.width
    + j_imm_19_field.width
)


# Environment instruction
# Base ISA System Instructions (ECALL, EBREAK)
# Some of Priviledged ISA instructions (SRET, MRET, MNRET, WFI)
# +-----------------+--------+-------+----------+----------+-----------+
# |   funct7        |  rs2   |  rs1  |  funct3  |  rd      |  1110011  |
# +-----------------+--------+-------+----------+----------+-----------+
sys_const_field = const_field


# Upper Immediate instruction
# Base ISA U-type instructions (LUI, AUIPC)
# +------------------------------------+------------+----------+
# |            imm[31:12]              |     rd     |  opcode  |
# +------------------------------------+------------+----------+

# Upper Immediate instruction
# Base ISA U-type instructions (LUI, AUIPC)
# +------------------------------------+------------+----------+
# |            imm[31:12]              |     rd     |  opcode  |
# +------------------------------------+------------+----------+
u_imm_field = Field(31, 12)


# Zicsr instruction
# Zicsr Extension (R-type instructions)
# +--------------------------+-------+----------+----------+-----------+
# |            csr           | rs1   |  funct3  |  rd      |  1110011  |
# +--------------------------+-------+----------+----------+-----------+
csr_field = i_imm_field


# Zicsr Immediate instruction
# Zicsr Extension (I-type instructions)
# +--------------------------+-------+----------+----------+-----------+
# |            csr           | uimm  |  funct3  |  rd      |  1110011  |
# +--------------------------+-------+----------+----------+-----------+
csr_uimm_field = rs1_field
