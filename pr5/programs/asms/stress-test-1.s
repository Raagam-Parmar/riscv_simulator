# RISC-V 32-bit Control Flow Chaos Test (RV32IM)
# Every computation error causes control flow divergence

    .section .data
array:
    .word    1, 2, 3, 4, 5, 6, 7, 8, 9, 10

    .section .text.init
    .globl   main

main:
    li       sp, 0x80002000

#===========================================
# PHASE 1: Fibonacci branches on exact values
#===========================================
    li       a0, 10
    jal      ra, fibonacci
    li       t0, 55                        # Fib(10) must be exactly 55
    beq      a0, t0, phase1_ok
    j        exit_fail
phase1_ok:

    li       a0, 13
    jal      ra, fibonacci
    li       t0, 233                       # Fib(13) must be exactly 233
    beq      a0, t0, phase2
    j        exit_fail

#===========================================
# PHASE 2: Array sum with branch on result
#===========================================
phase2:
    la       s0, array
    li       s1, 10
    li       s2, 0                         # Sum
    li       s3, 0                         # Index

sum_loop:
    beq      s3, s1, sum_done
    slli     t0, s3, 2
    add      t0, s0, t0
    lw       t1, 0(t0)
    add      s2, s2, t1                    # Accumulate sum
    addi     s3, s3, 1
    j        sum_loop

sum_done:
    li       t0, 55                        # Sum of 1..10 = 55
    beq      s2, t0, phase3
    j        exit_fail

#===========================================
# PHASE 3: Multiply each element, branch on product
#===========================================
phase3:
    la       s0, array
    li       s1, 5                         # First 5 elements
    li       s2, 1                         # Product
    li       s3, 0                         # Index

prod_loop:
    beq      s3, s1, prod_done
    slli     t0, s3, 2
    add      t0, s0, t0
    lw       t1, 0(t0)
    mul      s2, s2, t1                    # Multiply
    addi     s3, s3, 1
    j        prod_loop

prod_done:
    li       t0, 120                       # 1*2*3*4*5 = 120
    beq      s2, t0, phase4
    j        exit_fail

#===========================================
# PHASE 4: Division chain with exact checks
#===========================================
phase4:
    li       a0, 1000
    li       a1, 10
    div      a0, a0, a1                    # 100
    li       a1, 5
    div      a0, a0, a1                    # 20
    li       a1, 4
    div      a0, a0, a1                    # 5
    li       t0, 5
    beq      a0, t0, phase5
    j        exit_fail

#===========================================
# PHASE 5: Nested loop with exact sum check
#===========================================
phase5:
    li       s0, 0                         # Sum
    li       s1, 0                         # i

outer:
    li       t0, 5
    bge      s1, t0, outer_done

    li       s2, 0                         # j
inner:
    li       t0, 5
    bge      s2, t0, inner_done

    mul      t0, s1, s2                    # i * j
    add      s0, s0, t0

    addi     s2, s2, 1
    j        inner

inner_done:
    addi     s1, s1, 1
    j        outer

outer_done:
    li       t0, 100                       # Sum must be 100
    beq      s0, t0, phase6
    j        exit_fail

#===========================================
# PHASE 6: Shift-based computation
#===========================================
phase6:
    li       a0, 1
    li       a1, 0
    li       a2, 0                         # Sum of powers of 2

shift_loop:
    li       t0, 8
    bge      a1, t0, shift_done

    sll      t1, a0, a1                    # 2^a1
    add      a2, a2, t1
    addi     a1, a1, 1
    j        shift_loop

shift_done:
    li       t0, 255                       # 1+2+4+8+16+32+64+128 = 255
    beq      a2, t0, phase7
    j        exit_fail

#===========================================
# PHASE 7: Modulo pattern with branches
#===========================================
phase7:
    li       s0, 0                         # Counter
    li       s1, 0                         # Sum

mod_loop:
    li       t0, 20
    bge      s0, t0, mod_done

    li       t1, 3
    remu     t2, s0, t1                    # s0 % 3
    beqz     t2, mod_add                   # If divisible by 3
    j        mod_skip

mod_add:
    add      s1, s1, s0

mod_skip:
    addi     s0, s0, 1
    j        mod_loop

