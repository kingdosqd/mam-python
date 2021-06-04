%module bbc_lib

%{
    #include "bbc_lib.h"
%}

extern char* Addr2Hex(const char *addr);
extern char* Hex2Addr(const char *hex);


