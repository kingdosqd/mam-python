#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import json
import time
import pymysql
import traceback 
import sys
import os

def CreateAddr():
    cmd = "bitcoin-cli getnewaddress mam_test legacy"
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    address = info.stdout.strip("\n") 
    cmd = "bitcoin-cli dumpprivkey %s" % address
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    privkey = info.stdout.strip("\n")
    info = json.dumps({"privkey":privkey,"address":address},indent=4)
    print(info)

if __name__ == '__main__':

    # bitcoin-cli createwallet mam_test
    # bitcoin-cli encryptwallet 123456
    # bitcoin-cli walletpassphrase 123456 36000

    # bitcoin-cli getnewaddress mam_test legacy
    # -> 1FZ7967QJ9JvyBYy1UmaMEW3FBTYmGkej2

    # bitcoin-cli dumpprivkey 1FZ7967QJ9JvyBYy1UmaMEW3FBTYmGkej2
    # -> Ky9pYxCxLJWbneeEzHtdRT9ZwUhe3tKyF2nezgaCn8VJAyWVvBNw
    
    # bitcoin-cli importprivkey Ky9pYxCxLJWbneeEzHtdRT9ZwUhe3tKyF2nezgaCn8VJAyWVvBNw mam_test false
    # ->

    # bitcoin-cli getaddressesbylabel mam_test
    # -> list[data]

    # bitcoin-cli getbalance
    # -> 0

    info = '''[
    {
        "privkey": "Kwk5FhLsXJNDnAGVRz6uLPSDiubVHBfhH1rTJc5Ks2LGriwC3kB4",
        "address": "16RVHVpciNCAAj9NmQKNh7QS8TyUCwnqy4"
    },
    {
        "privkey": "L3gNQ2RkZMKfYvjPomzVMNuDyEZC41Wv9vyforrBHYDoGZngF7uu",
        "address": "1H73DRzdeAjsmhtkme2tGEHZfLDxRgvPjd"
    },
    {
        "privkey": "L1su6KScGhoRy8hnNAsjymeW3HGAMhVDG42NsCA2b5f8RaAbnrFj",
        "address": "1Eyokpvd9tYKCsvPJSHfArkb9Kqwb5qcJi"
    }
]'''
    print(info)
    #CreateAddr()