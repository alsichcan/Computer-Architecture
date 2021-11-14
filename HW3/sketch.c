//
// Created by 박지상 on 2021/11/11.
//

int saturate(int val){
    if(val > 255) return 255;
    else if(val < 0) return 0;
    else return val;
}

int readByte(unsigned char* tarptr, int idx){
    int mask = 0x000000FF << (idx << 4);
    int byte = (*tarptr & mask) >> idx;
    return byte;
}

void writeByte(unsigned char* tarptr, int idx, int value){
    int mask = 0x000000FF << (idx << 4);
    *tarptr = (*tarptr & ~mask) | (val << (16 * idx));
}


void bmpconv(unsigned char *imgptr, int h, int w, unsigned char *k, unsigned char *outptr){
    int h_o = h - 2;
    int w_o = w - 2;
    int w_byte = (w / 4) * 3 + (w % 4);

    // 4byte에서 1byte씩 추출 (Little Endian 고려)
    // 4th byte : *imgptr & mask
    // 3rd byte : mask << 16, (*imgptr & mask) >> 16
    // 2nd byte : mask << 16, (*imgptr & mask) >> 32
    // 1st byte : mask << 16, (*imgptr & mask) >> 48
    int byte_offset = 0;
    int read_bit_offset = 0;
    int kernel_offset = 0;
    int write_bit_offset = 0;

    for(int i = h_o; i > 0; i--){ // 행
        for(int j = w_o; j > 0; j--) { // 열
            // output[i][j]에 해당하는 pixel를 위한 convolution8
            int bgr[3] = {0, 0, 0}; // Blue, Green, Red

            // TODO: kernel[p][q]에 해당하는 값 계산
            for (int p = 3; p > 0; p--){ //행
                byte_offset = 0;
                byte_offset += w_byte * (3-p);
                for(int q = 3; q > 0; q--){ //열
                    int kernel = readByte(k, kernel_offset);

                    for (int bgr_count = 2; bgr_count >= 0; bgr_count++) {
                        int byte = readByte(imgptr + byte_offset, read_bit_offset);

                        // TODO: byte가지고 처리하기
                        bgr[bgr_count] += kernel * byte;

                        read_bit_offset++;
                        if (read_bit_offset == 4) { // reset
                            byte_offset++;
                            read_bit_offset = 0;
                        }
                    }

                    kernel_offset++;
                    if(kernel_offset == 4){
                        k++;
                        kernel_offset = 0;
                    }
                }
                // TODO : 다음 줄 kernel (kernel은 bit_offset으로 처리해야)
                read_bit_offset -= 9;
            }
            k -= 2;
            kernel_offset = 0;



            // TODO: *outptr에 값 쓰기
            for (int bgr_count = 3; bgr_count > 0; bgr_count--){
                writeByte(outptr, write_bit_offset, saturate(bgr[bgr_count]));
                write_bit_offset++;
                if(write_bit_offset == 4){
                    outptr++;
                    write_bit_offset = 0;
                }
            }


            // TODO : 한 pixel의 처리가 끝났을 때
            int counter = 3;
            while(couter > 0){
                read_bit_offset++;
                if(read_bit_offset == 4){
                    imgptr++;
                    read_bit_offset = 0;
                }
            }
        }

        // TODO: 한 행의 처리가 모두 끝났을 때

        // TODO : padding 처리
        while(write_bit_offset < 4){
            writeByte(outptr, write_bit_offset, 0);
            write_bit_offset++;
        }
        imgptr++;
        byte_offset = 0;
        read_bit_offset = 0;
        write_bit_offset = 0;
        outptr++;
    }

}

