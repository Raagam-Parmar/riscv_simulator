    .section .data
    .align   2
n:
    .word    11

    .section .text
    .globl   main
main:
# Assumption: factorial of any number <=1 is 1.
    addi     sp, sp, 272
    la       a0, n
    lw       a0, 0(a0)   # a0 <- n (factorial input)
    jal      ra, fact

halt:
    j        halt

fact:
    addi     sp, sp, -16 # make space on stack (16 byte aligned)
    sw       ra, 12(sp)  # store return address
    sw       s0, 8(sp)   # store current frame pointer
    add      s0, sp, 16  # update frame pointer
    sw       a0, -12(s0) # store arg0

# If number <=1, return 1
    addi     t0, a0, -1
    blez     t0, ret_1
# otherwise compute recursively

# call fact on n-1
    addi     a0, a0, -1
    jal      ra, fact

    mv       t0, a0
# argument n from stack
    lw       a0, -12(s0)

# a0 = n * fact (n-1)
    mul      a0, a0, t0
    j        return

ret_1:
    li       a0, 1       # set return value

return:
    lw       ra, 12(sp)  # restore return address
    lw       s0, 8(sp)   # restore frame pointer
    addi     sp, sp, 16  # restore stack pointer

    ret
