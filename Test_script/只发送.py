import multiprocessing as mul

import asyncio
import websockets
try:
    import ujson as json
except ModuleNotFoundError:
    import json
import time, logging as logger


logger.basicConfig(level=logger.INFO,
                             format="[%(asctime)s %(levelname)s]: %(message)s",
                             datefmt="%Y-%m-%d %H:%M:%S")


Session: str = None
loop: asyncio.get_event_loop() = None

# 连接保活
async def pone(ws: websockets.server.WebSocketServerProtocol, s: int = 5):
    """连接保活心跳协程
    """
    pmsg = json.dumps({"Session": Session})
    while True:
        await ws.pong(pmsg)
        await asyncio.sleep(s)


# 向服务器端认证，用户名密码通过才能退出循环
async def auth_system(ws: websockets.server.WebSocketServerProtocol):
    while True:
        await ws.send(json.dumps({"authkey": "alsdufkj"}))
        msg = await ws.recv()
        msg = json.loads(msg)
        logger.debug(f"{msg}")
        if msg["code"]:
            logger.critical(msg["msg"])
            await ws.close()
            return False
        global Session
        Session = msg["Session"]
        asyncio.run_coroutine_threadsafe(pone(ws), loop)
        return True

# 向服务器端发送认证后的消息
async def send_msg(ws: websockets.server.WebSocketServerProtocol):
    while True:
        recv_text = input(":")
        if len(recv_text):
            await ws.send(json.dumps({"Session": Session, "data": recv_text}))
            print(await ws.recv())

# 客户端主逻辑
async def main_logic():
    async with websockets.connect('ws://127.0.0.1:8088') as websocket:
        if await auth_system(websocket):
            await send_msg(websocket)

def main():
    try:
        global loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_logic())
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()