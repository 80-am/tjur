import json
import sys

import config
import pairings

from exchanges.Binance import Binance


API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

class Botany():
    binance = Binance(API_KEY, API_SECRET)

    print(binance.check_connection())
    print(binance.cur_avg_price(pairings.CRYPTO['ethereum/bitcoin']))

    print(binance.candle(pairings.CRYPTO['ethereum/bitcoin'], '4h', '1'))
