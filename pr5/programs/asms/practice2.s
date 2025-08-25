	.section .data

arr_x:
	.space   8

arr_y:
	.byte    104, 101, 108, 108, 111, 0

	.section .text
	.globl   main

main:
# practice 5: strcpy(x, y) [copy string y into x]
	la       a0, arr_x
	la       a1, arr_y
	jal      ra, strcpy

halt:
	j        halt


# strcpy dest src
strcpy:
	mv       t0, a0
	mv       t1, a1
while:
	lbu      t2, 0(t1)
	sb       t2, 0(t0)
	addi     t0, t0, 1
	addi     t1, t1, 1
	bnez     t2, while
	ret
