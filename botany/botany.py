import json
import sys

import config
import os

from analysis.metrics import Metrics
from exchanges.binance import Binance
from indicators.sma import SimpleMovingAverage

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

class Botany():
    binance = Binance(API_KEY, API_SECRET)
    ticks = 25;
    price = binance.get_historical_price('BTCUSDT', '5m', ticks, 0) 

    #TODO: Make it pretty
    def pretty_print(message):
        return message.center(os.get_terminal_size().columns)

    print(binance.check_connection())
    print(binance.get_historical_data('BTCUSDT', '5m', 1))
    print(pretty_print('SMA(' + str(ticks) + ')'))
    print(SimpleMovingAverage.get_sma(price, ticks))
    print(binance.get_latest_price('BTCUSDT'))
    print(binance.cur_avg_price('BTCUSDT'))

