#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import json
import time
import pymysql
import bbc_lib


connection = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="root", db="minemon")

def ExecSql(sql):
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        return cursor.lastrowid
    except Exception as e:
        print(e,sql)
        return 0


def get_tx_data(txid,height,bits):
    cmd = 'minemon-cli gettransaction %s' % txid
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    objs = json.loads(info.stdout)
    tx = objs["transaction"]
    pool_in = ""
    miner_in = ""
    if tx["sendto"][:4] == "21c0" and tx["type"] == 'token':
        miner_in = bbc_lib.Hex2Addr(tx["sig"][:66])
        pool_in = bbc_lib.Hex2Addr(tx["sig"][66:66+66])
    
    sql = "insert tx(txid,height,type,sendfrom,sendto,amount,txfee,bits,pool_in,miner_in)values('%s',%d,'%s','%s','%s',%f,%f,'%s','%s','%s')" \
        % (tx["txid"],height,tx["type"],tx["sendfrom"],tx["sendto"],tx["amount"],tx["txfee"],bits,pool_in,miner_in)
    #print(sql)
    ExecSql(sql)

def get_block_data(height):
    cmd = 'minemon-cli getblockhash %d' % height
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    if info.stdout == "":
        print("exit at height :",height)
    objs = json.loads(info.stdout)
    cmd = 'minemon-cli getblock %s' % objs[0]
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    objs = json.loads(info.stdout)
    get_tx_data(objs["txmint"],height,objs["bits"])
    for txid in objs["tx"]:
        get_tx_data(txid,height,objs["bits"])

def Run():
    cmd = 'minemon-cli getforkheight'
    info = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    height = int(info.stdout)
    for h in range(1,height+1):
        #print(h)
        get_block_data(h)
        
    ### 更新数据
    sql = "select sendto,pool_in,miner_in from tx where type = 'token'"
    cursor = connection.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    for tr in res:
        if tr[0][:4] == '21c0':
            sql = "update tx set pool_in = %s,miner_in = %s where sendto = %s and pool_in = ''"
            cursor.execute(sql,[tr[1],tr[2], tr[0]])
    connection.commit()

if __name__ == '__main__':
    ExecSql("delete from tx;")
    Run()