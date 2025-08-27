	.section .data
	.align   2
count:
	.word    0
	.word    0
	.word    0
	.word    0
	.word    0
	.word    0
	.word    0
	.word    0
	.word    0
	.word    0
	.word    0
marks:
	.word    2
	.word    3
	.word    0
	.word    5
	.word    10
	.word    7
	.word    1
	.word    10
	.word    10
	.word    8
	.word    9
	.word    6
	.word    7
	.word    8
	.word    2
	.word    4
	.word    5
	.word    0
	.word    9
	.word    1
n:
	.word    20

	.section .text
	.globl   main
main:
# Assumptions: The range of marks is integral from 0 to 10, so the size of the array
# `count` is fixed to 11.

	la       a0, marks  # a0 = &marks[0]
	la       a1, n
	lw       a1, 0(a1)  # a1 = n
	la       a2, count  # a2 = &count[0]

	addi     t0, a1, -1 # i = n-1 (loop index)
loop:
	bltz     t0, exit   # if i < 0, exit loop

	slli     t1, t0, 2  # t1 = i * 4 (word addressing)
	add      t2, a0, t1 # t2 = &marks[i]
	lw       t3, 0(t2)  # t3 = marks[i]; j = marks[i] (count index)

	slli     t4, t3, 2  # t4 = j * 4 (word addressing)
	add      t5, a2, t4 # t5 = &count[j]
	lw       t6, 0(t5)  # t6 = count[j]
	addi     t6, t6, 1  # t6++
	sw       t6, 0(t5)  # count[j] = t6

	addi     t0, t0, -1 # i--
	j        loop

exit:
halt:
	j        halt
