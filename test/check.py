#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python 3.6.9
# sqlalchemy 1.4.15(sqlalchemy.__version__)

import decimal
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR,DECIMAL
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal,getcontext

from sqlalchemy.sql.expression import null, true
from operator import add, itemgetter, attrgetter

import re
import subprocess

context = decimal.getcontext()
context.rounding = decimal.ROUND_DOWN

Base = declarative_base()

engine = create_engine("mysql+pymysql://root:root@localhost:3306/minemon", encoding="utf-8")

class Tx(Base):
    __tablename__ = 'tx'
    id = Column(INTEGER, primary_key=True)
    txid = Column(VARCHAR(256), nullable=False)
    height = Column(INTEGER)
    type = Column(VARCHAR(256), nullable=False)
    sendfrom = Column(VARCHAR(256), nullable=False)
    sendto = Column(VARCHAR(256), nullable=False)
    amount = Column(DECIMAL, nullable=False)
    txfee = Column(DECIMAL, nullable=False)
    pool_in = Column(VARCHAR(256), nullable=False)
    miner_in = Column(VARCHAR(256), nullable=False)

def TestWork():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Txs = session.query(Tx).all()
    info = {}
    for tx in Txs:
        if tx.type == 'work':
           info[tx.height] = {
               "work": tx.amount, 
               "txfee" : []}
        else:
            info[tx.height]["txfee"].append(tx.txfee)
    for key in info:
        assert info[key]["work"] == sum(info[key]["txfee"]) + Decimal("38.2"),"pow amount err"
    print("TestWork OK")

def SetVote(Vote,tx):
    if tx.pool_in in Vote:
        Vote[tx.pool_in]["v"] += tx.amount
        if tx.sendto in Vote[tx.pool_in]["info"]:
            Vote[tx.pool_in]["info"][tx.sendto]["vote"] += tx.amount
        else:
            Vote[tx.pool_in]["info"][tx.sendto] = {
                "vote":tx.amount,
                "stake":0
            }
    else:
        Vote[tx.pool_in] = {
            "v":tx.amount,
            "info":{
                tx.sendto : {
                    "vote":tx.amount,
                    "stake":0
                },
                tx.pool_in: {
                    "vote":0,
                    "stake":0
                }
            }
        }

def SetStake(Vote,pool_in,stake):
    assert pool_in != ""
    assert pool_in in Vote
    vote_sum = Decimal("0")
    for miner in Vote[pool_in]["info"]:
        assert miner != ""
        vote_sum += Vote[pool_in]["info"][miner]["vote"]

    for miner in Vote[pool_in]["info"]:
        v = Vote[pool_in]["info"][miner]["vote"]
        Vote[pool_in]["info"][miner]["stake"] += stake * Decimal("0.95") * v / vote_sum

    
def DelStake(Vote):
    for pool_in in Vote:
        assert pool_in != ""
        for miner in Vote[pool_in]["info"]:
            assert miner != ""
            Vote[pool_in]["info"][miner]["stake"] = Decimal("0")


def CheckStake(Vote,tx):
    for pool_in in Vote:
        for miner in Vote[pool_in]["info"]:
            if miner == tx.sendto:
                s1 = Vote[pool_in]["info"][miner]["stake"]
                s2 = tx.amount
                assert abs(s1 - s2) < Decimal("0.000008")    
                

def TestAmount():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Txs = session.query(Tx).all()
    info = {}
    Vote = {}
    for tx in Txs:
        if tx.height not in info:
            info[tx.height] = {
                "work":None,
                "stake":[],
                "vote":[]}
        if tx.type == 'work':
            info[tx.height]["work"] = tx
        if tx.type == 'stake':
            info[tx.height]["stake"].append(tx)
        if tx.type == 'token' and tx.sendto[0:4] == "21c0":
            info[tx.height]["vote"].append(tx)

    N_ = Decimal("100")
    M_ = N_ * 100
    TotalReward = Decimal("0")
    MoneySupply = Decimal("0")
    Stakes = []
    for height in info:
        Stake = Decimal("0")
        pool_addr = info[height]["work"].sendto
        if pool_addr in Vote:
            if Vote[pool_addr]["v"] > M_:
                Stake = round((TotalReward - MoneySupply + Decimal("61.8")),6)
            else:
                Stake = round((TotalReward - MoneySupply + Decimal("61.8")) * Vote[pool_addr]["v"] / M_,6)

        ####  开始验证 
        cmd = "cat ~/.minemon/logs/* ~/.minemon/logs-collector/* 2>/dev/null | grep 'CalcPledgeRewardValue: height: %s,' | head -n 1" % (height)
        res = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,universal_newlines=True)
        searchObj = re.search(r'nTotalReward: (.*), nMoneySupply: (.*), Surplus: .* = (.*), Pledge: .* = (.*), Reward: .* = (.*)', res.stdout, re.M|re.I)
        if searchObj:
            #print(height,searchObj.group())
            searchObj = {
                "TotalReward":Decimal(searchObj.group(1)),
                "MoneySupply":Decimal(searchObj.group(2)),
                "Surplus":Decimal(searchObj.group(3)),
                "Pledge":Decimal(searchObj.group(4)),
                "Reward":Decimal(searchObj.group(5))
            }
            assert TotalReward == searchObj["TotalReward"],(height,TotalReward,searchObj["TotalReward"])
            assert MoneySupply == searchObj["MoneySupply"],(height,MoneySupply,searchObj["MoneySupply"])
            #assert Stake == searchObj["Reward"],(height,Stake,searchObj["Reward"])
            #print("height:",height,"test OK.")

        if len(info[height]["stake"]) > 0:
            sum_stake = Decimal("0")
            for tx in info[height]["stake"]:
                sum_stake += tx.amount
                if tx.sendto[:4] != "20g0":
                    CheckStake(Vote,tx)
            assert sum_stake == sum(Stakes),(height,sum_stake,sum(Stakes))
            print("height:",height,"stake OK.")
            #### 结束验证

            ## 清空数据
            Stakes = []
            DelStake(Vote)

        #### 更新数据
        Stakes.append(Stake)
        TotalReward += Decimal("100.0")
        MoneySupply += Decimal("38.2") + Stake
        
        # 把奖励金额给分掉
        if Stake > Decimal("0"):
            SetStake(Vote,pool_addr,Stake)
        # 更新投票
        ## 转账的投票
        for tx in info[height]["vote"]:   
            SetVote(Vote,tx)
        ## 奖励的投票
        for tx in info[height]["stake"]:
            # 给矿池发放的奖励不是投票
            if tx.pool_in != "":
                SetVote(Vote,tx)

    session.close()
    print("TestAmount OK")
        
if __name__ == '__main__':
    TestWork()
    TestAmount()