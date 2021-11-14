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
main:
# a0 ~ a5 value t0~t5로 이전
# t0 : temporary imgptr
# t1 : temporary h (h-2 ~ 0)
# t2 : temporary w (w-2 ~ 0)
# t3 : kernel pointer
# t4 : temporary outptr
    add t0, a0, x0
    addi t1, a1, -2
    addi t2, a2, -2
    add t3, a3, x0
    add t4, a4, x0

# a1 ~ a4 value 초기화
# a3 : read_bit_offset
# a4 : write_bit_offset
    add a3, x0, x0
    add a4, x0, x0

# For loop : output[i][j]에 해당하는 pixel을 위한 convolution
outer_loop_start:
    beq t1, 0, outer_loop_end
inner_loop_start:
    beq t2, 0, inner_loop_end

    // TODO : kernel[p][q]에 해당하는 값 계산
    addi sp, sp, -28
    sw ra, 24(sp)
    sw a4, 20(sp)
    sw t0, 16(sp)
    sw t1, 12(sp)
    sw t2, 8(sp)
    sw t3, 4(sp)
    sw t4, 0(sp)
    jal ra, calPixel
    lw t4, 0(sp)
    lw t3, 4(sp)
    lw t2, 8(sp)
    lw t1, 12(sp)
    lw t0, 16(sp)
    lw a4, 20(sp)
    lw ra, 24(sp)


    // TODO: *outptr에 값쓰기
//    for (int bgr_count = 0; bgr_count < 3; bgr_count++){
//        writeByte(outptr, write_bit_offset, saturate(bgr[bgr_count]));
//        write_bit_offset++;
//        if(write_bit_offset == 4){
//            outptr++;
//            write_bit_offset = 0;
//        }
//    }

    addi t2, t2, -1
    beq x0, x0, inner_loop_start

inner_loop_end:

    // TODO : 한행의 처리가 모두 끝났을 때
    // TODO : padding 처리
//    while(write_bit_offset < 4){
//        writeByte(outptr, write_bit_offset, 0);
//        write_bit_offset++;
//    }
    addi t0, t0, 1
    add a1, x0, x0
    add a2, x0, x0
    add a4, x0, x0
    addi t4, t4, -1
    beq x0, x0, outer_loop_start

outer_loop_end:
    // TODO : 후처리? (restore sp, ra)
    jalr x0, 0(ra)

calPixel:
# a0 : temp
# a1 : temp
# a2 : temp (kernel, byte)
# a3 (*) : read_bit_offset
# a4 (*) : bgr_count
# t0 (*) : temporary imgptr & byte_offset
# t1 (*) : kernel[p]
# t2 (*) : kernel[q]
# t3 (*) : kernel pointer
# t4 (*) : kernel offset

# w_byte 선계산하기 (a2 후에 stack에 넣기)
    srli a1, a2, 2
    slli a1, a1, 2
    sub a1, a2, a1
    srli a2, a2, 2
    add a0, a2, a2
    add a2, a2, a0
    add a2, a2, a1

# Stack Memory에 추가하기
    addi sp, sp, -40
    sw ra, 36(sp) # address
    sw a2, 32(sp) # w_byte
    sw a3, 28(sp) # read_bit_offset
    sw a4, 24(sp) # write_bit_offset
    sw t0, 20(sp) # imgptr
    sw t3, 16(sp) # kerptr
    sw t4, 12(sp) # writeptr
    sw x0, 8(sp) # blue
    sw x0, 4(sp) # green
    sw x0, 0(sp) # red

#  초기화
    add a0, x0, x0

# p, q, kernel_offset 초기화
    addi t1, x0, 3
    addi t2, x0, 3
    add t4, x0, x0

outer_pixel_start:
    beq a4, 0, outer_pixel_end
    lw t0, 20(sp)
    lw a1, 32(sp)
    lw a3, 28(sp)
    sub a0, x0, t1
    addi a0, a0, 3
mul_w_byte:
    beq a0, x0, inner_pixel_start
    add t0, t0, a1
    addi a0, a0, -1
    beq x0, x0, mul_w_byte

inner_pixel_start:
    beq t2, x0, inner_pixel_end
    jal ra, readKernel
    add a2, a0, x0
    beq a2, x0, rgb_ignored
    addi a4, x0, 2
