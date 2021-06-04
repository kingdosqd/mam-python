#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import pymysql
import time, datetime
from decimal import Decimal
import sys
import os
import config
import logging
import traceback
import bbc_lib


url = config.url
connection = pymysql.connect(host=config.host, port=config.port, user=config.user, password=config.password, db=config.db)

def ExecSql(sql):
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        return cursor.lastrowid
    except Exception as e:
        return 0


def GetTask():
    with connection.cursor() as cursor:
        sql = 'SELECT id,block_hash from Task where is_ok = 0 limit 1'
        cursor.execute(sql)
        connection.commit()
        return cursor.fetchone()


def SbumitTask(taskid):
    with connection.cursor() as cursor:
        sql = 'update Task set is_ok = 1 where id = %s' % taskid
        cursor.execute(sql)
        connection.commit()


def GetBlock(block_hash):
    with connection.cursor() as cursor:
        sql = 'select `hash`,prev_hash,height from block where hash = "%s"' % block_hash
        cursor.execute(sql)
        connection.commit()
        return cursor.fetchone()

def GetUsefulBlock(block_hash):
    with connection.cursor() as cursor:
        sql = 'select `hash`,prev_hash,height from block where is_useful = 1 and hash = "%s"' % block_hash
        cursor.execute(sql)
        connection.commit()
        return cursor.fetchone()


def GetVote(hex_str):
    client_addr = bbc_lib.Hex2Addr(hex_str[0:66])
    dpos_addr = bbc_lib.Hex2Addr(hex_str[66:])    
    return client_addr,dpos_addr

def GetDbVote(sendto):
    with connection.cursor() as cursor:
        sql = 'select client_in, dpos_in from tx where type = "token" and `to` = "%s"' % sendto
        cursor.execute(sql)
        res = cursor.fetchone()
        return res[0],res[1]

def InsertTx(block_id,tx,cursor):
    in_money = Decimal(0)
    for vin in tx["vin"]:
        sql = "select id,amount,`to` from tx where txid = %s and n = %s"
        cursor.execute(sql,[vin["txid"],vin["vout"]])
        res = cursor.fetchone()
        in_money = in_money + res[1]
        sql = "update tx set spend_txid = %s where id = %s"
        cursor.execute(sql,[tx["txid"], res[0]])
    dpos_in = None
    client_in = None
    dpos_out = None
    client_out = None
    if tx["sendto"][:4] == "21c0":
        if tx["type"] == 'token':
            client_in,dpos_in = GetVote(tx["sig"][0:132])
        else:
            client_in,dpos_in = GetDbVote(tx["sendto"])
    if tx["sendfrom"][:4] == "20c0":
        client_out,dpos_out = GetDbVote(tx["sendfrom"])

    data = None
    if len(tx["data"]) > 0:
        data = tx["data"]
        if tx["type"] == 'certification':
            data = 'certification'
        elif len(data) >= 4096:
            data = data[:4096]     
    sql = "insert tx(block_hash,txid,`from`,`to`,amount,fee,`type`,n,`data`,dpos_in,client_in,dpos_out,client_out,transtime)values(%s,%s,%s,%s,%s,%s,%s,0,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql,[block_id,tx["txid"], tx["sendfrom"],tx["sendto"],tx["amount"],tx["txfee"],tx["type"],data,dpos_in,client_in,dpos_out,client_out,tx["time"]])
    amount = Decimal("%.6f" % tx["amount"])
    txfee = Decimal("%.6f" % tx["txfee"])
    if in_money > (amount + txfee):
        amount = in_money - (amount  + txfee)
        sql = "insert tx(block_hash,txid,`from`,`to`,amount,fee,`type`,n,data,transtime)values(%s,%s,%s,%s,%s,%s,%s,1,%s,%s)"
        cursor.execute(sql,[block_id,tx["txid"],tx["sendfrom"],tx["sendfrom"],amount,0,tx["type"],data,tx["time"]])

def RollBACK(block_hash):
    with connection.cursor() as cursor:
        sql = "update block set is_useful = 0 where `hash` = '%s'" % block_hash
        cursor.execute(sql)
        sql = "SELECT txid from Tx where block_hash = '%s' ORDER BY id desc" % block_hash
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            sql = "update Tx set spend_txid = null where spend_txid = '%s'" % row[0]
            cursor.execute(sql)
            sql = "Delete from Tx where txid = '%s'" % row[0]
            cursor.execute(sql)
        connection.commit()

