import json
import sys

import config
import datetime
import logging
import os

from exchanges.binance import Binance
from indicators.ma import MovingAverages
from strategies.maco import Maco

logging.basicConfig(filename='tjur/log/tjur.log', format='%(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

binance = Binance(API_KEY, API_SECRET)
symbol = 'BTCUSDT'

class Tjur:
    print('Tjur started.')
    print('Start time(UTC): ' + str(datetime.datetime.utcnow()))
    print('Trading ' + symbol)
    binance = Binance(API_KEY, API_SECRET)

    def pretty_print(title, message):
        title = str(title).center(os.get_terminal_size().columns, '=')
        pretty_print = title + '\n' + str(message)
        print(pretty_print)
        print('')

    def test_out_maco():

        m = Maco('sma', 'BTCUSDT', '4h', 21, 50)
        golden_cross = m.calculate_golden_cross()

        buy_signal = 0
        risk = 0.25

        if golden_cross and buy_signal == 0:

            buy_signal = 1
            buy_order = float(binance.get_latest_price(symbol)['price'])
            sell_out = buy_order * 1.1
            print('Buying at: ' + str(buy_order)) 
            print(datetime.datetime.utcnow())
            logging.info('Buying at: ' + str(buy_order))

            while (buy_signal == 1):
                latest_price = float(binance.get_latest_price(symbol)['price'])
                death_cross = m.calculate_death_cross()
                if death_cross or latest_price > sell_out:
                    sell_order = latest_price
                    print('Sold at: ' + str(sell_order))
                    print(datetime.datetime.utcnow())
                    logging.info('Sold at: ' + str(sell_order)) 

                    win_loss = float(sell_order) / float(buy_order)
                    print('Win / Lost: ' + str(win_loss))
                    logging.info('Win / Lost: ' + str(win_loss))
                    buy_signal = 0

    try:
        while True:
            test_out_maco()

    except KeyboardInterrupt:
        print(binance.get_latest_price(symbol)['price'])
        print('Exiting')
        logging.warning('Exiting')
        sys.exit()

