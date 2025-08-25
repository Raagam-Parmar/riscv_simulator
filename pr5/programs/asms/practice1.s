	.section .data
	.align   2

sum:
	.word    0

arr:
	.space   400

	.section .text
	.globl   main

main:
# practice 1: x10 = 0x1234abcd
	lui      x1, 0x1234b
	addi     x1, x1, -1075

# practive 2: x4 = max(a0, a1, a2)
	li       a0, 10
	li       a1, 20
	li       a2, 30
	jal      max3

# practice 3: sum = x1 + x2
	li       x1, 10
	li       x2, 21
	add      t0, x1, x2
	la       t1, sum
	sw       t0, 0(t1)

# practice 4: arr[100] with all entries 0xc001
	jal      init_arr

halt:
	j        halt


# max2 n1 n2
max2:
	blt      a0, a1, a1_greater         # if a0 < a1 then a1 is greater
	j        return
a1_greater:
	mv       a0, a1                     # a0 = a1
return:
	ret


# max3 n1 n2 n3
max3:
# store ra to stack
	addi     sp, sp, -4
	sw       ra, 0(sp)

	jal      max2
	mv       a1, a2
	jal      max2

# restore ra from stack
	lw       ra, 0(sp)
	addi     sp, sp, 4

	ret


# init_arr
init_arr:
	li       t0, 99                     # i = 100 - 1 (arr size - 1)
loop:
	bltz     t0, exit

	slli     t1, t0, 4                  # t1 = 4i (word addressed)
	la       t2, arr
	add      t3, t2, t1                 # t3 = &arr[i]
	li       t4, 0xc001
	sw       t4, 0(t3)

	addi     t0, t0, -1
	j        loop

exit:
	ret
