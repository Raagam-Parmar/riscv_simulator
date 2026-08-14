    .section .data
    .align   2

    .section .text
    .globl   main
main:
    add      x5, x0, x0
    add      x0, x0, x5

    add      x5, x0, x0
    sub      x0, x0, x0
    add      x0, x0, x5

    j        halt

halt:
    j        halt

