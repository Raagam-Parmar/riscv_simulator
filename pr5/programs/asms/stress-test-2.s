# RISC-V 32-bit PC Sequence Stress Test (RV32IM)
# Every incorrect computation leads to wrong branch = different PC sequence

    .section .text.init
    .globl   main

main:
    li       sp, 0x80002000

#===========================================
# TEST 1: Overflow changes branch direction
#===========================================
    li       a0, 0x7FFFFFFF       # MAX_INT
    addi     a0, a0, 1            # Must wrap to 0x80000000
    bltz     a0, test1_pass       # If overflow wrong, takes wrong branch
    j        test1_fail
test1_pass:
    j        test2
test1_fail:
    j        exit_fail

#===========================================
# TEST 2: Sign extension affects comparison
#===========================================
test2:
    li       a0, 0xFF
    addi     sp, sp, -4
    sb       a0, 0(sp)
    lb       a1, 0(sp)            # Must sign-extend to 0xFFFFFFFF
    addi     sp, sp, 4
    bgez     a1, test2_fail       # If not sign-extended, wrong branch
    j        test3
test2_fail:
    j        exit_fail

#===========================================
# TEST 3: Shift amount masking
#===========================================
test3:
    li       a0, 1
    li       a1, 33               # Should behave as shift by 1
    sll      a0, a0, a1           # Result must be 2
    li       a1, 2
    beq      a0, a1, test4        # If shift wrong, wrong branch
    j        exit_fail

#===========================================
# TEST 4: Signed vs unsigned comparison
#===========================================
test4:
    li       a0, -1               # 0xFFFFFFFF
    li       a1, 1
    blt      a0, a1, test4_a      # Signed: -1 < 1 (true)
    j        exit_fail
test4_a:
    bltu     a0, a1, exit_fail    # Unsigned: 0xFFFFFFFF < 1 (false)
    j        test5

#===========================================
# TEST 5: Multiplication low vs high
#===========================================
test5:
    li       a0, 0x10000
    li       a1, 0x10000
    mul      a2, a0, a1           # Low: 0x00000000
    mulh     a3, a0, a1           # High: 0x00000001
    bnez     a2, exit_fail        # If mul wrong, wrong branch
    beqz     a3, exit_fail        # If mulh wrong, wrong branch
    j        test6

#===========================================
# TEST 6: Division by zero
#===========================================
test6:
    li       a0, 100
    li       a1, 0
    div      a0, a0, a1           # Must return -1
    addi     a0, a0, 1            # Make it 0
    bnez     a0, exit_fail        # If div by zero wrong, wrong branch
    j        test7

#===========================================
# TEST 7: MIN_INT / -1 overflow
#===========================================
test7:
    li       a0, 0x80000000
    li       a1, -1
    div      a0, a0, a1           # Must return 0x80000000 (overflow)
    bltz     a0, test8            # Must still be negative
    j        exit_fail

#===========================================
# TEST 8: Remainder by zero
#===========================================
test8:
    li       a0, 42
    li       a1, 0
    rem      a2, a0, a1           # Must return 42 (dividend)
    li       a3, 42
    beq      a2, a3, test9
    j        exit_fail

#===========================================
# TEST 9: Chained arithmetic affecting branch
#===========================================
test9:
    li       a0, 5
    li       a1, 3
    mul      a0, a0, a1           # 15
    addi     a0, a0, -10          # 5
    slli     a0, a0, 2            # 20
    srli     a0, a0, 1            # 10
    li       a1, 10
    beq      a0, a1, test10
    j        exit_fail

#===========================================
# TEST 10: SRA sign extension
#===========================================
test10:
    li       a0, 0x80000000
    srai     a0, a0, 1            # Must be 0xC0000000
    li       a1, 0xC0000000
    beq      a0, a1, test11
    j        exit_fail

