import asyncio
import json
import pandas as pd
import requests
import websockets


class Socket:
    def __init__(self, logger, symbol, stream):
        self.logger = logger
        self.symbol = symbol.upper()
        self.stream = symbol.lower() + stream
        self.uri = 'wss://stream.binance.com:9443/ws/' + self.stream
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.__async__connect())
        self.ticker = pd.DataFrame()
        self.book = {}
        self.updates = 0
        self.sub_ready = False
        self.stream_ready = False
        if (stream == '@depth@100ms'):
            self.id = 'depthUpdate'
        if (stream == '@ticker'):
            self.id = '24hrTicker'

    def get_ticker(self):
        data = self.on_msg()
        if (data is None):
            if not (self.ws.open):
                self.loop.run_until_complete(self.__async__connect())
            return self.ticker
        else:
            data = json.loads(data)
        self.ticker = self.ticker.append(data, ignore_index=True)
        if (len(self.ticker.index) > 2):
            self.ticker.drop(self.ticker.index[:1], inplace=True)
        return self.ticker

    def get_book(self):
        data = self.on_msg()
        if (data is None):
            self.logger.log('No data in book')
            self.restart_socket()
            return self.book
        else:
            data = json.loads(data)

        if (data.get('U') is None):
            return self.book
        else:
            self.last_u = data.get('U')

        if (len(self.book) == 0):
            self.logger.log('Getting snapshot')
            self.book = self.get_snapshot()
            return self.book

        # if (self.book.get('bids') is None):
        if not (self.book.get('bids')):
            self.logger.log('Bids or asks empty')
            self.restart_socket()

        lastUpdateId = self.book.get('lastUpdateId')

        if (self.updates == 0):
            if ((data.get('U') <= lastUpdateId + 1)
                    and (data.get('u') >= lastUpdateId + 1)):
                self.book['lastUpdateId'] = data['u']
                self.process_updates(data)
        elif data.get('U') == lastUpdateId + 1:
            self.book['lastUpdateId'] = data['u']
            self.process_updates(data)
        return self.book

    def process_updates(self, data):
        for update in data['b']:
            self.manage_book('bids', update)
        for update in data['a']:
            self.manage_book('asks', update)

    def manage_book(self, side, update):
        price, qty = update

        for x in range(0, len(self.book[side])):
            if (price == self.book[side][x][0]):
                if (float(qty) == 0.00000000):
                    del self.book[side][x]
                    break
                else:
                    self.book[side][x] = update
                    break
            elif (price > self.book[side][x][0]):
                if (float(qty) != 0.00000000):
                    self.book[side].insert(x, update)
                    break
                else:
                    break

    def get_snapshot(self):
        url = requests.get('https://www.binance.com/api/v1/depth?symbol='
                           + self.symbol + '&limit=50')
        self.updates = 0
        return json.loads(url.content.decode())

    def on_msg(self):
        try:
            return self.loop.run_until_complete(self.__async__on_msg())
        except Exception as e:
            self.logger.log('Exception in on_msg')
            self.logger.log(e)
            self.restart_socket()

    async def __async__connect(self):
        try:
            self.ws = await websockets.client.connect(self.uri,
                                                      ping_interval=None,
                                                      ping_timeout=None)
        except Exception as e:
            self.logger.log('Exception in connect')
            self.logger.log(e)

    async def __async__reconnect(self):
        try:
            self.ws = await websockets.client.connect(self.uri,
                                                      ping_interval=None,
                                                      ping_timeout=None)
            await self.ws.pong()
        except Exception as e:
            self.logger.log('Exception in async reconnect')
            self.logger.log(e)
        await self.subscribe()

    async def subscribe(self):
        sub = {
            "method": "SUBSCRIBE",
            "params": [
                self.stream
            ],
            "id": 1
        }
        await self.ws.send(json.dumps(sub))
        self.logger.log('Subscribing to ' + self.stream)

    async def unsubscribe(self):
        sub = {
            "method": "UNSUBSCRIBE",
            "params": [
                self.stream
            ],
            "id": 312
        }
        await self.ws.send(json.dumps(sub))
        self.logger.log('Unsubscribing to ' + self.stream)

    async def list_subscriptions(self):
        list_subs = {
            "method": "LIST_SUBSCRIPTIONS",
            "id": 3
        }
        await self.ws.send(json.dumps(list_subs))

    def restart_socket(self):
        self.logger.log('Restarting socket')
        try:
            self.loop.run_until_complete(self.__async__reconnect())
        except Exception as e:
            self.logger.log('Exception in reconnect')
            self.logger.log(e)
        self.book = self.get_snapshot()
        self.updates = 0

    async def close_socket(self):
        try:
            await self.ws.close()
        except Exception as e:
            self.logger.log(e)

    async def __async__on_msg(self):
        return await self.ws.recv()
