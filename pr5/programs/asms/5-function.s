	.section .data
	.align   2

a:
	.word    1
	.word    2
	.word    3

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
	li       a3, 3                 # a3 = mat_size
	jal      ra, matmul

halt:
	j        halt

matmul:
# expects *A, *B, *C, n at a0, a1, a2, a3 respectively
# expects in row-major form
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

# a5 = *(a+4(3i+k))
	li       t5, 3                 # t5 = 3
	mul      t5, t5, t1            # t5 = 3i
	add      t5, t5, t4            # t5 = 3i+k
	slli     t5, t5, 2             # t5 = 4(3i+k)
	add      t5, t5, a0            # t5 = a+4(3i+k)
	lw       t5, 0(t5)             # t5 = *(a+4(3i+k))

# a6 = *(b+4(3k+j))
	li       t6, 3                 # t6 = 3
	mul      t6, t6, t4            # t6 = 3k
	add      t6, t6, t2            # t6 = 3k+j
	slli     t6, t6, 2             # t6 = 4(3k+j)
	add      t6, t6, a1            # t6 = b+4(3k+j)
	lw       t6, 0(t6)             # t6 = *(b+4(3k+j))

# sum += (a5 * a6)
	mul      t5, t5, t6            # temp = t5 * t6
	add      t3, t3, t5            # t3 += temp

	addi     t4, t4, 1
	j        loop_sum

loop_sum_exit:

# If (t3 == 0) add 1 to nz count
	bnez     t3, not_zero
	addi     t0, t0, 1

not_zero:
# *(c+4(3i+j)) = sum
	li       t6, 3                 # t6 = 3
	mul      t6, t6, t1            # t6 = 3i
	add      t6, t6, t2            # t6 = 3i+j
	slli     t6, t6, 2             # t6 = 4(3i+j)
	add      t6, t6, a2            # t6 = c+4(3i+j)
	sw       t3, 0(t6)             # *t6 = sum

	addi     t2, t2, 1             # j++
	j        loop_col

loop_col_exit:

	addi     t1, t1, 1
	j        loop_row              # i++

loop_row_exit:

	slt      a0, zero, t0          # if 0 < zr, a0 = 1 else a0 = 0
	ret
