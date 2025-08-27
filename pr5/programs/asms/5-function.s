	.section .data
	.align   2

a:
	.word    0
	.word    0
	.word    0

	.word    4
	.word    5
	.word    6

	.word    7
	.word    8
	.word    9

b:
	.word    10
	.word    11
	.word    12

	.word    13
	.word    14
	.word    15

	.word    16
	.word    17
	.word    18

c:
	.word    0
	.word    0
	.word    0

	.word    0
	.word    0
	.word    0

	.word    0
	.word    0
	.word    0

	.section .text
	.globl   main
main:

# Assumption: Matrix is stored in row-major form.
# So if the base address of matrix A is a,
# element Aij is located at a+3i+j (word addressed i and j)
# or a+4(3i+j) (for byte addressed i and j)

	la       a0, a                 # a0 = &a[0]
	la       a1, b                 # a1 = &b[0]
	la       a2, c                 # a2 = &c[0]
	jal      ra, matmul

halt:
	j        halt

matmul:
# expects *A, *B, *C at a0, a1, a2 respectively
# expects in row-major form

# prologue
	addi     sp, sp, -16           # make space on stack (16 byte aligned)
	sw       s0, 12(sp)            # store current frame pointer
	add      s0, sp, 16            # update frame pointer
	sw       a3, -8(s0)            # store a3 register
	li       a3, 3                 # load the matrix size n = 3

	li       t0, 0                 # zr = number of zero elements
	li       t1, 0                 # row index i = 0

loop_row:
	bge      t1, a3, loop_row_exit # if (i>=n) exit loop_row
	li       t2, 0                 # col index j = 0

loop_col:
	bge      t2, a3, loop_col_exit # if (j>=n) exit loop_col
	li       t3, 0                 # sum variable
	li       t4, 0                 # sum index k = 0

loop_sum:
	bge      t4, a3, loop_sum_exit # if (k>=n) exit loop_sum

# a5 = *(a+4(ni+k))
	mv       t5, a3                # t5 = n
	mul      t5, t5, t1            # t5 = ni
	add      t5, t5, t4            # t5 = ni+k
	slli     t5, t5, 2             # t5 = 4(ni+k)
	add      t5, t5, a0            # t5 = a+4(ni+k)
	lw       t5, 0(t5)             # t5 = *(a+4(ni+k))

# a6 = *(b+4(nk+j))
	mv       t6, a3                # t6 = n
	mul      t6, t6, t4            # t6 = nk
	add      t6, t6, t2            # t6 = nk+j
	slli     t6, t6, 2             # t6 = 4(nk+j)
	add      t6, t6, a1            # t6 = b+4(nk+j)
	lw       t6, 0(t6)             # t6 = *(b+4(nk+j))

# sum += (a5 * a6)
	mul      t5, t5, t6            # temp = t5 * t6
	add      t3, t3, t5            # t3 += temp

	addi     t4, t4, 1
	j        loop_sum

loop_sum_exit:

# If (t3 == 0) add 1 to zr count
	bnez     t3, not_zero
	addi     t0, t0, 1

not_zero:
# *(c+4(ni+j)) = sum
	mv       t6, a3                # t6 = n
	mul      t6, t6, t1            # t6 = ni
	add      t6, t6, t2            # t6 = ni+j
	slli     t6, t6, 2             # t6 = 4(ni+j)
	add      t6, t6, a2            # t6 = c+4(ni+j)
	sw       t3, 0(t6)             # *t6 = sum

	addi     t2, t2, 1             # j++
	j        loop_col

loop_col_exit:

	addi     t1, t1, 1
	j        loop_row              # i++

loop_row_exit:

	seqz     a0, t0                # if zr == 0, return 1, else return 0
	lw       a3, -8(s0)            # restore a3
	lw       s0, 12(sp)            # restore frame pointer
	addi     sp, sp, 16            # restore stack pointer

	ret
