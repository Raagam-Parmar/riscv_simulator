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
OPCODE = Field(6, 0)
RD = Field(11, 7)
FUNCT3 = Field(14, 12)
RS1 = Field(19, 15)
RS2 = Field(24, 20)
FUNCT7 = Field(31, 25)
CONST = Field(31, 7)
MSB = Field(31, 31)

I_IMM = Field(31, 20)
i_imm_width = I_IMM.width

S_IMM_11_5 = FUNCT7
S_IMM_4_0 = Field(11, 7)
s_imm_width = S_IMM_11_5.width + S_IMM_4_0.width

B_IMM_12 = MSB
B_IMM_10_5 = Field(30, 25)
B_IMM_4_1 = Field(11, 8)
B_IMM_11 = Field(7, 7)
b_imm_width = B_IMM_12.width   \
            + B_IMM_10_5.width \
            + B_IMM_4_1.width  \
            + B_IMM_11.width

MM_FM = Field(31, 28)
MM_PRED = Field(27, 24)
MM_SUCC = Field(23, 20)
MM_CONST = CONST

A_FUN5 = Field(31, 27)
A_AQ = Field(26, 26)
A_RL = Field(25, 25)

J_IMM_20 = MSB
J_IMM_10_1 = Field(30, 21)
J_IMM_11 = Field(20, 20)
J_IMM_19_12 = Field(19, 12)
j_imm_width = J_IMM_20.width    \
            + J_IMM_10_1.width  \
            + J_IMM_11.width    \
            + J_IMM_19_12.width

CSR = I_IMM

CSR_UIMM = RS1

SYS_CONST = CONST

U_IMM = Field(31, 12)
