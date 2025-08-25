    .section .data
    .align   2
n:
    .word    5
l:
    .word    2
    .word    -1
    .word    7
    .word    5
    .word    3

    .section .text
    .globl   main
main:
    la       t0, n
    lw       t0, 0(t0)   # t0 = n (number of array elements)

    la       t1, l       # t1 = &l[0]
    li       x10, 0      # x10 = 0 (number of non-negative evens)

loop:
    addi     t0, t0, -1  # t0 -= 1
    bltz     t0, halt    # if index is negative, halt

    slli     t2, t0, 2   # t2 = i * 4 (word addressed)
    add      t3, t2, t1  # t3 = address of the ith element
    lw       t4, 0(t3)   # t4 = RAM[i]

    andi     t5, t4, 1   # t5 = LSB of t4
    bnez     t5, loop    # if LSB is 1, go to loop
    bltz     t4, loop    # elif MSB is 1, go to loop

    addi     x10, x10, 1 # else add 1 to total count of non-negative evens
    jal      x0, loop    # jump to loop

halt:
    j        halt