mod_done:
    li       t0, 63                        # 0+3+6+9+12+15+18 = 63
    beq      s1, t0, phase8
    j        exit_fail

#===========================================
# PHASE 8: Recursive factorial with check
#===========================================
phase8:
    li       a0, 7
    jal      ra, factorial
    li       t0, 5040                      # 7! = 5040
    beq      a0, t0, phase9
    j        exit_fail

#===========================================
# PHASE 9: Bitwise operations chain
#===========================================
phase9:
    li       a0, 0xAAAAAAAA
    li       a1, 0x55555555

    and      a2, a0, a1                    # 0
    or       a3, a0, a1                    # 0xFFFFFFFF
    xor      a4, a0, a1                    # 0xFFFFFFFF

    bnez     a2, exit_fail                 # AND should be 0

    addi     a3, a3, 1                     # Should overflow to 0
    bnez     a3, exit_fail

    addi     a4, a4, 1                     # Should overflow to 0
    bnez     a4, exit_fail

    j        phase10

#===========================================
# PHASE 10: Memory write-read with computation
#===========================================
phase10:
    la       s0, array
    li       s1, 10
    li       s2, 0

# Write computed values
write_loop:
    beq      s2, s1, write_done

    mul      t0, s2, s2                    # i^2
    slli     t1, s2, 2
    add      t1, s0, t1
    sw       t0, 0(t1)

    addi     s2, s2, 1
    j        write_loop

write_done:

# Read and sum
    li       s2, 0
    li       s3, 0                         # Sum

read_loop:
    beq      s2, s1, read_done

    slli     t1, s2, 2
    add      t1, s0, t1
    lw       t0, 0(t1)
    add      s3, s3, t0

    addi     s2, s2, 1
    j        read_loop

read_done:
    li       t0, 285                       # 0+1+4+9+16+25+36+49+64+81 = 285
    beq      s3, t0, phase11
    j        exit_fail

#===========================================
# PHASE 11: Branch on sign after operations
#===========================================
phase11:
    li       a0, 100
    li       a1, -50
    add      a2, a0, a1                    # 50
    bgez     a2, phase11_a
    j        exit_fail

phase11_a:
    sub      a2, a1, a0                    # -150
    bltz     a2, phase12
    j        exit_fail

#===========================================
# PHASE 12: Compare results of mulh variants
#===========================================
phase12:
    li       a0, -1
    li       a1, -1

    mulh     a2, a0, a1                    # 0
    mulhu    a3, a0, a1                    # 0xFFFFFFFE

    bnez     a2, exit_fail

    li       t0, 0xFFFFFFFE
    beq      a3, t0, exit_success
    j        exit_fail

#===========================================
# FUNCTIONS
#===========================================

# Fibonacci (recursive) - must return exact values
fibonacci:
    addi     sp, sp, -12
    sw       ra, 8(sp)
    sw       a0, 4(sp)

    li       t0, 2
    blt      a0, t0, fib_base

    addi     a0, a0, -1
    sw       a0, 0(sp)
    jal      ra, fibonacci
    lw       t0, 0(sp)
    sw       a0, 0(sp)

    addi     a0, t0, -1
    jal      ra, fibonacci
    lw       t0, 0(sp)
    add      a0, a0, t0

    lw       ra, 8(sp)
    addi     sp, sp, 12
    ret

fib_base:
    lw       ra, 8(sp)
    addi     sp, sp, 12
    ret

# Factorial (recursive) - must return exact values
factorial:
    addi     sp, sp, -8
    sw       ra, 4(sp)
    sw       a0, 0(sp)

    li       t0, 1
    ble      a0, t0, fact_base

    addi     a0, a0, -1
    jal      ra, factorial
    lw       t0, 0(sp)
    mul      a0, a0, t0

    lw       ra, 4(sp)
    addi     sp, sp, 8
    ret

fact_base:
    li       a0, 1
    lw       ra, 4(sp)
    addi     sp, sp, 8
    ret

#===========================================
# EXIT
#===========================================
exit_success:
    li       a0, 0
    j        exit_common

exit_fail:
    li       a0, 1

exit_common:
    la       t1, tohost
    sw       a0, 0(t1)
1:
    j        1b
