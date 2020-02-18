import asyncio
import json
import pandas as pd

from websockets import connect


class SocketHandler:
    def __init__(self, stream):
        self.stream = stream

    async def __aenter__(self):
        self._conn = connect('wss://stream.binance.com:9443/ws/' + self.stream)
        self.websocket = await self._conn.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()


class Socket:
    def __init__(self, symbol):
        self.wws = SocketHandler(symbol.lower() + '@ticker')
        self.loop = asyncio.get_event_loop()
        self.df = pd.DataFrame(columns=['e', 'E', 's', 'p', 'P', 'w', 'x', 'c',
                                        'Q', 'b', 'B', 'a', 'A', 'o', 'h', 'l',
                                        'v', 'q', 'O', 'C', 'F', 'L', 'n'])

    def get_rolling(self):
        response = json.loads(self.loop.run_until_complete(
            self.__async__get_rolling()))
        self.df = self.df.append(response, ignore_index=True)

        if (len(self.df.index) > 2):
            self.df = self.df.iloc[1:]
        return self.df

    async def __async__get_rolling(self):
        async with self.wws as echo:
            return await echo.receive()
