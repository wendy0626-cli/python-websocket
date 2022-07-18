#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*- author:yyy -*-

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
import time

# jwt文件，绝对路径
JWT_FILE = 'D:/fish_arena.txt'
# wss地址
WSS_URL = 'wss://fat4-gateway.xxx.com/ws/bitfish_arena'
# 按照顺序定义操作流程
# PIPELINE = ['sign', 'enter', 'change', 'shoot', 'hit']
PIPELINE = ['sign', 'enter', 'change']
# 炮台编号列表
# BET_LIST = [2, 3, 4, 5, 10, 15, 20]
BET_LIST = [10, 15, 20]


async def send_msg(ws, data):
    payload = json.dumps(data)
    print('[INFO] data: {0}, send message...'.format(payload))
    await ws.send(payload)
    print('[INFO] data: {0}, send message completed'.format(payload))


async def worker():
    # 读取jwt配置
    jwt_list = read_jwt()
    for i in jwt_list:
        # 预定义炮台
        bet_code = random.choice(BET_LIST)
        # 执行交互任务
        print('[INFO] start connect wss address {0} ...'.format(WSS_URL))
        async with websockets.connect(WSS_URL) as ws:
            for p in PIPELINE:
                data = basic_data(p, i, bet_code)
                await send_msg(ws, data)
                print('[INFO] waiting reply...')
                while True:
                    reply = await ws.recv()
                    if reply == '1':
                        continue
                    print('[INFO] action: {0}, response: {1}'.format(p, reply))
                    resp = json.loads(reply)
                    time.sleep(1)
                    if resp.get('cmd') == 'addFish':
                        continue
                    if resp.get('code') != 0:
                        # 针对用户已报名场景做特殊处理
                        if p == 'sign' and (resp.get('data').get('status') == 4 or resp.get('data').get('status') == 5):
                            print('[INFO] user already signUp')
                        else:
                            raise Exception('[ERROR] action {0} response failed'.format(p))
                    break
            shoot_data = basic_data('shoot', i, bet_code)
            await send_msg(ws, shoot_data)
            while True:
                reply = await ws.recv()
                if reply == '1':
                    continue
                print('[INFO] action: {0}, response: {1}'.format(p, reply))
                resp = json.loads(reply)
                if resp.get('code') != 0:
                    raise Exception('[ERROR] action {0} response failed'.format(p))
                break
            time.sleep(1)
            # listen addFish push reply msg
            while True:
                reply = await ws.recv()
                if reply == '1':
                    continue
                print('[INFO] action: {0}, response: {1}'.format(p, reply))
                resp = json.loads(reply)
                if resp.get('code') != 0:
                    raise Exception('[ERROR] action {0} response failed'.format(p))
                if resp.get('code') == 0 and resp.get('cmd') == 'gameSettle':
                    print('[INFO] game settle, data: {0}'.format(reply))
                    break
                if resp.get('code') == 304:
                    print('[INFO] fishing ends, msg: {0}'.format(resp.get('msg')))
                    break
                if resp.get('cmd') == 'addFish':
                    fish_id = resp.get('data')[0].get('eid')
                    hit_data = basic_data('hit', i, bet_code)
                    hit_data['params']['eid'] = fish_id
                    await send_msg(ws, hit_data)
                    # while True:
                    #     reply = await ws.recv()
                    #     if reply == '1':
                    #         continue
                    #     print('[INFO] action: {0}, response: {1}'.format(p, reply))
                    #     resp = json.loads(reply)
                    #     if resp.get('cmd') == 'addFish':
                    #         continue
                    #     if resp.get('code') != 0:
                    #         raise Exception('[ERROR] action {0} response failed'.format(p))


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
                "userId": 123456789,
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
                "multiple": bet_count,
                "eid": None
            }
        }
    }
    return data.get(action)


if __name__ == '__main__':
    # 配置文件校验
    if len(WSS_URL.strip()) == 0 or len(JWT_FILE.strip()) == 0:
        print('[ERROR] WSS_URL or JWT_FILE configuration is empty!')
        sys.exit(1)
    asyncio.get_event_loop().run_until_complete(worker())