rgb_start:
    // TODO : rgb value읽어오기
    blt a4, x0, rgb_end
    jal ra, readImage

    bge a2, x0, 2
    xori a0, a0, -1
    add a2, a0, x0

    bne a4, x0, b_or_g
    lw a0, 0(sp)
    add a0, a0, a2
    sw a0, 0(sp)
    beq x0, x0, rgb_saved
b_or_g:
    addi a1, x0, 1
    bne a4, a1, blue
    lw a0, 4(sp)
    add a0, a0, a2
    sw a0, 4(sp)
    beq x0, x0, rgb_saved
blue:
    lw a0, 8(sp)
    add a0, a0, a2
    sw a0, 8(sp)
    beq x0, x0, rgb_saved
rgb_saved: # read_bit_offset update
    addi a3, a3, 1
    addi a0, x0, 4
    bne a3, a0, rgb_continue
    addi t0, t0, 1
    add a3, x0, x0
rgb_continue:
    addi a4, a4, -1
    beq x0, x0, rgb_start

rgb_ignored: # read_bit_offset update
    addi a1, x0, 3
rgb_ignored_loop
    beq a1, x0, rgb_end
    addi a3, a3, 1
    addi a0, x0, 4
    bne a3, a0, rgb_ignored_loop
    addi t0, t0, 1
    add a3, x0, x0
    addi a1, a1, -1
    beq x0, x0, rgb_ignored_loop

rgb_end: # kernel_offset update
    addi t4, t4, 1
    addi a0, x0, 4
    bne t4, a0, pixel_end
    addi t3, t3, 1
    add t4, x0, x0

pixel_end:
    addi t2, t2, -1
    beq x0, x0, inner_pixel_start

inner_pixel_end:
    addi a3, a3, -9
    addi t1, t1, -1
    beq x0, x0, outer_pixel_start

outer_pixel_end:
    // TODO : *outptr에 값 쓰기
    addi a4, x0, 2
write_start:
    blt a4, x0, next_pixel

    bne a4, x0, b_or_g
    lw a3, 0(sp)
    beq x0, x0, rgb_written
b_or_g:
    addi a1, x0, 1
    bne a4, a1, blue
    lw a3, 4(sp)
    beq x0, x0, rgb_written
blue:
    lw a3, 8(sp)
    beq x0, x0, rgb_written

rgb_written:
    sw a4, 24(sp) # write_bit_offset
    sw t4, 12(sp) # writeptr
    jal ra writeImage
    addi a3, a3, 1
    addi a0, x0, 4
    bne a3, a0, write_continue
    addi t0, t0, 1
    add a3, x0, x0

write_continue
    addi a4, a4, -1
    beq x0, x0, write_start

next_pixel
    // TODO: 한 pixel의 처리가 끝났을 때
    lw ra, 32(sp)
    addi sp, sp, 36
    jalr x0, 0(ra)


# Kernelptr에서 1byte 읽어오기 (a0에 저장)
# t3 : temp kerptr
# t4 : kernel offset
readKernel:
    addi a0, x0, 0x000000FF
    slli a1, t4, 4
    sll a0, a0, a1
    and a0, a0, t3
    srl a0, a0, t4
    jalr x0, 0(ra)

# Imageptr에서 1byte 읽어오기 (a0에 저장)
# t0 : temp imgptr
# a3 : read_bit_offset
readImage:
    addi a0, x0, 0x000000FF
    slli a1, a3, 4
    sll a0, a0, a1
    lw a1, 0(t0)
    and a0, a0, a1
    srl a0, a0, a3
    jalr x0, 0(ra)

# Outptr에 1byte 쓰기 (a3에 저장)
# a3 : value
# a4 : write_bit_offset
# t4 : outptr
writeImage:
    addi a0, x0, 0x000000FF
    slli a1, t4, 4
    sll a0, a0, a1
    xori a0, a0, -1
    lw a1, 0(t4)
    and a0, a0, a1
# Saturate
bge a3, x0, 2
    add a3, x0, x0
    addi a1, x0, 255
    blt a3, a1, value_saturated
    addi a3, x0, 255
value_saturated:
    slli a1, t4, 4
    sll a1, a3, a1
    or a0, a0, a1
    sw a0, 0(t4)
    jalr x0, 0(ra)


