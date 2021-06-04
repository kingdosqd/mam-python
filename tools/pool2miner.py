#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import json
from sys import stderr
from config import boss,miners,pools

def Vote(miner,pool):
    cmd = "minemon-cli importprivkey %s 123" % miner["privkey"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    cmd = "minemon-cli listkey"
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    keys = json.loads(info.stdout)
    for key in keys:
        if key["key"] == miner["pubkey"]:
            if key["locked"] == True:
                cmd = "minemon-cli unlockkey %s 123 0" % miner["pubkey"]
                info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
                print(info.stdout.strip("\n"))
    cmd = "minemon-cli getbalance -a=%s" % miner["addr"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    m = json.loads(info.stdout)[0]["avail"]
    if m < 210:
        print("Too little money",miner)
        return
    m = m/2
    cmd = 'minemon-cli addnewtemplate mintpledge \'{"owner": "%s", "powmint": "%s", "rewardmode":1}\'' % (miner["addr"],pool["pool_addr"])
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    cmd = "minemon-cli sendfrom %s %s %s %s" % (miner["addr"], info.stdout.strip("\n"),m - 0.01,0.01)
    print(cmd)
    subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    
    cmd = 'minemon-cli addnewtemplate mintpledge \'{"owner": "%s", "powmint": "%s", "rewardmode":2}\'' % (miner["addr"],pool["pool_addr"])
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    cmd = "minemon-cli sendfrom %s %s %s %s" % (miner["addr"], info.stdout.strip("\n"),m - 0.01,0.01)
    print(cmd)
    subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)

if __name__ == '__main__':
    cmd = "minemon-cli importprivkey %s 123" % boss["privkey"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    cmd = "minemon-cli listkey"
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    keys = json.loads(info.stdout)
    for key in keys:
        if key["key"] == boss["pubkey"]:
            if key["locked"] == True:
                cmd = "minemon-cli unlockkey %s 123 0" % boss["pubkey"]
                info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
                print(info.stdout.strip("\n"))
    cmd = "minemon-cli getbalance -a=%s" % boss["addr"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    m = json.loads(info.stdout)[0]["avail"]
    if m > 810:
        m = m * 0.95
        for miner in miners:
            cmd = "minemon-cli sendfrom %s %s %s %s" % (boss["addr"], miner["addr"],m/len(miners) - 0.01,0.01)
            print(m)
            subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    else:
        print("Too little money")
    Vote(miners[0],pools[0])
    Vote(miners[1],pools[0])
    Vote(miners[2],pools[1])
    print("OK")