import json
import sys

import config

from analysis.metrics import metrics
from exchanges.binance import binance

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

class Botany():
    binance = Binance(API_KEY, API_SECRET)

    print(binance.check_connection())
    print(binance.cur_avg_price('BTCUSDT'))

    print(binance.get_historical_data('Binance', 'BTCUSDT', '4h', '', '',  '1'))
