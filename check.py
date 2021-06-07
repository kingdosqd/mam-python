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
from sqlalchemy import text

from sqlalchemy.sql.expression import null, true
from operator import add, itemgetter, attrgetter

import re
import subprocess

from sqlalchemy.sql.functions import GenericFunction
import bbc_lib

context = decimal.getcontext()
context.rounding = decimal.ROUND_DOWN

Base = declarative_base()

engine = create_engine("mysql+pymysql://root:root@localhost:3306/minemon", encoding="utf-8")

class Tx(Base):
    __tablename__ = 'tx'
    id = Column(INTEGER, primary_key=True)
    txid = Column(VARCHAR(256), nullable=False)
    block_hash = Column(VARCHAR(256), nullable=False)
    type = Column(VARCHAR(256), nullable=False)
    #from_ = Column(VARCHAR(256), nullable=False)
    to = Column(VARCHAR(256), nullable=False)
    amount = Column(DECIMAL, nullable=False)
    fee = Column(DECIMAL, nullable=False)
    dpos_in = Column(VARCHAR(256), nullable=False)
    client_in = Column(VARCHAR(256), nullable=False)
    height = Column(INTEGER)
    data = Column(VARCHAR(256), nullable=False)

class Block(Base):
    __tablename__ = 'block'
    id = Column(INTEGER, primary_key=True)
    hash = Column(VARCHAR(256), nullable=False)
    prev_hash = Column(VARCHAR(256), nullable=False)
    time = Column(INTEGER)
    height = Column(INTEGER)
    reward_address = Column(VARCHAR(256), nullable=False)
    reward_money = Column(DECIMAL, nullable=False)
    bits = Column(INTEGER)

def TestWork():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Blocks = session.query(Block).filter(Block.height>0).all()
    conn = engine.connect()
    for block in Blocks:
        res = conn.execute(text("SELECT fee FROM tx where block_hash = '%s'" % (block.hash)))
        s = Decimal("0.0")
        for obj in res:
            s += obj.fee
        assert(s + Decimal("38.2") == block.reward_money)
    print("TestWork OK")

def SetVote(Vote,tx):
    if tx.dpos_in in Vote:
        Vote[tx.dpos_in]["v"] += tx.amount
        if tx.to in Vote[tx.dpos_in]["info"]:
            Vote[tx.dpos_in]["info"][tx.to]["vote"] += tx.amount
        else:
            Vote[tx.dpos_in]["info"][tx.to] = {
                "vote":tx.amount,
                "stake":0
            }
    else:
        Vote[tx.dpos_in] = {
            "v":tx.amount,
            "info":{
                tx.to : {
                    "vote":tx.amount,
                    "stake":0
                },
                tx.dpos_in: {
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
        vote = Vote[pool_in]["info"][miner]["vote"]
        if vote > Decimal("10000.0"):
            vote = Decimal("10000.0")
        vote_sum += vote

    for miner in Vote[pool_in]["info"]:
        v = Vote[pool_in]["info"][miner]["vote"]
        if v > Decimal("10000.0"):
            v = Decimal("10000.0")
        Vote[pool_in]["info"][miner]["stake"] += stake * Decimal("0.95") * v / vote_sum

    
def DelStake(Vote):
    for pool_in in Vote:
        assert pool_in != ""
        for miner in Vote[pool_in]["info"]:
            assert miner != ""
            Vote[pool_in]["info"][miner]["stake"] = Decimal("0")


def CheckStake(Vote,tx):
    for pool_in in Vote:
        if pool_in == None:
            continue
        for miner in Vote[pool_in]["info"]:
            if miner == tx.to and miner[:4] == "21c0":
                s1 = Vote[pool_in]["info"][miner]["stake"]
                s2 = tx.amount
                print(tx.to,s2,abs(s1 - s2))
                assert abs(s1 - s2) < Decimal("0.000008")
            
            if miner == bbc_lib.Hex2Addr(tx.data) and tx.to[:1] == "1":
                s1 = Vote[pool_in]["info"][miner]["stake"]
                s2 = tx.amount
                print(tx.to,s2,abs(s1 - s2))
                assert abs(s1 - s2) < Decimal("0.000008")
                
def GetBlockTx(blockhash):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT *, `from` as from_ FROM tx where block_hash = '%s'" % (blockhash)))
    tx_stake = []
    tx_vote = []
    for tx in result:
        if tx.type == 'stake':
            tx_stake.append(tx)
        if tx.type == 'token' and tx.to[0:4] == "21c0":
            tx_vote.append(tx)
    return tx_stake,tx_vote

def TestStake():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Blocks = session.query(Block).filter(Block.height>0).all()
    TotalReward = Decimal("0")
    MoneySupply = Decimal("0")
    Stakes = []
    Vote = {}
    N_ = Decimal("100")
    M_ = N_ * 100
    for block in Blocks:
        tx_stake,tx_vote = GetBlockTx(block.hash)
        cmd = "cat ~/.minemon/logs/* ~/.minemon/logs-collector/* 2>/dev/null | grep 'CalcPledgeRewardValue: height: %s,' | tail -n 1" % (block.height)
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
            assert TotalReward == searchObj["TotalReward"],(block.height,TotalReward,searchObj["TotalReward"])
            assert MoneySupply == searchObj["MoneySupply"],(block.height,MoneySupply,searchObj["MoneySupply"])
            Stake_ = searchObj["Reward"]
            #print("height:",height,"test OK.")
            #print(block.height)
            #print(searchObj)
        if len(tx_stake) > 0:
            sum_stake = Decimal("0")
            for tx in tx_stake:
                sum_stake += tx.amount
                if tx.to[:4] != "20g0":
                    CheckStake(Vote,tx)
            sum_stake_ = sum(Stakes)
            #print(len(Stakes))
            assert sum_stake == sum_stake_,(block.height,sum_stake,sum_stake_)
            print("height:",block.height,"stake OK.")
            #### 结束验证

            ## 清空数据
            Stakes = []
            DelStake(Vote)

        Stake = Decimal("0")
        pool_addr = block.reward_address
        
        if pool_addr in Vote:
            if Vote[pool_addr]["v"] > M_:
                Stake = round((TotalReward - MoneySupply + Decimal("61.8")),6)
            else:
                Stake = round((TotalReward - MoneySupply + Decimal("61.8")) * Vote[pool_addr]["v"] / M_,6)
            assert Stake_ == Stake,(Stake_,Stake,block.height)

        #### 更新数据
        Stakes.append(Stake)
        TotalReward += Decimal("100.0")
        MoneySupply += Decimal("38.2") + Stake

        # 把奖励金额给分掉
        if Stake > Decimal("0"):
            SetStake(Vote,pool_addr,Stake)
        # 更新投票
        ## 转账的投票
        for tx in tx_vote: # info[height]["vote"]:   
            SetVote(Vote,tx)
        ## 奖励的投票
        for tx in tx_stake: # info[height]["stake"]:
            # 给矿池发放的奖励不是投票
            if tx.dpos_in != "":
                SetVote(Vote,tx)

    session.close()

if __name__ == '__main__':
    TestWork()
    TestStake()