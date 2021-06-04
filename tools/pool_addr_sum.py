#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import json
from sys import stderr

def Run(obj):
    cmd = "minemon-cli importprivkey %s 123" % obj["privkey"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    pubkey = info.stdout.strip("\n")
    cmd = "minemon-cli unlockkey %s 123 10" % pubkey
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    cmd = "minemon-cli getpubkeyaddress %s" % pubkey
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    addr = info.stdout.strip("\n")
    cmd = "minemon-cli addnewtemplate mint '{\"spent\": \"%s\", \"pledgefee\":%s}'" % (addr,obj["pledgefee"])
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    cmd = "minemon-cli getbalance -a=%s" % obj["pool_addr"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    bs = json.loads(info.stdout.strip("\n"))
    s = 0
    for b in bs:
        s += b["avail"]
    if s > 0.01:
        cmd = "minemon-cli sendfrom %s 1x6pbay33eezmm1rvheyfsqpedr0y0n6fb1gne353c9fapzrw6f1a6mpc %s %s" % (obj["pool_addr"],s-0.01,0.01)
        info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
        print(info.stdout.strip("\n"))

if __name__ == '__main__':
    #"privkey" : "0a877ddf72a531748a6123640652b22220493752d0b2abcf75fd11e899c748ae",
    #"pubkey" : "c2331c7fab5e62a30c576158cf54e0016ecedefcbc8b1b074abf736378b5ace9"
    # 1x6pbay33eezmm1rvheyfsqpedr0y0n6fb1gne353c9fapzrw6f1a6mpc
    #cmd = "minemon-cli importprivkey 0a877ddf72a531748a6123640652b22220493752d0b2abcf75fd11e899c748ae 123"
    #info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    #pubkey = info.stdout.strip("\n")
    #cmd = "minemon-cli unlockkey c2331c7fab5e62a30c576158cf54e0016ecedefcbc8b1b074abf736378b5ace9 123 0" % pubkey
    #info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    #print(info.stdout)
    #cmd = "minemon-cli unlockkey 9fd0d2dd4b5480b45dfcb9e877757166ab709faa8f9a9e6aca1fcb9ef0e8b67d 123 0"
    cmd = "minemon-cli getforkheight"
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    if info.stderr != '':
        print("OK")
    exit()

    with open('/home/shang/mam/pool-mam/test-mam/privkey.json') as f:
        objs = json.load(f)
        for obj in objs:
            print(obj)
            Run(obj)