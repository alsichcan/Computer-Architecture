#----------------------------------------------------------------
#
#  4190.308 Computer Architecture (Fall 2021)
#
#  Project #3: Image Convolution in RISC-V Assembly
#
#  October 25, 2021
#
#  Jaehoon Shim (mattjs@snu.ac.kr)
#  Ikjoon Son (ikjoon.son@snu.ac.kr)
#  Seongyeop Jeong (seongyeop.jeong@snu.ac.kr)
#  Systems Software & Architecture Laboratory
#  Dept. of Computer Science and Engineering
#  Seoul National University
#
#----------------------------------------------------------------

####################
# void bmpconv(unsigned char *imgptr, int h, int w, unsigned char *k, unsigned char *outptr)
####################

	.globl bmpconv

# --- Usage of registers ---
# a0 : *imgptr
# a1 : h
# a2 : w
# a3 : *k
# a4 : *outptr
# t0 : temporary imgptr
# t1 : temporary h
# t2 : temporary w
# t3 : temporary kernel
# t4 : temporary outptr
# sp, ra, zero(x0)

# Saturate
sat:
    bge t4, x0, 2
    add t4, x0, x0
# a0 reg is used
    addi a0, x0, 255
    blt t4, a0, 2
    addi t4, x0, 255
    ret


# Calculate for a single cell
calCell:
    lw t0, 0(a0)
    bge t0, x0, 2
    sub t0, x0, t0
    add t4, t4, t0
    ret

# Calculate for an entire cell (3x3 cell)
calKer:

    beq
    lw t0, 0(a0)
    bne t0, 0, calCell

main:
# Stack memory에 args 저장
    addi sp, sp, -24
    sw ra, 20(sp)
    sw a0, 16(sp)
    sw a1, 12(sp)
    sw a2, 8(sp)
    sw a3, 4(sp)
    sw a4, 0(sp)

# a2에 width에서 읽어들여야하는 범위 계산
    srli t2, a2, 2
    slli t2, t2, 2
    sub t2, a2, t2
    srli a2, a2, 2
    add a2, a2, t2
    addi a2, a2, -2

# a3에 height에서 읽어들여야하는 범위 계산
    addi a3, a3, -2

# t0, t3, t4에 각각 arg의 초기값을 배정한다.
    add t0, a0, x0
    add t3, a3, x0
    add t4, a4, x0

# 중첩 while loop을 통해



















	ret
