    .section .data

A:
    .word    1, 2, 0             # or try 1,2,3
    .word    4, 5, 6
    .word    7, 8, 9

B:
    .word    2, 8, 7
    .word    -1, 5, 4
    .word    0, 2, 1

C:
    .space   36

    .section .text
    .globl   main
main:
    addi     sp, sp, 272
    la       a0, A               # arg0 = &A
    la       a1, B               # arg1 = &B
    la       a2, C               # arg2 = &C
    call     matmul              # call function matmal (matrix multiplication)
    j        halt

matmul:
    addi     sp, sp, -16         # Allocate 16 bytes on stack for saving registers
    sw       ra, 12(sp)          # Save return address (ra) at offset 12(sp)
    sw       s0, 8(sp)           # Save frame pointer (s0) at offset 8(sp)
    addi     s0, sp, 16          # Set s0 as new frame pointer


    mv       s1, a0              # s1 = address of A
    mv       s2, a1              # s2 = address of B
    mv       s3, a2              # s3 = address of C

    li       t6, 1               # return value = 1 (initialized assuming for nonzero matrix)
    li       t0, 0               # (i) t0 = 0 (row index)

outer_loop:
    li       t1, 0               # (j) t1 = 0 (column index)

middle_loop:
    li       t2, 0               # (sum) t2 = 0
    li       t3, 0               # (k) t3 = 0 (loop from 0 -> 2)

inner_loop:
# load A[i][k]
    li       t4, 3               # t4 = 3
    mul      t5, t0, t4          # t5 = i * 3
    add      t5, t5, t3          # t5 = i*3 + k = t5 + k
    slli     t5, t5, 2           # t5 + byte offset for address of A[i][k]
    add      t5, s1, t5          # t5 = current address of A[i][k] , since s1 = address of A
    lw       s4, 0(t5)           # s4 = val of A[i][k]

# load B[k][j]
    mul      s5, t3, t4          # s5 = k * 3
    add      s5, s5, t1          # s5 = k*3 + j = s5 + k
    slli     s5, s5, 2           # s5 + byte offset for address of B[k][j]
    add      s5, s2, s5          # s5 = current address of B[k][j], since s2 = address of B
    lw       s6, 0(s5)           # s6 = val of B[k][j]

    mul      s4, s4, s6          # s4 = product of A[i][k] * B[k][j]
    add      t2, t2, s4          # sum += s4

    addi     t3, t3, 1           # k++
    blt      t3, t4, inner_loop  # if k < 2 , continue inner_loop

# store sum in C[i][j]
    mul      t5, t0, t4          # t5 = i * 3
    add      t5, t5, t1          # t5 = i*3 + j = t5 + j
    slli     t5, t5, 2           # t5 + byte offset for address of C[i][j]
    add      t5, s3, t5          # t5 = current address of C[i][j] , since s3 = address of C
    sw       t2, 0(t5)           # store value of C[i][j] = sum

    beq      t2, zero, set_zero  # if C[i][j] == 0 , then go to set_zero

    addi     t1, t1, 1           # j++
    blt      t1, t4, middle_loop # if (j < 3), continue middle_loop

    addi     t0, t0, 1           # i++
    blt      t0, t4, outer_loop  # if (i < 3),countinue outer_loop

end:
    mv       a0, t6              # return value = t6 (0 if zero found, else 1)
    lw       ra, 12(sp)          # restore return address
    lw       s0, 8(sp)           # restore frame pointer
    addi     sp, sp, 16          # deallocate stack frame
    ret                          # return to main

set_zero:
    li       t6, 0               # set return value (t6) = 0 (since found 0 in matmul)
    j        end                 # jump to end

halt:
    j        halt
