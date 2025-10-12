	.section .data
	.align   2
a:
	.word    7

	.section .text

	.globl   main
main:
	la       t1, a                   # load address of a
	lw       x11, 0(t1)              # loaded value in a to x11
	addi     x10,x0,0                # flushing the current value in x10 to 0
	addi     t2, x0, 0               # flushing the value to be empty (to hold the reminder)
	addi     t3,x0,2                 # having a value t1==2 so can iterative take reminder and check
	blt      x11, t3, notprime_label # if less than 2 its n then its not prime
	srai     t4,x11,1                # to store a/2 optimal

loop:
	rem      t2,x11,t3               # hold the reminder
	beq      t2, x0, notprime_label  # if t2==0 then its not a prime ,as its divisble by t3
	beq      t3,t4, prime_label      # if t3 == a/2 then stop iteration its a prime
	addi     t3,t3,1                 # incremnet t3
	j        loop                    # continue loop

prime_label:
	addi     x10,x0,1                # final output
	j        halt

notprime_label:
	addi     x10,x0,-1               # final output
	j        halt

halt:
	j        halt
