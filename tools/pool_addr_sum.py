#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import json
from sys import stderr

from config import boss

def Run(obj):
    cmd = "minemon-cli importprivkey %s 123" % obj["privkey"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    pubkey = info.stdout.strip("\n")
    cmd = "minemon-cli unlockkey %s 123 10" % pubkey
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    cmd = "minemon-cli getpubkeyaddress %s" % pubkey
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    addr = info.stdout.strip("\n")
    cmd = 'minemon-cli addnewtemplate mint \'{"spent": "%s", "pledgefee":%s}\'' % (addr,obj["pledgefee"])
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    cmd = "minemon-cli getbalance -a=%s" % obj["pool_addr"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    bs = json.loads(info.stdout.strip("\n"))
    s = 0
    for b in bs:
        s += b["avail"]
    if s > 0.01:
        cmd = "minemon-cli sendfrom %s %s %s %s" % (obj["pool_addr"],boss["addr"], s-0.01,0.01)
        info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
        print(info.stdout.strip("\n"))

if __name__ == '__main__':
    cmd = "minemon-cli getbalance -a=%s" % boss["addr"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    print(info.stdout.strip("\n"))
    with open('./privkey.json') as f:
        objs = json.load(f)
        for obj in objs:
            #print(obj)
            Run(obj)
    cmd = "minemon-cli getbalance -a=%s" % boss["addr"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    print(info.stdout.strip("\n"))