#===========================================
# TEST 11: Store-load dependency
#===========================================
test11:
    li       a0, 0xABCD1234
    addi     sp, sp, -4
    sw       a0, 0(sp)
    lw       a1, 0(sp)
    addi     sp, sp, 4
    beq      a0, a1, test12       # If store/load broken, wrong branch
    j        exit_fail

#===========================================
# TEST 12: LUI creates correct immediate
#===========================================
test12:
    lui      a0, 0x12345
    srli     a0, a0, 12           # Should give 0x00012345
    li       a1, 0x00012345
    beq      a0, a1, test13
    j        exit_fail

#===========================================
# TEST 13: AUIPC + offset
#===========================================
test13:
    auipc    a0, 0
    addi     a0, a0, 12           # Point to test13_target
    jalr     zero, a0, 0          # Jump there
    j        exit_fail            # Should not reach
test13_target:
    j        test14

#===========================================
# TEST 14: Computed branch with XOR
#===========================================
test14:
    li       a0, 0xAAAAAAAA
    li       a1, 0x55555555
    xor      a2, a0, a1           # Must be 0xFFFFFFFF
    addi     a2, a2, 1            # Must be 0
    bnez     a2, exit_fail
    j        test15

#===========================================
# TEST 15: AND/OR/XOR chain
#===========================================
test15:
    li       a0, 0xFF00FF00
    li       a1, 0x00FF00FF
    or       a2, a0, a1           # 0xFFFFFFFF
    and      a3, a0, a1           # 0x00000000
    add      a2, a2, a3           # 0xFFFFFFFF + 0 = 0xFFFFFFFF
    xori     a2, a2, -1           # 0
    bnez     a2, exit_fail
    j        test16

#===========================================
# TEST 16: SLT and SLTU differences
#===========================================
test16:
    li       a0, -1
    li       a1, 1
    slt      a2, a0, a1           # Signed: -1 < 1, result = 1
    sltu     a3, a0, a1           # Unsigned: 0xFFFFFFFF < 1, result = 0
    beqz     a2, exit_fail        # If slt wrong
    bnez     a3, exit_fail        # If sltu wrong
    j        test17

#===========================================
# TEST 17: Load byte vs load halfword vs load word
#===========================================
test17:
    li       a0, 0x12345678
    addi     sp, sp, -4
    sw       a0, 0(sp)

    lb       a1, 0(sp)            # Load byte 0: 0x78 -> sign extend -> 0x00000078
    lh       a2, 0(sp)            # Load half 0: 0x5678 -> sign extend -> 0x00005678
    lw       a3, 0(sp)            # Load word: 0x12345678

    addi     sp, sp, 4

    li       a4, 0x00000078
    bne      a1, a4, exit_fail

    li       a4, 0x00005678
    bne      a2, a4, exit_fail

    li       a4, 0x12345678
    bne      a3, a4, exit_fail
    j        test18

#===========================================
# TEST 18: Complex computation chain
#===========================================
test18:
    li       a0, 7
    li       a1, 11
    mul      a2, a0, a1           # 77
    li       a3, 13
    divu     a2, a2, a3           # 77 / 13 = 5
    remu     a4, a2, a1           # 5 % 11 = 5
    mul      a2, a4, a4           # 5 * 5 = 25
    li       a5, 25
    beq      a2, a5, test19
    j        exit_fail

#===========================================
# TEST 19: Negative multiplication
#===========================================
test19:
    li       a0, -5
    li       a1, 3
    mul      a2, a0, a1           # -15
    li       a3, -15
    beq      a2, a3, test20
    j        exit_fail

#===========================================
# TEST 20: Memory forwarding test
#===========================================
test20:
    li       a0, 100
    li       a1, 200
    addi     sp, sp, -8
    sw       a0, 0(sp)
    sw       a1, 4(sp)
    lw       a2, 0(sp)
    lw       a3, 4(sp)
    addi     sp, sp, 8
    add      a4, a2, a3           # 100 + 200 = 300
    li       a5, 300
    beq      a4, a5, exit_success
    j        exit_fail

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

