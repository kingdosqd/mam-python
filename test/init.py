#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import json
import time
import sys

privkey = "24d0ad81e6af0adc350b0f5962596d409a320a96cd7b6c2ce5dad2e65568a39a"
pubkey = "e89fc4e7d08723124a8037a50b2d9a5006c3f54bc98261b9701bdad81d9cf341"
addr = "187ssr7erv8dq1eb1gb4mqxe30s89mb8bmmvr0jgj4e3x1sy4kzm27jpv"

if len(sys.argv) > 1:
    privkey = "d76a62a1513a6f0f7a196536bc3916f6480c092ff458b09a0473eebae7c88f61"
    pubkey = "d51e71c180bf2731413a0bb737cb0a73eca7d08687047fe7d5cab042b0e28f6d"
    addr = "1dp7y5c22p35dbsvz0j3rdm57xhsgnjsqpw5kmg9h4yzr1gbh3vamb18j"
    print("另外一台机器")

def run_cmd(cmd):
    print(cmd)
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    print(info.stdout)
    time.sleep(1)

run_cmd('minemon-cli stop')
run_cmd('rm -rf ~/.minemon/*')

cmd = '''echo spentaddress=%s '
pledgefee=50
listen4' >> ~/.minemon/minemon.conf
''' % addr

if len(sys.argv) > 1:
    cmd = '''echo spentaddress=%s '
pledgefee=50
connect=192.168.0.103
listen4' >> ~/.minemon/minemon.conf
''' % addr

run_cmd(cmd)

subprocess.run('minemon -daemon',shell=True)
time.sleep(5)
cmd = 'minemon-cli importprivkey %s 123' % privkey
run_cmd(cmd)
cmd = 'minemon-cli unlockkey %s 123 0' % pubkey
run_cmd(cmd)

# 添加挖矿模板
cmd = "minemon-cli addnewtemplate mint '{\"spent\": \"%s\", \"pledgefee\":50}'" % addr
info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
miner_addr = info.stdout.strip("\n")

cmd = "minemon-cli addnewtemplate mintpledge '{\"owner\": \"%s\", \"powmint\": \"%s\", \"rewardmode\":1}'" % (addr,miner_addr)
info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
vote_addr1 = info.stdout.strip("\n")
print(vote_addr1,"-->>",miner_addr)

exit()
# 添加投票模板
#cmd = "minemon-cli addnewtemplate mintpledge '{\"owner\": \"%s\", \"powmint\": \"%s\", \"rewardmode\":1}'" % (privkey,miner_addr)
#info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
#vote_addr1 = info.stdout.strip("\n")

# 赎回模板，投票模板只能向赎回模板转账
#cmd = "minemon-cli addnewtemplate mintredeem '{\"owner\": \"%s\", \"nonce\": 1}'" % privkey
#info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
#mintredeem = info.stdout.strip("\n")

def Vote(miner_addr,pri):
    cmd = "minemon-cli addnewtemplate mintpledge '{\"owner\": \"%s\", \"powmint\": \"%s\", \"rewardmode\":1}'" % (pri,miner_addr)
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    vote_addr1 = info.stdout.strip("\n")
    print(vote_addr1,"-->>",miner_addr)
    cmd = "minemon-cli sendfrom %s %s 100" % (miner_addr,vote_addr1)
    subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)

while True:
    time.sleep(3)
    json_str = subprocess.getoutput('minemon-cli getbalance')
    objs = json.loads(json_str)
    is_break = False
    for obj in objs:
        if obj["address"] == miner_addr and obj["avail"]  > 100:
            is_break = True
            break

    # 给挖矿地址投票
    if is_break:
        Vote(miner_addr,"16rqwvjcr6r458va8cfwyyc5gqh2vj0p6b1b1zan1ga1zg5vqpy3v15m1")
        #Vote(miner_addr,"17nhq5fn5v60x05n6p446ne39rt2g2me0ffez12926st4d3kxr8mbfape")
        #Vote(miner_addr,"1h9pd97xa2xm1w5nj2m7baft082xdy75ccj624g6v5rgc7xbnmf3c6t45")
        break
    run_cmd("minemon-cli getforkheight")


while True:
    time.sleep(3)
    json_str = subprocess.getoutput('minemon-cli getbalance')
    objs = json.loads(json_str)
    is_break = False
    for obj in objs:
        if obj["address"] == miner_addr and obj["avail"]  > 100:
            is_break = True
            break

    # 给挖矿地址投票
    if is_break:
        #Vote(miner_addr,"16rqwvjcr6r458va8cfwyyc5gqh2vj0p6b1b1zan1ga1zg5vqpy3v15m1")
        Vote(miner_addr,"17nhq5fn5v60x05n6p446ne39rt2g2me0ffez12926st4d3kxr8mbfape")
        #Vote(miner_addr,"1h9pd97xa2xm1w5nj2m7baft082xdy75ccj624g6v5rgc7xbnmf3c6t45")
        break
    run_cmd("minemon-cli getforkheight")

while True:
    time.sleep(3)
    json_str = subprocess.getoutput('minemon-cli getbalance')
    objs = json.loads(json_str)
    is_break = False
    for obj in objs:
        if obj["address"] == miner_addr and obj["avail"]  > 100:
            is_break = True
            break

    # 给挖矿地址投票
    if is_break:
        #Vote(miner_addr,"16rqwvjcr6r458va8cfwyyc5gqh2vj0p6b1b1zan1ga1zg5vqpy3v15m1")
        #Vote(miner_addr,"17nhq5fn5v60x05n6p446ne39rt2g2me0ffez12926st4d3kxr8mbfape")
        Vote(miner_addr,"1h9pd97xa2xm1w5nj2m7baft082xdy75ccj624g6v5rgc7xbnmf3c6t45")
        break
    run_cmd("minemon-cli getforkheight")