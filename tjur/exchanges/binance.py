import datetime
import hashlib
import hmac
import json
import logging
import pandas as pd
import requests
import sys
import time
import urllib3

from decimal import Decimal
from requests.exceptions import Timeout
from urllib.parse import urlencode

# Interface to Binance public Rest API


class Binance:

    BASE_URL = 'https://www.binance.com/api/v1'
    BASE_V3_URL = 'https://api.binance.com/api/v3'
    PUBLIC_URL = 'https://www.binance.com/exchange/public/product'
    pd.set_option('display.max_colwidth', -1)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    # Test connectivity to the Rest API and return server time
    def check_connection(self):
        path = '%s/time' % self.BASE_URL
        params = {}
        return self._get(path, params)

    # Current exchange trading rules and symbol info
    def exchange_info(self):
        path = '%s/exchangeInfo' % self.BASE_V3_URL
        params = {}
        return self._get(path, params)

    # Get recent trades (up to last 1000)
    def get_recent_trades(self, symbol, limit):
        """
        Args:
        symbol (str): Symbol pair to operate on i.e LINKETH
        limit (int): Number of trades to get

        Returns:
        list: id, price, quantity, quoteQuantity, time, isBuyerMaker, isBestMatch

        """
        path = '%s/trades' % self.BASE_URL
        params = {'symbol': symbol, 'limit': limit}
        return self._get(path, params)

    # Current average price for a symbol
    def get_cur_avg_price(self, symbol):
        path = '%s/avgPrice' % self.BASE_V3_URL
        params = {'symbol': symbol}
        r = self._get(path, params)
        return Decimal(r['price'])

    # Latest price for a symbol or symbols
    def get_latest_price(self, symbol):
        path = '%s/ticker/price' % self.BASE_V3_URL
        params = {'symbol': symbol}
        return self._get(path, params)

    # Kline/candlestick bars for a symbol, klines are uniquely identified by their open time
    def get_historical_data(self, symbol, candle_interval, limit):
        """
        Args:
        symbol (str): Symbol pair to operate on i.e BTCUSDT
        candle_interval (str): Trading time frame i.e 5m or 4h
        limit (int, optional): Number of ticks to return. Default 500; Max 1000

        Returns:
        pandas.DataFrame: Open time, Open, High, Low, Close, Volume, Close time
        """

        if not candle_interval:
            candle_interval = '4h'
        if not limit or limit > 1000:
            limit = 500

        path = '%s/klines' % self.BASE_URL
        params = {'symbol': symbol,
                  'interval': candle_interval,
                  'limit': limit}
        raw_historical = self._get(path, params)
        df = pd.read_json(json.dumps(raw_historical))
        df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                      'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
                      'Taker buy quote asset volume', 'Ignore']
        df.drop(df.columns[[7, 8, 9, 10, 11]], axis=1, inplace=True)

        df['Open time'] = df['Open time'].apply(
            lambda x: datetime.datetime.fromtimestamp(x / 1e3))
        df['Close time'] = df['Close time'].apply(
            lambda x: datetime.datetime.fromtimestamp(x / 1e3))

        return df

    def get_historical_price(self, symbol, candle_interval, limit):
        """
        Args:
        symbol (str): Symbol pair to operate on i.e BTCUSDT
        candle_interval (str): Trading time frame i.e 5m or 4h
        limit (int, optional): Number of ticks to return. Default 500; Max 1000
        TODO: price_type (int): Type of price (OHLC) i.e 2 as in High or 4 as in Close

        Returns:
        pandas.DataFrame: Price
        """

        historical_price = self.get_historical_data(
            symbol, candle_interval, limit)

        historical_price = historical_price[['Close']]

        return historical_price

    # Get current account information
    def get_account_information(self):
        path = '%s/account?' % self.BASE_V3_URL
        params = {}
        r = self.sign_payload('GET', path, params)
        return r

    # Get balance for selected symbol
    def get_symbol_balance(self, account, symbol):
        """
        Args:
        symbol (str): Symbols balance to fetch

        Returns:
        Decimal
        """

        for assets in account['balances']:
            if assets['asset'] == symbol:
                print('Balance for', symbol, ':', assets['free'])
                logging.info('Balance for ' + symbol + ' : ' + assets['free'])
                return Decimal(assets['free'])

    def get_symbol_min_quantity(self, symbols):
        """
        Args:
        symbols (str): Symbol pair to check min quantity per trade allowed

        Returns:
        Decimal
        """

        exchange_info = self.exchange_info()
        for pairing in exchange_info['symbols']:
            if (pairing['symbol'] == symbols):
                for filter in pairing['filters']:
                    if (filter['filterType'] == 'LOT_SIZE'):
                        return Decimal(filter['minQty'])

    def get_symbol_max_quantity(self, symbols):
        """
        Args:
        symbols (str): Symbol pair to check max quantity per trade allowed

        Returns:
        Decimal
        """

        exchange_info = self.exchange_info()
        for pairing in exchange_info['symbols']:
            if (pairing['symbol'] == symbols):
                for filter in pairing['filters']:
                    if (filter['filterType'] == 'LOT_SIZE'):
                        return Decimal(filter['maxQty'])

    def get_symbol_stepsize(self, symbols):
        """
        Args:
        symbols (str): Symbol pair to check stepsize

        Returns:
        string
        """

        exchange_info = self.exchange_info()
        for pairing in exchange_info['symbols']:
            if (pairing['symbol'] == symbols):
                for filter in pairing['filters']:
                    if (filter['filterType'] == 'LOT_SIZE'):
                        return filter['stepSize']

    def get_open_orders(self, symbol):
        """
        Args:
        symbol (str): Symbol to get orders for

        Returns:
        list
        """

        path = '%s/openOrders?' % self.BASE_V3_URL
        params = {'symbol': symbol}
        return self.sign_payload('GET', path, params)

    # Creates and validates a new order
    def create_new_order(self, symbol, side, order_type, quantity, price):
        """
        Args:
        symbol (str): Symbol pair to operate on i.e LINKETH
        side (str): Order side i.e buy or sell
        order_type (str): Order type i.e MARKET
        quantity (decimal): Position sizing, quantity to trade
        price (str): Price of position
        """

        side = side.upper()
        path = '%s/order?' % self.BASE_V3_URL
        params = {'symbol': symbol,
                  'side': side,
                  'type': order_type,
                  'quantity': quantity,
                  'recvWindow': 4000}
        if (order_type == 'LIMIT'):
            params = params.copy()
            params.update({'price': price,
                           'timeInForce': 'GTC'})

        return self.sign_payload('POST', path, params)

    # Creates and validates a new order but does not send it into the matching engine
    def create_new_order_test(self, symbol, side, order_type, quantity, price):
        """
        Args:
        symbol (str): Symbol pair to operate on i.e LINKETH
        side (str): Order side i.e buy or sell
        order_type (str): Order type i.e MARKET
        quantity (decimal): Position sizing, quantity to trade
        """

        path = '%s/order/test?' % self.BASE_V3_URL
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'timeInForce': 'GTC',
            'recvWindow': 4000}

        r = self.sign_payload('POST', path, params)

    def sign_payload(self, method, path, params):
        query = urlencode(sorted(params.items()))
        query += '&timestamp={}'.format(int(time.time() * 1000))
        signature = hmac.new(self.secret.encode('utf-8'), query.encode('utf-8'),
                             hashlib.sha256).hexdigest()
        query += '&signature={}'.format(signature)

        resp = requests.request(method, path + query,
                                headers={"X-MBX-APIKEY": self.key})
        data = resp.json()
        logging.info(data)
        if 'msg' in data:
            print(data['msg'])
            logging.error(data['msg'])
            if ('Filter failure' in data['msg']):
                print('Exiting')
                sys.exit(0)
        return data

    def _get(self, path, params):
        try:
            url = '%s?%s' % (path, urlencode(params))
            init_request = requests.get(url, timeout=30, verify=False)
            request = init_request.json()
            init_request.close()
            if 'msg' in request:
                print(request['msg'])
                logging.error(request['msg'])
            return request
        except:
            Timeout
        print('Exception', url)
        print('Exiting')
        sys.exit(0)

    def _post(self, path, params):
        url = '%s?%s' % (path, urlencode(params))
        return requests.post(url)
