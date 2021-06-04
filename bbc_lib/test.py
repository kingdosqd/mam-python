#!/usr/bin/env python3
# -*- codeing : utf-8 -*-

import bbc_lib
from bbc import bbc_test2
import threading
import sys
from binascii import a2b_hex

if __name__ == '__main__':
    addr = "1965p604xzdrffvg90ax9bk0q3xyqn5zz2vc9zpbe3wdswzazj7d144mm"
    ret = bbc_lib.Addr2Hex(addr)
    if ret == "01498b63009dfb70f7ee0902ba95cc171f7d7a97ff16d89fd96e1f1b9e7d5f91da":
        ret = bbc_lib.Hex2Addr(ret)
        if ret == "1965p604xzdrffvg90ax9bk0q3xyqn5zz2vc9zpbe3wdswzazj7d144mm":
            print("test1 OK")
        else:
            print("test1 err")
    else:
        print("test1 err")

    addr = "100000000000000000000000000000000000000000000000000000000"
    ret = bbc_lib.Addr2Hex(addr)
    if ret == "010000000000000000000000000000000000000000000000000000000000000000":
        ret = bbc_lib.Hex2Addr(ret)
        if ret == "100000000000000000000000000000000000000000000000000000000":
            print("test2 OK")
        else:
            print("test2 err")
    else:
        print("test2 err")

    addr = "100000000000000000000000000000000000000000000000000000001"
    ret = bbc_lib.Addr2Hex(addr)
    if ret == "err":
        print("test3 OK")
    else:
        print("test3 err")
    bbc_test2()