def Useful(block_hash):
    with connection.cursor() as cursor:
        data = {"id":1,
                "method":"getblockdetail",
                "jsonrpc":"2.0",
                "params":{"block": block_hash}
                } 
        response = requests.post(url, json=data)
        obj = json.loads(response.text)
        if "result" in obj:
            obj = obj["result"]
        else:
            return False
        
        if GetBlock(block_hash) == None:
            sql = "insert into block(hash,prev_hash,time,height,reward_address,bits,reward_money) values(%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,[obj["hash"],obj["hashPrev"],obj["time"],obj["height"],obj["txmint"]["sendto"],obj["bits"],obj["txmint"]["amount"]])
        else:
            sql = "update block set is_useful = 1 where `hash` = '%s'" % block_hash
            cursor.execute(sql)
        
        for tx in obj["tx"]:
            InsertTx(block_hash,tx,cursor)
        InsertTx(block_hash,obj["txmint"],cursor)
        connection.commit()
        return True


def GetEndData():
    with connection.cursor() as cursor :
        sql = "SELECT `hash`, prev_hash,height from block ORDER BY id DESC LIMIT 1"
        cursor.execute(sql)
        connection.commit()
        return cursor.fetchone()


def GetPrev(b_hash):
    sql = "SELECT b2.`hash`,b2.prev_hash,b2.height from Block b1 inner JOIN Block b2 on b1.prev_hash = b2.`hash` where b1.`hash` = '%s'" % b_hash
    with connection.cursor() as cursor :
        cursor.execute(sql)
        connection.commit()
        return cursor.fetchone()

def UpdateState(prev_hash,height):
    p2_hash = None # RollBACK end block
    p2_height = 0
    p3_hash = prev_hash # current prev block (P2 may not equal P3)
    p3_height = height
    
    RollBack = []
    UseBlock = []
    end_data = GetEndData()
    p2_hash = end_data[0]
    p2_height = end_data[2]
    if p2_hash == p3_hash:
        return
    if p2_height > p3_height:
        RollBack.append(p2_hash)
        while True:
            res = GetPrev(p2_hash)
            p2_height = res[2]
            p2_hash = res[0]
            if res[2] == p3_height:
                break
            RollBack.append(p2_hash)
    elif p3_height > p2_height:
        UseBlock.append(p3_hash)
        while True:
            res = GetPrev(p3_hash)
            p3_height = res[2]
            if res[2] == p2_height:
                break
            p3_hash = res[0]
            UseBlock.append(p3_hash)
    
    while p2_hash != p3_hash:
        RollBack.append(p2_hash)
        
        res2 = GetPrev(p2_hash)
        p2_hash = res2[0]
        
        res3 = GetPrev(p3_hash)
        p3_hash = res3[0]
        if p2_hash != p3_hash:
            UseBlock.append(p3_hash)

    for cancel_hash in RollBack:
        RollBACK(cancel_hash)

    UseBlock.reverse()
    for use_hash in UseBlock:
        Useful(use_hash)

def ExecTask(block_hash):
    task_add = []
    db_res = GetUsefulBlock(block_hash)
    while db_res == None:
        #print(block_hash,"dddd")
        #time.sleep(30000)
        task_add.append(block_hash)
        data = {"id":1,
                "method":"getblock",
                "jsonrpc":"2.0",
                "params":{"block": block_hash}
                }
        response = requests.post(url, json=data)
        res = json.loads(response.text)
        if "result" in res:
            res = res["result"]
        else:
            print("RollBack",block_hash)
            return
        block_hash = res["hashPrev"]
        print(res["height"])
        if res["height"] == 0:
            break
        db_res = GetUsefulBlock(block_hash)
    if db_res != None:
        UpdateState(db_res[0],db_res[2])

    task_add.reverse()
    for use_hash in task_add:
        print("begin", use_hash)
        if Useful(use_hash) == False:
            print("use_hash Error",use_hash)
            return

def Getblockhash(height):
    data = {"id":1,
            "method":"getblockhash",
            "jsonrpc":"2.0",
            "params":{
                "height":height
            }}
    response = requests.post(url, json=data)
    return json.loads(response.text)

def Getforkheight():
    data = {"id":2,
            "method":"getforkheight",
            "jsonrpc":"2.0",
            "params":{ 
            }}

    response = requests.post(url, json=data)
    #print(response.text)
    obj = json.loads(response.text)
    if "result" in obj:
        obj = obj["result"]
    else:
        return False
    
    end_data = GetEndData()
    if end_data == None:
        return 1
    if obj > end_data[2]:
        if (obj - end_data[2]) > 100:
            return end_data[2] + 100
        return obj
    else:
        return 0

def Run():
    height = Getforkheight()
    if height > 0:
        obj = Getblockhash(height)
        if "result" in obj:
            blockHash = obj["result"][-1]
            ExecTask(blockHash)

if __name__ == '__main__':
    while True:
        height = Getforkheight()
        if height > 0:
            obj = Getblockhash(height)
            print(obj)
            if "result" in obj:
                blockHash = obj["result"][-1]
                ExecTask(blockHash) 
            else:
                print("getblockhash error:",obj)   
                time.sleep(3)                    
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"wait task 3s ...")
            time.sleep(3)