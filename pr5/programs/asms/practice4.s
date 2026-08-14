    .section .data
    .align   2

n:
    .word    2

    .section .data
    .globl   main

main:
    la       a0, n
    lw       a0, 0(a0)
    jal      fact

halt:
    j        halt

fact:
# prologue
    addi     sp, sp, -16
    sw       ra, 12(sp)
    sw       fp, 8(sp)
    addi     fp, sp, 16
    sw       a0, -12(fp)

    addi     a0, a0, -1
    blez     a0, return_one

    jal      fact
    lw       a1, -12(fp)
    mul      a0, a0, a1
    j        return

return_one:
    li      a0, 1

return:
    lw      ra, 12(sp)
    lw      fp, 8(sp)
    addi    sp, sp, 16
    ret

