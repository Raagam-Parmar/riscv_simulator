
	.section .data
	.align   2
A:
	.word    1
	.word    2
	.word    3
	.word    3
	.word    2
	.word    1
	.word    1
	.word    0
	.word    3
B:
	.word    1
	.word    0
	.word    1
	.word    1
	.word    1
	.word    1
	.word    1
	.word    0
	.word    1
C:
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
	la       a0, A
	la       a1, B
	la       a2, C
	call     matmul
	j        halt


# A leaf procedure which does everything in the temporary registers,
# so there's no need to set up a stack frame.
matmul:
	li       t2, 3
	li       t0, 0
	li       a3, 1          # a3 stores the zero flag.
# Loop 1 (t0: 0 -> 2)
L1:
	bge      t0, t2, EL1
	li       t1, 0
# Loop 2 (t1: 0 -> 2)
L2:
	bge      t1, t2, EL2

# t3: will store C[t0][t1]
	li       t3, 0
	li       t4, 0
# Loop 3 (t4: 0 -> 2)
L3:
	bge      t4, t2, EL3

# t5 <- A{t0][t4]
	mul      t5, t0, t2
	add      t5, t5, t4
	slli     t5, t5, 2
	add      t5, t5, a0
	lw       t5, 0(t5)

# t6 <- B[t4][t1]
	mul      t6, t4, t2
	add      t6, t6, t1
	slli     t6, t6, 2
	add      t6, t6, a1
	lw       t6, 0(t6)

	mul      t5, t5, t6
	add      t3, t3, t5

	addi     t4, t4, 1
	j        L3
# End of loop 3.
EL3:
# Setting C[t0][t1]
	mul      t5, t0, t2
	add      t5, t5, t1
	slli     t5, t5, 2
	add      t5, t5, a2
	sw       t3, 0(t5)

# Updating the return value if C[t0][t1] is 0.
	bne      t3, x0, NO_SET
	addi     a3, x0, 0
NO_SET:

	addi     t1, t1, 1
	j        L2
# End of loop 2.
EL2:
	addi     t0, t0, 1
	j        L1
# End of loop 1.
EL1:
# Putting the zero flag in a0.
	mv       a0, a3
	ret


halt:
	j        halt

