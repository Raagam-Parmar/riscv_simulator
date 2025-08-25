	.section .data
	.align   2
a:
	.word    8

	.section .text

	.globl   main
main:
# By definition, prime numbers are naturals and not negative,
# so the program returns (-1) if called on numbers <= 1.
	la       a0, a
	lw       a0, 0(a0)        # a0 = (number to check prime)

	addi     t0, a0, -1
	blez     t0, not_prime    # if a0 == 1, it is not prime

	addi     t0, a0, -2
	beqz     t0, is_prime     # if a0 == 2, it is prime

	andi     t0, a0, 1
	beqz     t0, not_prime    # if a0 is even, it is not prime

	li       t0, 3            # start checking from 3 to sqrt(n)

loop:
	mul      t1, t0, t0       # t1 = n^2
	bgt      t1, a0, is_prime # did not find a factor so far, is_prime

	rem      t2, a0, t0       # check remainder with odd numbers starting form 3
	beqz     t2, not_prime    # if remainder is 0, it is not_prime

	addi     t0, t0, 2        # check for next odd divisor
	j        loop

is_prime:
	li       a0, 1            # return 1 and halt
	j        halt

not_prime:
	li       a0, -1           # return -1 and halt

halt:
	j        halt
