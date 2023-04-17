import datetime
import hashlib
import hmac
import json
import pandas as pd
import requests
import sys
import time
import urllib3

from decimal import Decimal
from urllib.parse import urlencode

# Interface to Binance public Rest API


class Binance():

    BASE_URL = 'https://www.binance.com/api/v1'
    BASE_V3_URL = 'https://api.binance.com/api/v3'
    PUBLIC_URL = 'https://www.binance.com/exchange/public/product'
    pd.set_option('display.max_colwidth', None)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def __init__(self, key, secret, logger):
        self.key = key
        self.secret = secret
        self.logger = logger

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
        list: id, price, quantity, quoteQuantity, time, isBuyerMaker,
              isBestMatch

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
        r = self._get(path, params)
        while r is None:
            r = self._get(path, params)
            if not r is None:
                break
        return r

    # Kline/candles for a symbol, klines are identified by their open time
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
        while df.empty:
            self.logger.warn(f"{path} response empty.")
            time.sleep(5)
            raw_historical = self._get(path, params)
            df = pd.read_json(json.dumps(raw_historical))
            if not df.empty:
                break

        df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
                      'Close time', 'Quote asset volume', 'Number of trades',
                      'Taker buy base asset volume',
                      'Taker buy quote asset volume', 'Ignore']
        df.drop(df.columns[[7, 8, 9, 10, 11]], axis=1, inplace=True)

        df['Open time'] = df['Open time'].apply(
            lambda x: datetime.datetime.fromtimestamp(x / 1e3))
        df['Close time'] = df['Close time'].apply(
            lambda x: datetime.datetime.fromtimestamp(x / 1e3))
        df = df.set_index(pd.to_datetime(df['Open time']))

        return df

    def get_historical_price(self, symbol, candle_interval, limit):
        """
        Args:
        symbol (str): Symbol pair to operate on i.e BTCUSDT
        candle_interval (str): Trading time frame i.e 5m or 4h
        limit (int, optional): Number of ticks to return. Default 500; Max 1000

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
                self.logger.info(
                    f"Balance for {symbol}: {assets['free']}")
                return Decimal(assets['free'])

    def get_symbol_filters(self, symbols):
        """
        Args:
        symbols (str): Symbol pair to gather filter rules

        Returns:
        Decimal
        """

        exchange_info = self.exchange_info()
        for pairing in exchange_info['symbols']:
            if pairing['symbol'] == symbols:
                quote_precision = pairing['quotePrecision']
                for filt in pairing['filters']:
                    if filt['filterType'] == 'LOT_SIZE':
                        min_qty = Decimal(filt['minQty'])
                        max_qty = Decimal(filt['maxQty'])
                        steps = Decimal(filt['stepSize'])
                    if filt['filterType'] == 'PRICE_FILTER':
                        tick_size = abs(Decimal(str(Decimal(filt['tickSize'])
                                        .normalize().as_tuple().exponent)))
        filters = {
            'quote_precision': quote_precision,
            'min_qty': min_qty,
            'max_qty': max_qty,
            'steps': steps,
            'tick_size': tick_size}
        return filters

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

    def get_trade_history(self, symbol, limit):
        """
        Args:
        symbol (str): Symbol to get orders for
        limit (int): Number of orders to get (max 1000)
        """

        path = '%s/myTrades?' % self.BASE_V3_URL
        if not limit:
            limit = 500
        params = {'symbol': symbol,
                  'limit': limit}
        return self.sign_payload('GET', path, params)

    # Creates and validates a new order
    def create_new_order(self, symbol, side, quantity, price):
        """
        Args:
        symbol (str): Symbol pair to operate on i.e LINKETH
        side (str): Order side i.e buy or sell
        quantity (decimal): Position sizing, quantity to trade
        price (str): Price of position
        """

        side = side.upper()
        path = '%s/order?' % self.BASE_V3_URL
        params = {'symbol': symbol,
                  'side': side,
                  'type': 'LIMIT',
                  'quantity': quantity,
                  'recvWindow': 4000,
                  'price': price,
                  'timeInForce': 'GTC'}

        r = self.sign_payload('POST', path, params)
        self.logger.debug(r)
        return r

    # Creates and validates a new order without sending it to market
    def create_new_order_test(self, symbol, side, quantity, price):
        """
        Args:
        symbol (str): Symbol pair to operate on i.e LINKETH
        side (str): Order side i.e buy or sell
        quantity (decimal): Position sizing, quantity to trade
        price (str): Price of position
        """

        path = '%s/order/test?' % self.BASE_V3_URL
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'quantity': quantity,
            'recvWindow': 4000,
            'price': price,
            'timeInForce': 'GTC'}

        return self.sign_payload('POST', path, params)

    def create_new_order_mocked(self, symbol, commission_asset, quantity, price):
        """
        Args:
        symbol (str): Symbol pair to operate on i.e LINKETH
        side (str): Order side i.e buy or sell
        quantity (decimal): Position sizing, quantity to trade
        price (str): Price of position
        """

        return {
            'symbol': symbol,
            'orderId': 1337,
            'origQty': quantity,
            'executedQty': quantity,
            'cummulativeQuoteQty': quantity,
            'fills': [
                {
                    'price': price,
                    'qty': quantity / 2,
                    'commission': '4.00000000',
                    'commissionAsset': commission_asset,
                    'tradeId': 56
                },
                {
                    'price': price - 1,
                    'qty': quantity / 2,
                    'commission': '19.99500000',
                    'commissionAsset': commission_asset,
                    'tradeId': 57
                }
            ]
        }

    def sign_payload(self, method, path, params):
        query = urlencode(sorted(params.items()))
        query += '&timestamp={}'.format(int(time.time() * 1000))
        signature = hmac.new(self.secret.encode('utf-8'),
                             query.encode('utf-8'), hashlib.sha256).hexdigest()
        query += '&signature={}'.format(signature)

        resp = requests.request(method, path + query,
                                headers={"X-MBX-APIKEY": self.key})
        data = resp.json()
        if 'msg' in data:
            self.logger.debug(f"{data['msg']}")
            if 'Filter failure' in data['msg']:
                self.logger.log_print_and_exit('Exiting')
                sys.exit(0)
        return data

    def _get(self, path, params):
        try:
            url = '%s?%s' % (path, urlencode(params))
            init_request = requests.get(url, timeout=30, verify=True)
            request = init_request.json()
            init_request.close()
            if 'msg' in request:
                self.logger.debug(f"{request['msg']}")
            return request
        except requests.exceptions.HTTPError as errh:
            self.logger.error(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            self.logger.error(f"Connection Error: {errc}")
        except requests.exceptions.Timeout as errt:
            self.logger.error(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Error: {err}")
