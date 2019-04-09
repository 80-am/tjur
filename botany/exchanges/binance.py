from urllib.parse import urlencode

import datetime
import json
import pandas as pd
import requests
import time
import urllib3

# Bridge to Binance public Rest API
class Binance:

    BASE_URL = "https://www.binance.com/api/v1"
    BASE_V3_URL = "https://www.api.binance.com/api/v3"
    PUBLIC_URL = "https://www.binance.com/exchange/public/product"
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    # Test connectivity to the Rest API and return server time.
    def check_connection(self):
        path = "%s/time" % self.BASE_URL
        params = {}
        return self._get(path, params)

    # Current exchange trading rules and symbol info.
    def exchange_info(self):
        path = "%s/exchangeInfo" % self.BASE_URL
        params = {}
        return self._get(path, params)

    # Current average price for a symbol.
    def cur_avg_price(self, symbol):
        path = "%s/avgPrice" % self.BASE_V3_URL
        params = {"symbol": symbol}
        return self._get(path, params)

    # Latest price for a symbol or symbols.
    def get_latest_price(self, symbol):
        path = "%s/ticker/price" % self.BASE_V3_URL
        params = {"symbol": symbol}
        return self._get(path, params)

    # Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.
    def get_historical_data(self, pairing, candle_interval, limit):

        """
        Args:
        pairing (str): Symbol pair to operate on i.e BTCUSDT
        candle_interval (str): Trading time frame i.e 5m or 4h
        limit (int, optional): Number of ticks to return. Default 500; Max 1000 

        Returns:
        pandas.DataFrame: Open time, Open, High, Low, Close, Volume, Close time 
        """

        if not candle_interval:
            candle_interval = '4h'
        if not limit or limit > 1000:
            limit = 500 

        path = "%s/klines" % self.BASE_URL
        params = {"symbol": pairing,
                  "interval": candle_interval,
                  "limit": limit}
        raw_historical = self._get(path, params)
        df = pd.read_json(json.dumps(raw_historical))
        df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                      'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
                      'Taker buy quote asset volume', 'Ignore']
        df.drop(df.columns[[7, 8, 9, 10, 11]], axis=1, inplace=True)

        df['Open time'] = df['Open time'].apply(lambda x: datetime.datetime.fromtimestamp(x / 1e3))
        df['Close time'] = df['Close time'].apply(lambda x: datetime.datetime.fromtimestamp(x / 1e3))

        return df

    def get_historical_price(self, pairing, candle_interval, limit, price_type):

        """
        Args:
        pairing (str): Symbol pair to operate on i.e BTCUSDT
        candle_interval (str): Trading time frame i.e 5m or 4h
        limit (int, optional): Number of ticks to return. Default 500; Max 1000 
        price_type (int): Type of price (OHLC) i.e 2 as in High or 4 as in Close

        Returns:
        TBD
        """

        historical_price = self.get_historical_data(pairing, candle_interval, limit);

        #if price_type < 4 or price_type < 0:
        #    return "ERROR"

        historical_price = historical_price[[price_type]]
        
        #historical_price.drop(historical_price.columns[[0, 2, 3, 4, 5, 6]], axis=1, inplace=True)

        return historical_price

    def _get(self, path, params):
        url = "%s?%s" % (path, urlencode(params))
        return requests.get(url, timeout=30, verify=False).json()
 
