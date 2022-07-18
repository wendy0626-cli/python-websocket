#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*- author:yyy -*-

"""
@file: config.py
@version: 0.0.1
@author: xxx
@time: 2020/9/1 9:58
@software: IntelliJ IDEA
@site:
"""

# 进程池大小，若未给出(None)，则默认与CPU核数保持一致
WORKER_PROCESSES = 6
# 每个进程内协程启动数量，若未给出（None），认20
COROUTINE_POOL_SIZE = 600

# 目标ws地址
WS_URL = 'ws://localhost:8765'

# 发送消息报文
MESSAGE = 'ping'
# 链接断开后，发起重连前等待时间（单位秒）
INTERVAL = 2

# 接收响应超时时间（单位秒）
RESPONSE_TIMEOUT = 30
# 心跳发送超时时间（单位秒）
HEART_BEAT_TIMEOUT = 10
