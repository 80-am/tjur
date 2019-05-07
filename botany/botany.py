import json
import sys

import config
import os

from exchanges.binance import Binance
from indicators.sma import SimpleMovingAverage
from strategies.maco import Maco

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

class Botany():
    binance = Binance(API_KEY, API_SECRET)
    symbol = 'BTCUSDT'
    ticks = 25;
    price1 = binance.get_historical_price(symbol, '5m', 25, 'Close') 
    price2 = binance.get_historical_price(symbol, '5m', 50, 'Close') 

    maco = Maco(symbol, '4h', price1, price2, 'Close') 

    def pretty_print(title, message):
        title = str(title).center(os.get_terminal_size().columns, '=')
        pretty_print = title + '\n' + str(message)
        print(pretty_print)
        print('')

    pretty_print(' SMA(' + str(ticks) + ') ', SimpleMovingAverage.get_sma(price1, ticks))
    pretty_print(' SMA(' + str(50) + ') ', SimpleMovingAverage.get_sma(price2, 50))
    #pretty_print(' Latest Price for ' + symbol + ' ', binance.get_latest_price(symbol))
    #pretty_print(' Current Price for ' + symbol + ' ', binance.cur_avg_price(symbol))
    print(maco.calculate_signals())
