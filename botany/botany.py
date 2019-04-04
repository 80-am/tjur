import json
import sys

import config

from analysis.metrics import Metrics
from exchanges.binance import Binance

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

class Botany():
    binance = Binance(API_KEY, API_SECRET)

    print(binance.check_connection())
    print(binance.cur_avg_price('BTCUSDT'))
    print(binance.get_latest_price('BTCUSDT'))
    print(binance.get_historical_data('BTCUSDT', '4h', 1))
