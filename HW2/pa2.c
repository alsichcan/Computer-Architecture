//---------------------------------------------------------------
//
//  4190.308 Computer Architecture (Fall 2021)
//
//  Project #2: FP10 (10-bit floating point) Representation
//
//  October 5, 2021
//
//  Jaehoon Shim (mattjs@snu.ac.kr)
//  Ikjoon Son (ikjoon.son@snu.ac.kr)
//  Seongyeop Jeong (seongyeop.jeong@snu.ac.kr)
//  Systems Software & Architecture Laboratory
//  Dept. of Computer Science and Engineering
//  Seoul National University
//
//---------------------------------------------------------------

#include "pa2.h"

void writeBit(int idx, unsigned char* dst, int val){
    int mask = 1 << idx;
    *dst = (*dst & ~mask) | (val << idx);
}

void writeFP10(unsigned short* dst, int sign, int exp, unsigned char frac){
    // Write the Sign Bit
    for(int i = 7; i > 0; i--){
        writeBit(i,((unsigned char *)dst) + 1, sign);
    }

    // Write the Exponent
    for(int pos = 4; pos <= 8; pos++){
        int bit = exp % 2;
        exp /= 2;

        if(pos == 8) writeBit(0, ((unsigned char *)dst) + 1, bit);
        else writeBit(pos, ((unsigned char *)dst), bit);
    }

    // Write the Fraction
    for(int pos = 3; pos >= 0; pos--){
        int bit = (frac >> pos) & 1; // 앞에서부터 1bit씩 추출
        writeBit(pos, ((unsigned char *)dst), bit);
    }
}

void writeFP(float* dst, int sign, int exp, unsigned char frac){
    // Write the Sign Bit
    writeBit(7,((unsigned char *)dst) + 3, sign);

    // Write the Exponent
    for(int pos = 0; pos <= 7; pos++){
        int bit = exp % 2;
        exp /= 2;

        if(pos == 0) writeBit(7, ((unsigned char *)dst) + 2, bit);
        else writeBit(pos-1, ((unsigned char *)dst) + 3, bit);
    }

    // Write the Fraction
    for(int pos = 3; pos >= 0; pos--){
        int bit = (frac >> pos) & 1; // 앞에서부터 1bit씩 추출
        writeBit(pos+3, ((unsigned char *)dst) + 2, bit);
    }
}

void writeInfinity(unsigned short* dst, int sign){
    writeFP10(dst, sign, 31, 0);
}

/* Convert 32-bit signed integer to 10-bit floating point */
fp10 int_fp10(int n)
{
    unsigned short result = 0;
    int sign = 0;
    int exp = 0;

    // Variable for Fraction
    int frac = 0;
    int frac_idx = 3;
    int ls_bit = 0;
    int round_bit = 0;
    int sticky_bit = 0;

    unsigned int value;
    if(n < 0){
        sign = 1;
        value = (unsigned int) (n * -1);
    } else{
        value = (unsigned int) n;
    }
    unsigned char* src = (unsigned char *) &value;

    // Little Endian 반영하여 뒤의 Byte부터 추출한다.
    for(int i = sizeof(int)-1; i >= 0; i--){
        for(int j = 7; j  >= 0; j--){
            int bit = (*(src + i) >> j) & 1; // 앞에서부터 1bit씩 추출

            // Exp에 대한 처리 - Sign bit을 제외한 가장 첫번째 1일 때
            if(exp == 0 && bit == 1){
                exp = i * 8 + j;
                exp += 15;
                // Infinity에 대한 처리 - Exp가 범위를 벗어날 때
                if (exp > 30){
                    writeInfinity(&result, sign);
                    return result;
                }
                continue;
            }

            // Fraction에 대한 처리
            if(exp != 0){
                if(frac_idx >= 0){
                    if(bit == 1) frac += 1 << frac_idx;
                    if(frac_idx == 0) ls_bit = bit;
                }
                else if(frac_idx == -1) round_bit = bit;
                else if(bit == 1) sticky_bit = bit;
                frac_idx--;
            }
        }
    }

    // -0에 대한 처리 - Sign bit을 바꿔준다.
    if(sign == 1 && exp == 0 && frac == 0) sign = 0;

    // Round-to-Even 처리 - Round-down은 별도로 처리할 필요가 없다.
    if(round_bit == 1){
        if((sticky_bit == 1) || (ls_bit == 1)){
            frac++;
            if(frac == 16){ // Re-normalize
                frac = 0;
                exp++;
                if(exp > 30){ // Overflow
                    writeInfinity(&result, sign);
                    return result;
                }
            }
        }
    }
    writeFP10(&result, sign, exp, (unsigned char) frac);
	return result;
}

