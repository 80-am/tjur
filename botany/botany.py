import json
import sys

import config
import os

from exchanges.binance import Binance
from indicators.sma import SimpleMovingAverage

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

class Botany():
    binance = Binance(API_KEY, API_SECRET)
    ticks = 25;
    price1 = binance.get_historical_price('BTCUSDT', '5m', 25, 'Close') 
    price2 = binance.get_historical_price('BTCUSDT', '5m', 25, 'Open') 

    def pretty_print(message):
        message = str(message).center(os.get_terminal_size().columns, '=')
        return message

    print(binance.get_historical_data('BTCUSDT', '5m', 1))
    print(pretty_print(' SMA(' + str(ticks) + ') '))
    print(SimpleMovingAverage.get_sma(price1, ticks))
    print(SimpleMovingAverage.get_sma(price2, ticks))
    print(binance.get_latest_price('BTCUSDT'))
    print(binance.cur_avg_price('BTCUSDT'))
