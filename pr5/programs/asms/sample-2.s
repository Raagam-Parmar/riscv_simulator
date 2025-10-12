.section .text
.globl main
main:
	lui x1, 1
	addi x2, x0, 1
	slli x2, x2, 12
	beq x1, x2, eq
	mv x0, x0
	mv x0, x0
	j halt

eq:
	mv x1, x1

halt:
	j halt

