# -*- coding: utf-8 -*-
# @Time    : 2021/12/10 20:54
# @Author  : Mr.lian
# @File    : slot_ring.py
# @Software: PyCharm

import json
import jsonpath
import random
from websocket import create_connection

with open(r"D:\slot_ring.txt", mode='r', encoding='utf-8') as f:
    """读取用户数据/当然可以用JWT库生成ps：JWT库高版本不太兼容可以尝试使用1.6.4版本"""
    jwt_list = f.readlines()
    for jwt in jwt_list:
        bet_count = random.choice([0.1, 1, 5, 10])
        # 建立接口连接
        ws = create_connection('wss://fat4-slot-ring.xxx.com/ws')
        res_code = ws.recv()
        # 复盘请求数据
        replay_data = {
            "cmd": "replay",
            "params": {
                "jwt": jwt
            }
        }
        # 红利游戏请求数据
        bonus_data = {
            "cmd": "bonusStart",
            "params": {
                "jwt": jwt
            }
        }
        # 主游戏开始请求数据
        main_data = {
            "cmd": "mainStart",
            "params": {
                "jwt": jwt,
                "bet": bet_count
            }
        }
        # 转换为结构化数据
        new_replay_data = json.dumps(replay_data, ensure_ascii=False)
        new_bonus_data = json.dumps(bonus_data, ensure_ascii=False)
        new_main_data = json.dumps(main_data, ensure_ascii=False)
        # 发送复盘游戏请求
        ws.send(new_replay_data)
        replay_res = json.loads(ws.recv())
        print(replay_res)
        # 提取isBonus节点
        bonus = jsonpath.jsonpath(replay_res, '$.data.mainStart.isBonus')[0]
        # 判断isBonus节点是否为true
        if bonus is True:
            """如果为True进入红利游戏"""
            ws.send(new_bonus_data)
            bonus_res = json.loads(ws.recv())
            try:
                free_number = jsonpath.jsonpath(bonus_res, '$.data.freeNum')[0]
                while True:
                    """循环免费游戏次数直到为0"""
                    if free_number != 0:
                        ws.send(new_bonus_data)
                        free_number -= 1
                    else:
                        break
            except:
                TypeError
        else:
            ws.send(new_main_data)
            main_res = json.loads(ws.recv())
            # 提取isBonus节点
            my_bou = jsonpath.jsonpath(main_res, '$.data.isBonus')[0]
            if my_bou is True:
                """如果为True进入红利游戏"""
                ws.send(new_bonus_data)
                bonus_two_res = json.loads(ws.recv())
                try:
                    free_two_number = jsonpath.jsonpath(bonus_two_res, '$.data.freeNum')[0]
                    while True:
                        """循环免费次数直到为0"""
                        if free_two_number != 0:
                            ws.send(new_bonus_data)
                            free_two_number -= 1
                        else:
                            break
                except:
                    TypeError
        ws.close()
