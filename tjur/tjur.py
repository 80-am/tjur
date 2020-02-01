import os
import sys
import time

import config
import logging

from datetime import datetime
from analysis.performance import Performance
from exchanges.binance import Binance
from strategies.maco import Maco
from strategies.macd import Macd

tjur_path = sys.argv[0]
tjur_dir = os.path.dirname(tjur_path)
logging.basicConfig(
    filename=tjur_dir + '/log/tjur-' + str(
        datetime.timestamp(
            datetime.utcnow())) + '.log',
    format='%(asctime)s.%(msecs)06d %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)
logging.Formatter.converter = time.gmtime

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

binance = Binance(API_KEY, API_SECRET)


class Tjur:
    with open(tjur_dir + '/assets/start-up.txt', 'r') as f:
        print(f.read())
    ready = False
    account = binance.get_account_information()
    symbol1 = input('Select first symbol to pair: ').upper()
    balance_symbol1 = binance.get_symbol_balance(account, symbol1)
    if (balance_symbol1):
        symbol2 = input('Select second symbol to pair: ').upper()
        balance_symbol2 = binance.get_symbol_balance(account, symbol2)
        if not (balance_symbol2):
            print('No holdings in account for', symbol2, '\nExiting')
            sys.exit(0)
    else:
        print('No holdings in account for', symbol1, '\nExiting')
        sys.exit(0)

    symbol = symbol1 + symbol2
    check_symbol = str(binance.cur_avg_price(symbol))
    if ('Invalid symbol' in check_symbol):
        print(symbol, 'is not a valid symbol', '\nExiting')
        sys.exit(0)

    print('Available strategies:')
    print('[1] Moving Average Cross Over')
    print('[2] Moving Average Convergence/Divergence (MACD)')
    strategy = int(input('Select strategy: ') or 1)

    if (strategy == 1):
        custom = input('Use custom parameters? [y/N] ').lower()
    else:
        custom = 'n'

    if (custom == 'y'):
        print('Available moving averages:')
        print('[1] Simple Moving Average (SMA)')
        print('[2] Exponential Moving Average (EMA)')
        average = int(input('Select average: '))
        if (average == 1):
            average = 'sma'
        elif (average == 2):
            average = 'ema'
        else:
            average = int(input('Select average: '))

        time_frame = input('Enter time frame: ').lower()
        short_term = int(input('Select short-term period: '))
        long_term = int(input('Select long-term period: '))
        win_target = float(input('Profit target per trade (%): '))
    else:
        average = 'sma'
        time_frame = '1h'
        short_term = 9
        long_term = 26
        win_target = 1.036

    if (short_term <= 0 or long_term <= 0):
        print(short_term)
        print('Invalid period', '\nExiting')
        sys.exit(0)
    if not (time_frame in {'1m', '3m', '5m', '15m', '30m', '45m',
                           '1h', '2h', '3h', '4h', '1d', '1w', '1mo'}):
        print('Invalid time frame', '\nExiting')
        sys.exit(0)
    if (strategy == 1):
        strategy = Maco(average, symbol, time_frame, short_term, long_term)
    elif (strategy == 2):
        strategy = Macd(symbol, time_frame)
    else:
        print('Invalid strategy', '\nExiting')
        sys.exit(0)

    print('Start time(UTC):', datetime.utcnow())
    print('Trading', symbol)
    logging.info('Starting trading ' + symbol)
    while not ready:
        if (strategy.is_ready()):
            ready = True
            logging.info('Strategy ready')

    def calculate_signals(strategy, symbol, time_frame, win_target):
        """
        Calculates when to send signal to buy or sell.
        """

        signal = 0
        if (strategy.calculate_buy_signal() and signal == 0):
            buy_order = float(binance.get_latest_price(symbol)['price'])
            take_profit = buy_order * win_target
            signal = 1
            print(datetime.utcnow(), 'Buying at:', str(buy_order))
            logging.info('Buying at: ' + str(buy_order))

            while (signal == 1):
                latest_price = float(binance.get_latest_price(symbol)['price'])
                stop_loss = buy_order * 0.84
                sell_signal = strategy.calculate_sell_signal()

                if ((sell_signal and stop_loss > latest_price)
                        or (sell_signal and latest_price > take_profit)):
                    sell_order = latest_price
                    print(datetime.utcnow(), 'Sold at:', str(sell_order))
                    logging.info('Sold at: ' + str(sell_order))
                    pl = Performance.calculate_pl(buy_order, sell_order)
                    print(
                        datetime.utcnow(), 'Margin:', str(
                            round(
                                pl, 3)) + '%')
                    logging.info('Margin:' + str(round(pl, 3)) + '%')
                    signal = 0

    try:
        while True:
            calculate_signals(strategy, symbol, time_frame, win_target)

    except KeyboardInterrupt:
        print('Exiting')
        logging.warning('Exiting')
        sys.exit(0)
