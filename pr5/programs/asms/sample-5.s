    .section .data
    .align   2
a:
    .word    0x000000ff


    .section .text
    .globl   main
main:
    addi     x3, x0, -1
    la       x2, a
    lb       x1, 0(x2)
    beq      x1, x3, eq
    mv       x0, x0
    j        halt

eq:
    mv       x1, x1

halt:
    j        halt
