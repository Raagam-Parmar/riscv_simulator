	.section .data
	.align   2
a:
	.word    70
	.word    80
	.word    40
	.word    20
	.word    10
	.word    30
	.word    50
	.word    60
n:
	.word    8

	.section .text
	.globl   main
main:

	la       a0, n
	lw       a0, 0(a0)          # a0 = n (size of array)
	la       a1, a              # a1 = &a[0]
	li       t0, 1              # i = 1 (outer index)

outer_loop:
	bge      t0, a0, exit_outer # if i >= n, end outer loop
	addi     t1, t0, -1         # j = i-1 (inner index)

inner_loop:
	bltz     t1, exit_inner     # if j < 0, end inner loop

if:
	slli     t2, t1, 2          # multiply i by 4 (word indexing)
	add      t3, a1, t2         # t3 = &a[j]
	lw       t5, 0(t3)          # t5 = a[j]

	addi     t2, t1, 1          # t2 = i+1
	slli     t2, t2, 2
	add      t4, a1, t2         # t4 = &a[j+1]
	lw       t6, 0(t4)          # t6 = a[j+1]

	ble      t5, t6, exit_inner # if a[j] >= a[j+1], break

	sw       t5, 0(t4)
	sw       t6, 0(t3)          # swap elements a[j] and a[j+1] in memory

	addi     t1, t1, -1         # j--
	j        inner_loop

exit_inner:

	addi     t0, t0, 1          # i++
	j        outer_loop

exit_outer:

halt:
	j        halt
