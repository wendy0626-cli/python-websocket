#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*- author:yyy -*-

"""
@file: perf_ws.py
@version: 0.0.1
@author: xxx
@time: 2020/9/1 9:48
@software: IntelliJ IDEA
@site:
"""

# 若未安装websockets模块，则使用pip install websockets 或 python -m pip install websockets
import os
import socket
import asyncio
import websockets
from concurrent.futures import ProcessPoolExecutor, as_completed
from config import WORKER_PROCESSES, COROUTINE_POOL_SIZE, WS_URL, MESSAGE, INTERVAL
from config import RESPONSE_TIMEOUT, HEART_BEAT_TIMEOUT

# 若无进程池、协程池配置，则初始化默认值
WORKER_PROCESSES = os.cpu_count() if not WORKER_PROCESSES else WORKER_PROCESSES
COROUTINE_POOL_SIZE = 20 if not COROUTINE_POOL_SIZE else COROUTINE_POOL_SIZE


async def client(process_num, coroutine_num, url, interval, msg):
    """
    websocket客户端实现
    async关键字声明一个协程，await关键字用于挂起可异步执行的阻塞方法
    :param process_num: 进程编号
    :param coroutine_num: 协程编号
    :param url: websocket地址
    :param interval: 心跳数据发送间隔时间，单位s
    :param msg: 消息数据
    :return:
    """
    info = '进程编号: {0}, 协程编号: {1}'.format(process_num, coroutine_num)
    # 外层循环用于控制每次连接失败后的重新连接
    while True:
        try:
            async with websockets.connect(url) as ws:
                # 定义心跳发送次数计数器，重连后重新计数
                n = 0
                while True:
                    try:
                        reply = await asyncio.wait_for(ws.recv(), timeout=RESPONSE_TIMEOUT)
                        msg_recv = '{0}, 收到服务端响应信息: {1}'.format(info, reply)
                        print(msg_recv)
                    except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
                        # 心跳计数器+1
                        n += 1
                        try:
                            pong = await ws.ping()
                            await asyncio.wait_for(pong, timeout=HEART_BEAT_TIMEOUT)
                            print('{0}，第{1}次心跳信号Ping测试，连接正常'.format(info, n))
                            continue
                        except Exception as e:
                            print('{0}, 第{1}次心跳信号Ping测试，连接异常，稍后将重连，本次错误信息：{2}'.format(info, n, e))
                            await asyncio.sleep(interval)
                            break
        except socket.gaierror as e:
            print('{0}，WebSocket启动失败，即将再次尝试，错误信息：{1}'.format(info, e))
            continue
        except ConnectionRefusedError:
            print('{0}，WebSocket启动时发起连接，但被服务端拒绝，即将再次尝试'.format(info))
            continue


async def create_tasks(process_num, url, interval, msg):
    task_list = [asyncio.create_task(client(process_num, i, url, interval, msg)) for i in range(COROUTINE_POOL_SIZE)]
    await asyncio.wait(task_list)


def factory_coroutine(process_num, url, interval, msg):
    """
    协程初始化
    :param process_num:
    :param url:
    :param interval:
    :param msg:
    :return:
    """
    # 协程池，易于理解写法如下
    task_list = []
    loop = asyncio.get_event_loop()
    for i in range(COROUTINE_POOL_SIZE):
        # 创建协程任务
        task = loop.create_task(client(process_num, i, url, interval, msg))
        task_list.append(task)
    loop.run_until_complete(asyncio.wait(task_list))
    # 如下为更好的写法示范，运用列表解析特性，只需一行代码
    # task_list = [asyncio.create_task(client(process_num, i, url, interval, msg)) for i in range(COROUTINE_POOL_SIZE)]


def factory_processes(process_count, url, interval, msg):
    # 进程池管理
    with ProcessPoolExecutor(WORKER_PROCESSES) as prc_executor:
        futures_list = [
            prc_executor.submit(
                factory_coroutine,
                i,
                url,
                interval,
                msg
            ) for i in range(process_count)
        ]
        for fut in as_completed(futures_list):
            print(fut.result())


def main():
    factory_processes(WORKER_PROCESSES, WS_URL, INTERVAL, MESSAGE)


if __name__ == '__main__':
    main()
