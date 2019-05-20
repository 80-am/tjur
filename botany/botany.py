import json
import sys

import config
import datetime
import logging
import os

from exchanges.binance import Binance
from indicators.sma import SimpleMovingAverage
from strategies.maco import Maco

logging.basicConfig(filename='botany/log/botany.log', format='%(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

binance = Binance(API_KEY, API_SECRET)
symbol = 'BTCUSDT'

class Botany():
    print('Botany started.')
    print('Start time(UTC): ' + str(datetime.datetime.utcnow()))
    binance = Binance(API_KEY, API_SECRET)
    symbol = 'BTCUSDT'
    ticks = 25

    def pretty_print(title, message):
        title = str(title).center(os.get_terminal_size().columns, '=')
        pretty_print = title + '\n' + str(message)
        print(pretty_print)
        print('')

    def test_out_maco():
        price1 = binance.get_historical_price(symbol, '5m', 50, 'Close')
        price2 = binance.get_historical_price(symbol, '5m', 200, 'Close') 
        short_sma = SimpleMovingAverage.get_sma(price1, 50)
        long_sma = SimpleMovingAverage.get_sma(price2, 200)

        buy_signal = 0
        risk = 0.25
        capital = 4 # Total capital

        if short_sma > long_sma and buy_signal == 0:
            print('Current capital: ' + str(capital))
            logging.info('Current capital: ' + str(capital))

            buy_signal = 1
            buy_price = float(binance.get_latest_price(symbol)['price'])
            buy_order = buy_price * (capital * risk)

            sell_out = buy_order * 1.002
            print('Buying at: ' + str(buy_price) + ' worth: ' + str(buy_order))
            print(datetime.datetime.utcnow())
            logging.info('Buying at: ' + str(buy_price) + ' worth: ' + str(buy_order))

            while (buy_signal == 1):
                latest_price = float(binance.get_latest_price(symbol)['price'])
                if long_sma > short_sma or latest_price > sell_out:
                    sell_price = latest_price
                    sell_order = sell_price * (capital * risk) 
                    print('Sold at: ' + str(sell_price) + ' worth: ' + str(sell_order))
                    print(datetime.datetime.utcnow())
                    logging.info('Sold at: ' + str(sell_price) + ' worth: ' + str(sell_order))

                    win_loss = float(sell_order) / float(buy_order)
                    print('Win / Lost: ' + str(win_loss))
                    logging.info('Win / Lost: ' + str(win_loss))
                    if win_loss > 1:
                        capital = capital + win_loss
                    else:
                        capital = capital - win_loss

                    print('CAPITAL: ' + str(capital))
                    logging.info('CAPITAL: ' + str(capital))
                    print('**************************************')
                    buy_signal = 0

    try:
        while True:
            test_out_maco()

    except KeyboardInterrupt:
        print(binance.get_latest_price(symbol)['price'])
        print('Exiting')
        logging.warning('Exiting')
        sys.exit()

