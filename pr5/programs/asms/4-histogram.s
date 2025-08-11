.section .data
	.align 2
count:
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
marks:
	.word 2
	.word 3
	.word 0
	.word 5
	.word 10
	.word 7
	.word 1
	.word 10
	.word 10
	.word 8
	.word 9
	.word 6
	.word 7
	.word 8
	.word 2
	.word 4
	.word 5
	.word 0
	.word 9
	.word 1
n:
	.word 20

.section .text
.globl main
main:
	# your code here
	# you may change the numbers in the marks array. 
	# Change the size of the array n suitably; 
	# The histogram should be in count.
	# the name of the arrays to remain unchanged
	# remove these comments!


halt:
	j halt
