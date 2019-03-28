from urllib.parse import urlencode

import json
import time
import requests

# Bridge to Binance public Rest API
class Binance:

    BASE_URL = "https://www.binance.com/api/v1"
    BASE_V3_URL = "https://www.api.binance.com/api/v3"
    PUBLIC_URL = "https://www.binance.com/exchange/public/product"

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

    def cur_avg_price(self, symbol):
        path = "%s/avgPrice" % self.BASE_V3_URL
        params = {"symbol": symbol}
        return self._get(path, params)

    # Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.
    def get_historical_data(self, pairing, candle_interval, start_time, end_time, limit):
        
        """
        Args:
        pairing (str): Symbol pair to operate on i.e BTCUSDT
        candle_interval (str): Trading time frame i.e 5m or 4h
        start_time (int, optional): Start timestamp i.e 1553753159999 
        end_time (int, optional): End timestamp i.e 1553753159999
        limit (int, optional): Number of ticks to return. Default 500; Max 1000 
        """
        
        if not candle_interval:
            candle_interval = '4h'
        if not start_time:
            start_time = ""
        if not end_time:
            end_time = ""
        if not limit or limit > 1000:
            limit = 500 

        path = "%s/klines" % self.BASE_URL
        params = {"symbol": symbol,
                  "interval": candle_interval,
                  "startTime": start_time,
                  "endTime": end_time,
                  "limit": limit}
        return self._get(path, params)

    def _get(self, path, params):
        url = "%s?%s" % (path, urlencode(params))
        return requests.get(url, timeout=30, verify=False).json()
