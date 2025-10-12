.section .data
.align 2
pre_x:
	.word 0
x:
	.word 0
post_x:
	.word -1


.section .text
.global main
main:
	la x2, x
	lbu x1, -4(x2)
	beq x1, x0, eq
	mv x0, x0
	j halt

eq:
	mv x1, x1

halt:
	j halt

