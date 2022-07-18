#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@file: fish2.py
@version: 0.0.1
@author: xxx
@time: 2022/1/21 11:07
@software: IntelliJ IDEA
@site: 
"""
import sys
import json
import random
import asyncio
import websockets

# jwt文件，绝对路径
JWT_FILE = 'D:/token.txt'
# wss地址
WSS_URL = 'wss://fat4-gateway.testbitgame.com/ws/bitfish_arena'
# 按照顺序定义操作流程
PIPELINE = ['sign', 'enter', 'change', 'shoot', 'hit']
# 炮台编号列表
BET_LIST = [2, 3, 4, 5, 10, 15, 20]


async def worker(ws, action, jwt, bet_code):
    print('[INFO] action: {0}, start...'.format(action))
    await ws.send(json.dumps(basic_data(action, jwt, bet_code)))
    print('[INFO] action: {0}, completed'.format(action))
    print('[INFO] action: {0}, waiting reply...'.format(action))
    reply = await ws.recv()
    print('[INFO] action: {0}, response: {1}'.format(action, reply))
    if json.loads(reply).get('code') != 0:
        raise Exception('[ERROR] action {0} response failed'.format(action))
    print('[INFO] action: {0} response is ok'.format(action))       


def read_jwt():
    jwt_list = []
    with open(JWT_FILE) as f:
        c = f.readlines()
        for i in c:
            short = i.strip()
            if short is None:
                continue
            jwt_list.append(short)
    return jwt_list


async def conn():
    # 读取jwt配置
    jwt_list = read_jwt()
    for i in jwt_list:
        # ws_url = WSS_URL + i.strip()
        ws_url = WSS_URL
        # 预定义炮台
        bet_code = random.choice(BET_LIST)
        # 执行交互任务
        print('[INFO] start connect wss address {0} ...'.format(ws_url))
        async with websockets.connect(ws_url) as ws:
            for p in PIPELINE:
                await worker(ws, p, i, bet_code)


def basic_data(action, jwt, bet_count):
    """
    请求数据构造方法，根据操作（action）类型，获取指定的数据。
    :param action: 操作类型，当前支持报名sign、进入房间enter、切换炮台change、同步射击动作shoot和击中鱼hit
    :param jwt: JSON Web Token
    :param bet_count:
    :return: 已构造的请求数据
    """
    data = {
        'sign': {
            'cmd': 'signUp',
            'params': {
                'jwt': jwt,
                'currency': 'USDT'
            }
        },
        'enter': {
            "cmd": "enterGame",
            "params": {
                "jwt": jwt,
                "currency": "USDT"
            }
        },
        'change': {
            "cmd": "changeTurret",
            "params": {
                "jwt": jwt,
                "multiple": bet_count
            }
        },
        'shoot': {
            "cmd": "shoot",
            "params": {
                "jwt": jwt,
                "direction": {
                    "x": 0.8563146985136435,
                    "y": -0.516454390154143
                }
            }
        },
        'hit': {
            "cmd": "hit",
            "params": {
                "jwt": jwt,
                "multiple": bet_count
            }
        }
    }
    return data.get(action)


if __name__ == '__main__':
    # 配置文件校验
    if len(WSS_URL.strip()) == 0 or len(JWT_FILE.strip()) == 0:
        print('[ERROR] WSS_URL or JWT_FILE configuration is empty!')
        sys.exit(1)
    asyncio.get_event_loop().run_until_complete(conn())
