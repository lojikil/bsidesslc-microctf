#include <stdio.h>

void
printdelta(int delta) {
    int idx = 0;

    if(delta < 0) {
        for(; delta < 0; delta++) {
            printf("+");
        }
    } else {
        for(; delta > 0; delta--) {
            printf("-");
        }
    }
}

int
main(int ac, char **al) {
    int len = 0, tmp = 48, idx = 0, delta = -1;
    if(ac != 2) {
        printf("usage: ip2bf <ipaddress>\n");
        return 1;
    }

    len = strlen(al[1]);

    for(idx = 0; idx < 48; idx++) {
        printf("+");
    }

    printf(">");

    for(idx = 0; idx < 46; idx++) { 
        printf("+");
    }

    printf("<");

    tmp = al[1][0] - 48;
    delta = tmp;

    printdelta(-tmp);

    printf(".");

    for(idx = 1; idx < len; idx++) {
        if(al[1][idx] >= '0' && al[1][idx] <= '9') {
            tmp = al[1][idx] - 48;
            delta -= tmp;
            printdelta(delta);
            delta = tmp;
            printf(".");
        } else if(al[1][idx] == '.') {
            printf(">.<");
        } else {
            break;
        }
    }
    printf("\n");
}
