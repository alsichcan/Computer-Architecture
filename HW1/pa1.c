//---------------------------------------------------------------
//
//  4190.308 Computer Architecture (Fall 2021)
//
//  Project #1: Run-Length Encoding
//
//  September 14, 2021
//
//  Jaehoon Shim (mattjs@snu.ac.kr)
//  Ikjoon Son (ikjoon.son@snu.ac.kr)
//  Seongyeop Jeong (seongyeop.jeong@snu.ac.kr)
//  Systems Software & Architecture Laboratory
//  Dept. of Computer Science and Engineering
//  Seoul National University
//
//---------------------------------------------------------------

int writeBit(int idx, char* dst, int val){
    int mask = 1 << idx;
    *dst = (*dst & ~mask) | (val << idx);
    return 0;
}

int writeEncoding(int* count, int* idx, int* length, char* const dst, const int dstlen){
    for(int pos = 2; pos >= 0; pos--){
        int val = 0;
        if(pos == 2){
            val = *count / 4;
            *count -= val * 4;
        }
        else if (pos == 1){
            val = *count / 2;
            *count -= val * 2;
        }
        else{
            val = *count;
            *count -= val;
        }

        writeBit(*idx, dst+*length, val);

        (*idx)--;
        if(*idx < 0){
            *idx = 7;
            (*length)++;
            if(*length == dstlen)
                return -1;
        }
    }
    return 0;
}


int encode(const char* const src, const int srclen, char* const dst, const int dstlen)
{
    if(srclen == 0) return 0;

    // Encoding을 위한 변수
    int count = 0;
    int prev_bit = 0;

    // 메모리 쓰기를 위한 변수
    int idx = 7; // Bit 단위의 위치
    int length = 0; // Byte 단위의 위치

    for(int i = 0; i < srclen; i++){
        for (int j = 7; j >= 0; j--){
            int bit = (*(src+i) >> j) & 1; // 앞에서부터 1 bit씩 추출

            // 동일한 bit일 경우 Count를 늘리지만 7이 되었을때의 예외처리
            if(bit == prev_bit){
                count++;
                if(count == 7){
                    if (writeEncoding(&count, &idx, &length, dst, dstlen)==-1) return -1;

                    // Bit 전환
                    prev_bit = 1 - prev_bit;
                }
            } else{ // 다른 bit일 경우 전의 count를 encoding하여 기록
                if (writeEncoding(&count, &idx, &length, dst, dstlen)==-1) return -1;
                // 새로운 Bit의 count 증가
                prev_bit = 1 - prev_bit;
                count++;
            }
        }
    }

    // 남은 Count 처리하기
    if (writeEncoding(&count, &idx, &length, dst, dstlen)==-1) return -1;

    // Padding 채우기
    while(idx >= 0){
        writeBit(idx, dst+length, 0);
        idx--;
        if(idx < 0) break;
    }
    return length + 1;
}


int decode(const char* const src, const int srclen, char* const dst, const int dstlen)
{
    if(srclen == 0) return 0;

    // Decoding을 위한 변수
    int i = 0; // Byte 단위의 위치
    int j = 7; // Bit 단위의 위치
    int curr_bit = 0;

    // 메모리 쓰기를 위한 변수
    int idx = 7; // Bit 단위의 위치
    int length = 0; // Byte 단위의 위치

    while(i < srclen){
        // 3개 단위로 값을 읽어오기 --> 갯수(val)를 구한다.
        int val = 0;
        for (int pos = 2; pos >= 0; pos--) {
            int bit = (*(src + i) >> j) & 1; // 앞에서부터 1 bit씩 추출
            if (pos == 2) val += bit * 4;
            else if (pos == 1) val += bit * 2;
            else val += bit;
            j--;
            if (j < 0) {
                j = 7;
                i++;
                // 마지막에 도달했을 때 쓰레기 값을 읽어올 수 있으므로 loop을 종료한다.
                if(i == srclen){
                    break;
                }
            }
        }

        // Padding (항상 val = 0)이외의 값이 있을경우 무시
        if((length == dstlen) && val != 0)
            return -1;

        // 갯수(val)만큼 해당하는 bit을 입력한다.
        while(val > 0){
            writeBit(idx, dst+length, curr_bit);
            idx--;
            val--;

            if (idx < 0) {
                idx = 7;
                length++;

                // Padding이 존재할 수 있으므로 length == dstlen만으로 return -1하면 안됨.
                if (length == dstlen && val != 0)
                    return -1;
            }
        }
        curr_bit = 1 - curr_bit; // bit 전환
    }
    return length;
}
