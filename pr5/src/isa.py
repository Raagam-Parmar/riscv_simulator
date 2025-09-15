from isa_unpriv import *
# from isa_priv import *

type Instruction =  \
    Reg             \
    | Imm           \
    | Load          \
    | Store         \
    | Branch        \
    | Upper         \
    | Jump          \
    | Misc_mem      \
    | Atomic        \
    | System        \
    | Zicsr         \
    | Zicsr_Imm     
