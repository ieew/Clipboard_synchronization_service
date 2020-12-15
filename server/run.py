import asyncio
import websockets
import logging as logger
import json

import random
from typing import List


logger.basicConfig(level=logger.INFO,
                   format="[%(asctime)s %(levelname)s]: %(message)s",
                   datefmt="%Y-%m-%d %H:%M:%S")

class errors(Exception):
    pass

Heartbeat: List[websockets.server.WebSocketServerProtocol] = []

token_list = ["alsdufkj"]
Session = [""]


async def token():
    c = 0
    tmp = ""
    while c < 20:
        tmp += random.choice(["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","!","@","#","$","%","^","&","*","(",")","_","+","}","{",":","\"","|","<",">","?","[","]",";","'","\\",",",".","/","'","}"])
        c += 1
        await asyncio.sleep(0)
    return tmp

async def Heartbeats(s: int = 5):
    s = s if s > 3 else 3
    while True:
        for i in Heartbeat:
            try:
                await i.pong()
            except:
                Heartbeat.remove(i)
        await asyncio.sleep(s)


# 检测客户端权限，用户名密码通过才能退出循环
async def check_permit(ws: websockets.server.WebSocketServerProtocol):
    #return True
    while True:
        data = await ws.recv()
        data = json.loads(data)
        if "authkey" in data:
            if data["authkey"] in token_list:
                session = ""
                while session in Session:
                    session = await token()
                    await asyncio.sleep(0)
                await ws.send(json.dumps({"code": 0, "msg": "authkey 正确", "Session": session}))
                Session.append(session)
                ws.Session = session
                Heartbeat.append(ws)
                return session
        else:
            await ws.send(json.dumps({"code": -1, "msg": "参数异常"}))
        await ws.send(json.dumps({"code": 1, "msg": "authkey 错误"}))


# 接收客户端消息并处理，这里只是简单把客户端发来的返回回去
async def recv_msg(ws: websockets.server.WebSocketServerProtocol):
    Clipboard = ""
    while True:
        recv_text = json.loads(await ws.recv())
        logger.debug(f"{recv_text}")
        if not isinstance(recv_text, dict):
            await ws.send("{\"code\": -1, \"msg\": \"参数异常\"}")
            raise errors(f"{recv_text}")
        if "Session" in recv_text:
            if recv_text["Session"] in Session:
                if "data" in recv_text:
                    if Clipboard != recv_text["data"]:
                        for ws2 in Heartbeat:
                            if ws2.Session == recv_text["Session"]:
                                await ws.send("{\"code\": 0, \"msg\": \"一切正常\"}")
                            else:
                                await ws2.send(f"{{\"code\": 0, \"data\": \"{recv_text['data']}\"}}")
            else:
                await ws.send("{\"code\": 2, \"msg\": \"Session 异常\"}")
        else:
            await ws.send("{\"code\": 2, \"msg\": \"Session 异常\"}")

# 服务器端主逻辑
# websocket和path是该函数被回调时自动传过来的，不需要自己传
async def main_logic(conn: websockets.server.WebSocketServerProtocol, path):
    try:
        session = await check_permit(conn)
        if session:
            await recv_msg(conn)
    except websockets.ConnectionClosed as e:
        logger.info(f"一个客户端断开连接:  {e}")
    except json.decoder.JSONDecodeError as e:
        logger.info(e)
        await conn.close(reason="请按 json 格式传数据")
    except errors as e:
        logger.info(e)
        await conn.close(reason="请按 json 格式传数据")
    if session:
        Session.remove(session)

loop = asyncio.get_event_loop()
try:
    logger.info("开始运行(ws://0.0.0.0:8088)~")
    loop.run_until_complete(websockets.serve(main_logic, '0.0.0.0', 8088))
    loop.run_until_complete(Heartbeats())
    loop.run_forever()
except KeyboardInterrupt:
    logger.info("bay~")
except Exception as e:
    logger.error(e)