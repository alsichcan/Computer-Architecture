#include <stdio.h>

void f(char *p){
    printf("%x %x\n", *p, *(p+2));
}


int main() {
    long i = 0xFFFFFFFFFFFFFFFFFF;
    printf("%d", (i << 31));
}
