#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import json
import time

# "spent":"187ssr7erv8dq1eb1gb4mqxe30s89mb8bmmvr0jgj4e3x1sy4kzm27jpv",
#                       "pledgefee":49,
# 
def Vote(pledgefee,mint_addr_index):
    cmd = "minemon-cli makekeypair"
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    obj = json.loads(info.stdout)
    cmd = "minemon-cli getpubkeyaddress " + obj["pubkey"]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    obj["spent"] = info.stdout.strip("\n")
    obj["pledgefee"] = pledgefee
    cmd = "minemon-cli addnewtemplate mint '{\"pledgefee\": %d, \"spent\": \"%s\"}'" % (pledgefee,obj["spent"])
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    obj["pool_addr"] = info.stdout.strip("\n")
    obj["mint_addr_index"] = mint_addr_index
    return obj

data = []
for i in range(100):
   data.append(Vote(50,i))

file_data = json.dumps(data,indent=4,ensure_ascii=False)
with open('./privkey.json','w') as f:
    f.write(file_data)

for key in data:
    del key["privkey"]
    del key["pubkey"]

file_data = json.dumps(data,indent=4,ensure_ascii=False)
with open('./addr.json','w') as f:
    f.write(file_data)