/* Convert 10-bit floating point to 32-bit signed integer */
int fp10_int(fp10 x)
{
    int result = 0;
    int exp = 0;
    int frac = 0;

	unsigned short value = x;
    unsigned char* src = (unsigned char *) &value;

    // Sign bit 추출
    int sign = (*(src + 1) >> 7) & 1;

    // Exp 추출
    for(int pos = 4; pos >= 0; pos--){
        if(pos == 4) exp += ((*(src + 1) >> 0) & 1) << pos;
        else exp += ((*src >> (pos + 4)) & 1) << pos;
    }

    // Fraction 추출
    for(int pos = 3; pos >= 0; pos--){
        frac += ((*src >> pos) & 1) << pos;
    }

    // Denormalized : Special Values (Infinity, NaN)
    if(exp == 31) result = 0x80000000;
    // Denoramlized : -0과 0처리
    else if(exp == 0 && frac == 0) result = 0;
    else{ // Normalized value
        frac += 1 << 4;
        exp -= (1 << (5 - 1)) - 1;
        if(exp >= 4) result += frac << (exp-4);
        else result += (int) (frac >> (4-exp));

        if(sign == 1) result *= -1;
    }
	return result;
}

/* Convert 32-bit single-precision floating point to 10-bit floating point */
fp10 float_fp10(float f)
{
    unsigned short result = 0;
    int sign = 0;
    int exp = 0;

    // Variable for Fraction
    int frac = 0;
    int frac_idx = 3;
    int ls_bit = 0;
    int round_bit = 0;
    int sticky_bit = 0;

    unsigned char* src = (unsigned char *) &f;

    // Sign bit 추출
    sign = (*(src + sizeof(float) - 1) >> 7) & 1;

    // Exp 추출
    for(int pos = 7; pos >= 0; pos--){
        if(pos >= 1) exp += ((*(src + 3) >> (pos-1)) & 1) << pos;
        else exp += ((*(src + 2) >> 7) & 1) << 0;
    }

    // Fraction 추출
    for(int pos = 22; pos >= 0; pos--){
        int bit = (*(src + pos/8) >> (pos - (pos/8)*8)) & 1;
        if(frac_idx >= 0){
            if(bit == 1) frac += 1 << frac_idx;
            if(frac_idx == 0) ls_bit = bit;
        }
        else if(frac_idx == -1) round_bit = bit;
        else if(bit == 1) sticky_bit = bit;
        frac_idx--;
    }

    // Round-to-Even 처리 - Round-down은 별도로 처리할 필요가 없다.
    if(round_bit == 1){
        if((sticky_bit == 1) || (ls_bit == 1)){
            frac++;
            if(frac == 16){ // Re-normalize
                frac = 0;
                exp++;
            }
        }
    }

    exp = exp - 127 + 15;
    // Denormalized : Special Values (Infinity, NaN)
    if(exp > 30){
        writeInfinity(&result, sign); // Infinity
        if(frac != 0) writeBit(0, (unsigned char*) &result, 1); // NaN
    }
    // Denormalized : 0.0
    else if(exp == 0 && frac == 0){
        writeFP10(&result, sign, 0, 0);
    }
    // Denoramalized : small value very close to 0.0
    else if (exp == 0 && frac != 0){
        sticky_bit = round_bit || sticky_bit;
        round_bit = frac % 2;
        frac = frac >> 1;
        frac += 1 << 3;
        ls_bit = frac % 2;

        // Round-to-Even 처리 - Round-down은 별도로 처리할 필요가 없다.
        if(round_bit == 1){
            if((sticky_bit == 1) || (ls_bit == 1)){
                frac++;
                if(frac == 16){ // Re-normalize
                    frac = 0;
                    exp++;
                }
            }
        }
        writeFP10(&result, sign, exp, (unsigned char) frac);
    }
    else if(exp < 0){
        writeFP10(&result, sign, 0, 0);
    }
    // Normalized value
    else{
        writeFP10(&result, sign, exp, (unsigned char) frac);
    }
     return result;
}

/* Convert 10-bit floating point to 32-bit single-precision floating point */
float fp10_float(fp10 x)
{
    float result = 0;
    int exp = 0;
    int frac = 0;

    unsigned short value = x;
    unsigned char* src = (unsigned char *) &value;

    // Sign bit 추출
    int sign = (*(src + 1) >> 7) & 1;

    // Exp 추출
    for(int pos = 4; pos >= 0; pos--){
        if(pos == 4) exp += ((*(src + 1) >> 0) & 1) << pos;
        else exp += ((*src >> (pos + 4)) & 1) << pos;
    }

    // Fraction 추출
    for(int pos = 3; pos >= 0; pos--){
        frac += ((*src >> pos) & 1) << pos;
    }

    // Denormalized : Special Values (Infinity, NaN)
    if(exp == 31){
        writeFP(&result, sign, 255, 0);
        if(frac != 0) writeBit(0, (unsigned char*) &result, 1);
    }
    // Denoramlized : -0과 0처리
    else if(exp == 0 && frac == 0){
        if(sign == 1) writeBit(7, ((unsigned char*) &result)+3, 1);
    }
    // Denormalized : Small value close to 0.0
    else if(exp == 0 && frac != 0){
        while(frac < 16){
            frac = frac << 1;
            exp--;
        }
        exp = exp - 14 + 127;
        frac -= 16;
        writeFP(&result, sign, exp, frac);
    }
    else{ // Normalized value
        exp = exp - 15 + 127;
        writeFP(&result, sign, exp, frac);
    }
    return result;
}
