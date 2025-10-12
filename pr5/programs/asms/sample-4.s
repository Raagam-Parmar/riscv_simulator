.section .text
.globl main
main:
	li x2, -1          # x2 = 0xFFFFFFFF (op1, signed -1)
	li x3, 2           # x3 = 0x00000002 (op2, unsigned 2)
	mulhsu x1, x2, x3  # Should give 0xFFFFFFFF in x1
	li x4, 0xFFFFFFFF  # Load expected correct result
	beq x1, x4, correct
	# Wrong implementation path
	mv x5, x0
	mv x5, x0
	j halt
correct:
	# Correct implementation path
	mv x6, x1
halt:
	j halt
