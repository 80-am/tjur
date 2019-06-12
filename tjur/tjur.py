import sys

import config
import datetime
import logging

from exchanges.binance import Binance
from indicators.ma import MovingAverages
from strategies.maco import Maco

logging.basicConfig(filename='tjur/log/tjur.log', format='%(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

binance = Binance(API_KEY, API_SECRET)

class Tjur:
    with open('tjur/assets/start-up.txt', 'r') as f:
        print(f.read())
    print('Start time(UTC): ' + str(datetime.datetime.utcnow()))
    binance = Binance(API_KEY, API_SECRET)

    symbol = input("Select symbol to pair: ").upper()
    time_frame = input('Enter time frame: ').lower()
    short_term = int(input('Select short-term period: '))
    long_term = int(input('Select long-term period: '))

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

    strategy = Maco('sma', symbol, time_frame, short_term, long_term)
    print('Trading ' + symbol)

    def calculate_signals(strategy, symbol):
        """
        Calculates when to send signal to buy or sell

        Returns:
        1 (int): Signal to buy
        0 (int): Signal to hold
       -1 (int): Signal to sell
        """

        golden_cross = strategy.calculate_golden_cross()
        signal = 0
        if (golden_cross and signal == 0):
            buy_order = float(binance.get_latest_price(symbol)['price'])
            take_profit = buy_order * 1.16
            signal = 1
            print('Buying at: ' + str(buy_order))
            print(datetime.datetime.utcnow())
            logging.info('Buying at: ' + str(buy_order))

            while (signal == 1):
                latest_price = float(binance.get_latest_price(symbol)['price'])
                stop_loss = buy_order * 0.84
                death_cross = strategy.calculate_death_cross()

                if (death_cross and stop_loss > latest_price
                        or death_cross and latest_price > buy_order * 1.08
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
            calculate_signals(strategy, symbol)

    except KeyboardInterrupt:
        print(binance.get_latest_price(symbol)['price'])
        print('Exiting')
        logging.warning('Exiting')
        sys.exit()

