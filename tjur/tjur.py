import os
import sys
import time

import config
import datetime
import logging

from exchanges.binance import Binance
from strategies.maco import Maco
from strategies.macd import Macd

tjur_path = sys.argv[0]
tjur_dir = os.path.dirname(tjur_path)
logging.basicConfig(filename=tjur_dir + '/log/tjur.log', format='%(asctime)s.%(msecs)06d %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
logging.Formatter.converter = time.gmtime

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

binance = Binance(API_KEY, API_SECRET)

class Tjur:
    with open(tjur_dir +'/assets/start-up.txt', 'r') as f:
        print(f.read())
    print('Start time(UTC): ' + str(datetime.datetime.utcnow()))
    binance = Binance(API_KEY, API_SECRET)

    symbol = input("Select symbol to pair: ").upper()
    print("Available strategies:")
    print("[1] Moving Average Cross Over")
    print("[2] Moving Average Convergence/Divergence (MACD)")
    strategy = int(input("Select strategy: "))

    if (strategy == 1):
        custom = input("Use custom parameters? [y/N] ").lower()
    else:
        custom = 'n'

    if (custom == 'y'):
        time_frame = input('Enter time frame: ').lower()
        short_term = int(input('Select short-term period: '))
        long_term = int(input('Select long-term period: '))
    else:
        time_frame = '5m'
        short_term = 12
        long_term = 26

    check_symbol = str(binance.cur_avg_price(symbol))
    if ('Invalid symbol' in check_symbol):
        print('Invalid symbol')
        print('Exiting')
        sys.exit()
    if (short_term <= 0 or long_term <= 0):
        print(short_term)
        print('Invalid period')
        print('Exiting')
        sys.exit()
    if not (time_frame in {'1m', '3m', '5m', '15m', '30m', '45m',
                           '1h', '2h', '3h', '4h', '1d', '1w', '1mo'}):
        print('Invalid time frame')
        print('Exiting')
        sys.exit()
    if (strategy == 1):
        strategy = Maco('sma', symbol, time_frame, short_term, long_term)
    elif (strategy == 2):
        strategy = Macd(symbol, time_frame)
    else:
        print('Invalid strategy')
        print('Exiting')
        sys.exit()

    print('Trading ' + symbol)

    def calculate_signals(strategy, symbol, time_frame):
        """
        Calculates when to send signal to buy or sell

        Returns:
        1 (int): Signal to buy
        0 (int): Signal to hold
       -1 (int): Signal to sell
        """

        signal = 0
        if (strategy.calculate_buy_signal() and signal == 0):
            buy_order = float(binance.get_latest_price(symbol)['price'])
            take_profit = buy_order * 1.16
            signal = 1
            print('Buying at: ' + str(buy_order))
            print(datetime.datetime.utcnow())
            logging.info('Buying at: ' + str(buy_order))

            while (signal == 1):
                time.sleep(0.01)
                latest_price = float(binance.get_latest_price(symbol)['price'])
                stop_loss = buy_order * 0.84
                sell_signal = strategy.calculate_sell_signal()

                if (sell_signal and stop_loss > latest_price
                        or sell_signal and latest_price > buy_order * 1.08
                        or take_profit < latest_price):
                    sell_order = latest_price
                    print('Sold at: ' + str(sell_order))
                    print(datetime.datetime.utcnow())
                    logging.info('Sold at: ' + str(sell_order))

                    win_loss = float(sell_order) / float(buy_order)
                    print('Win / Lost: ' + str(win_loss))
                    logging.info('Win / Lost: ' + str(win_loss))
                    signal = 0

    try:
        while True:
            calculate_signals(strategy, symbol, time_frame)

    except KeyboardInterrupt:
        print(binance.get_latest_price(symbol)['price'])
        print('Exiting')
        logging.warning('Exiting')
        sys.exit()

