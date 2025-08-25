    .section .data
    .align   2
n:
    .word    -1

    .section .text
    .globl   main
main:
    la       a0, n
    lw       a0, 0(a0)  # a0 <- n (factorial input)
    jal      ra, fact

halt:
    j        halt

fact:
# If number <=1, return 1
    addi     t0, a0, -1
    blez     t0, ret_1
# otherwise compute recursively

# make space for ra and arg a0 on stack
    addi     sp, sp, -8
    sw       a0, 0(sp)
    sw       ra, 4(sp)

# call fact on n-1
    addi     a0, a0, -1
    jal      ra, fact

    mv       t0, a0
# restore ra and argument n from stack
    lw       a0, 0(sp)
    lw       ra, 4(sp)

# a0 = n * fact (n-1)
    mul      a0, a0, t0

# remove elements from stack and return
    addi     sp, sp, 8
    ret

ret_1:
    li       a0, 1
    ret
