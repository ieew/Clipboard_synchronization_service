import websockets
import asyncio
import json
import logging as logger


logger.basicConfig(level=logger.INFO,
                             format="[%(asctime)s %(levelname)s]: %(message)s",
                             datefmt="%Y-%m-%d %H:%M:%S")

loop: asyncio.get_event_loop() = None

def Clipboard(v: str = False):
    """剪贴板操作

    不传值就是读取剪贴板，传值就是修改剪贴板为传入的值
    """
    import win32clipboard
    v = v if isinstance(v, (str, int)) else False
    if v:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(str(v))
        win32clipboard.CloseClipboard()
        return True
    else:
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
        except:
            return None
        return data


def get_loop():
    if loop is None:
        raise ValueError("loop 未初始化")
    return loop


class css:
    Clipboard: str
    ws: websockets.server.WebSocketServerProtocol
    Session: str = None
    def __init__(self) -> None:
        pass
    
    async def auth_system(self, ws: websockets.server.WebSocketServerProtocol):
        """鉴权
        """
        while True:
            await ws.send(json.dumps({"authkey": "alsdufkj"}))
            msg = await ws.recv()
            msg = json.loads(msg)
            logger.debug(f"{msg}")
            if msg["code"]:
                logger.critical(msg["msg"])
                await ws.close()
                return False
            self.Session = msg["Session"]
            self.ws = ws
            asyncio.run_coroutine_threadsafe(self.send(), get_loop())
            return True

    async def send(self):
        """剪贴板监听与发送
        """
        self.Clipboard = "" if Clipboard() is None else Clipboard()

        while True:
            data = Clipboard()
            if data != self.Clipboard:
                logger.info(f"发送变动通知: {data}")
                self.Clipboard = Clipboard()
                await self.ws.send(json.dumps({"Session": self.Session, "data": Clipboard()}))
            await asyncio.sleep(0.5)

    async def receive(self, ws: websockets.server.WebSocketServerProtocol):
        """服务器消息接收与处理
        """
        while True:
            data = json.loads(await ws.recv())
            logger.info(Clipboard())
            if "data" in data:
                if data['data'] != self.Clipboard:
                    logger.info(f"收到变动通知: {data['data']}")
                    Clipboard(data["data"])
                    self.Clipboard = data["data"]

    async def nework(self):
        async with websockets.connect('ws://127.0.0.1:8088') as websocket:
            if await self.auth_system(websocket):
                await self.receive(websocket)

    def run(self):
        get_loop().run_until_complete(self.nework())
        get_loop().run_forever()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = css()
    app.run()
    #print(Clipboard())