.section .data
	.align 2
a:
	.word 70
	.word 80
	.word 40
	.word 20
	.word 10
	.word 30
	.word 50
	.word 60
n:
	.word 8

.section .text
.globl main
main:
	# your code here
	# you may change the numbers in the array, 
	# and the size of the array; but allow
	# the name of the array to remain as 'a', 
	# and size as 'n'
	# remove these comments!


halt:
	j halt
