    .section .data

    .section .text
    .globl   main

main:
# Q9
# write an assembly program to set the 5th bit of register x1
# to the value of the 3rd bit of x2.
    li       x1, 0xffffffff      # TEST VALUE
    li       x2, 0x0             # TEST VALUE

    srli     t0, x2, 2
    andi     t0, t0, 1
    li       t1, 0xFFFFFFEF
    and      x1, x1, t1
    slli     t0, t0, 4
    or       x1, x1, t0

# Q10
# write a program in assembly to convert an integer stored in memory
# from the little endian to the big endian format.
# assuming the interger is in x1.
    li       x1, 0x89abcdef      # TEST VALUE

    slli     t0, x1, 24
    srli     t1, x1, 24
    or       t0, t0, t1
    li       t2, 0x0000FF00
    and      t1, x1, t2
    slli     t1, t1, 8
    or       t0, t0, t1
    li       t2, 0x00FF0000
    and      t1, x1, t2
    srli     t1, t1, 8
    or       t0, t0, t1

    mv       x2, t0

# Q11
# write a program in assembly to compute the factorial of a positive
# number using an iterative algorithm.
# assuming number to find fact of is in x1 and result to be stored in x2.
    li       x1, 5               # TEST VALUE

    li       x2, 1               # fact = 1
    li       t0, 1               # temp t0 = 1
while1:
    ble      x1, t0, end_fact    # if x1 <= 1, end.
    mul      x2, x2, x1          # fact = fact * n
    addi     x1, x1, -1          # n--
    j        while1
end_fact:

# Q12
# write a program in assembly to find if a number is prime
# assuming number is located in x1, and answer in x2
    li       x1, 8011            # TEST VALUES

    addi     t0, x1, -1
    blez     t0, not_prime

    addi     t0, x1, -2
    beqz     t0, is_prime

    addi     t0, x1, -3
    beqz     t0, is_prime

    li       t0, 2               # i = 2
while2:
    mul      t1, t0, t0          # j = i*i
    bgt      t1, x1, is_prime    # j > n, n is prime
    rem      t2, x1, t0          # k = n mod i
    beqz     t2, not_prime       # if n mod i == 0, it is not prime
    addi     t0, t0, 1           # i++
    j        while2
is_prime:
    li       x2, 1               # it is prime
    j        end_primes
not_prime:
    li       x2, 0               # it is not prime
end_primes:

# Q13
# write a program in assembly to test if a number is a perfect square
# assuming number is located in x1 and answer in x2
# and that the number is an integer
    li       x1, 1024            # TEST VALUES

    bltz     x1, not_square      # if x < 0, it is not a perfect square
    beqz     x1, is_square       # if x == 0, it is a prefect square

    li       t0, 1               # i = 1
while3:
    mul      t1, t0, t0          # j = i*i
    bgt      t1, x1, not_square  # if j > n, not perfect square
    beq      t1, x1, is_square   # if j == n, we found a square root
    addi     t0, t0, 1           # i++
    j        while3
is_square:
    li       x2, 1
    j        end_prefect_squares
not_square:
    li       x2, 0
end_prefect_squares:

# Q14
# given a 32-bit integer in x3, write a assembly program to count the
# number of 1 to 0 transitions in it.
# assuming result to be stored in x4
    li       x3, 0x307b2a62      # TEST VALUE

    li       t0, 32              # shifts remaining = 32
    li       t1, 0               # number of 10 transitions so far, zero
    mv       t2, x3              # temp = x3 (the number)
while4:
    bltz     t0, end_while3      # if no more shifts left, end while loop
    andi     t3, t2, 3           # mask to get the last two digits

    beqz     t3, seq_zero        # if masked value is zero, goto seq_zero
    addi     t4, t3, -1
    beqz     t4, seq_one         # if masked value is one, goto seq_one
    addi     t4, t3, -2
    beqz     t4, seq_two         # if masked value is two, goto seq_two
    addi     t4, t3, -3
    beqz     t4, seq_three       # if masked value is three, goto seq_three

seq_zero:
seq_one:
    srli     t2, t2, 1
    addi     t0, t0, -1
    j        while4

seq_two:
    addi     t1, t1, 1           # 10 sequence found
    srli     t2, t2, 2
    addi     t0, t0, -2
    j        while4

seq_three:
    srli     t2, t2, 2
    addi     t0, t0, -2
    j        while4
end_while3:
    mv       x4, t1

# TODO
# Q15
# write a program in assembly to find the smallest number that is a
# sum of two different pairs of cubes. [Note: 1729 is the Hardy-Ramanujan number. 1729 =
# 123 + 13 = 103 + 93].

# Q16
# Write a assembly program that checks if a 32-bit number is a palin-
# drome. Assume that the input is available in r3. The program should set r4 to 1 if it is a
# palindrome, otherwise r4 should contain a 0. A palindrome is a number which is the same
# when read from both sides. For example, 1001 is a 4-bit palindrome.

    li       x3, 0x7FFFFFFE    # TEST VALUE

    li       t0, 0             # i = 0
loop1:
    li       t1, 16
    bge      t0, t1, end_loop1 # if i >= 16, break loop1

    li       t2, 1
    sll      t2, t2, t0        # t2 = 1 << i (mask for right side)
    and      t5, x3, t2        # use the mask, store it in x5
    srl      t5, t5, t0        # get the masked bit

    li       t3, 0x80000000
    srl      t3, t3, t0        # tr = 0x80000000 >> i (mask for left side)
    and      t6, x3, t3        # use the mask, store it in t6

    li       t3, 31
    sub      t3, t3, t0        # t3 = 31 - i
    srl      t6, t6, t3        # get the masked bit

    bne      t5, t6, not_pal   # not palindrome
    addi     t0, t0, 1         # i++
    j        loop1

end_loop1:
    li       x4, 1
    j        end_pal
not_pal:
    li       x4, 0
end_pal:


# TODO
# Q17
# Design a SimpleRisc program that examines a 32-bit value stored in r1 and counts
# the number of contiguous sequences of 1s. For example, the value:
# 01110001000111101100011100011111
# contains six sequences of 1s. Write the result in r2.

# Q18
# Write a program in SimpleRisc assembly to subtract two 64-bit numbers, where
# each number is stored in two registers.
#
# for number n1, x1 stores lower and x2 stores higher 32 bit values
# for number n2, x3 ... and x4 ...
# final result, n1-n2, x5 ... and x6 ...
    sub x5, x1, x3
    sub x6, x2, x4
    slt t0, x1, x3 # t0 is 1 if x1 < x3, else 0
    sub x6, x6, t0

halt:
    j        halt
