import math
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
    else:
        print('No holdings in account for', symbol1, '\nExiting')
        sys.exit(0)

    symbol = symbol1 + symbol2
    check_symbol = str(binance.cur_avg_price(symbol))
    if ('Invalid symbol' in check_symbol):
        print(symbol, 'is not a valid symbol', '\nExiting')
        sys.exit(0)

    print('\nAvailable strategies:')
    print('[1] Moving Average Cross Over (Default)')
    print('[2] Moving Average Convergence/Divergence (MACD)')
    strategy = int(input('Select strategy: ') or 1)

    if (strategy == 1):
        custom = input('Use custom parameters? [y/N] ').lower()
    else:
        custom = 'n'

    if (custom == 'y'):
        print('\nAvailable moving averages:')
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
        win_target = 1 + float(input('Profit target per trade (%): ')) / 100
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

    min_qty = binance.get_symbol_min_quantity(symbol)
    max_qty = binance.get_symbol_max_quantity(symbol)
    steps = binance.get_symbol_stepsize(symbol)
    print('\nSizing rules for', symbol)
    print('Min qty:', min_qty, '\nMax qty:', max_qty, '\nStep size:', steps)
    print('\nAvailable amount types:')
    print('[1] Fixed amount (Default)')
    print('[2] Percentage of symbols balance (Will round to nearest allowed step)')
    amount_type = int(input('Select amount type: ') or 1)
    if (amount_type == 1):
        position_size = float(input('Select position sizing: '))
    else:
        position_size = float(input('Select position sizing (%): ')) / 100

    while (position_size > 0.05 and amount_type == 2):
        print('Using a position sizing above 5% is not recommended.')
        confirm = input('Continue anyway? [y/N] ').upper()
        if not (confirm == 'Y'):
            if (amount_type == 1):
                position_size = float(input('Select position sizing: '))
            else:
                position_size = float(
                    input('Select position sizing (%):')) / 100
        else:
            break

    if (amount_type == 2):
        stepper = 10.0 ** int(abs(math.log10(float(steps))))
        position_size = position_size * balance_symbol2
        position_size = math.trunc(stepper * position_size) / stepper

    print('\nAvailable order types:')
    print('[1] Market (Default)')
    print('[2] Limit')
    order_type = input('Select order type: ').upper()
    if (order_type == '2' or order_type == 'LIMIT'):
        order_type = 'LIMIT'
    else:
        order_type = 'MARKET'

    print('Start time(UTC):', datetime.utcnow())
    print('Trading', symbol)
    logging.info('Starting trading ' + symbol)
    while not ready:
        if (strategy.is_ready()):
            ready = True
            logging.info('Strategy ready')

    def calculate_signals(strategy, symbol, symbol1, symbol2, order_type, position_size, time_frame, win_target):
        """
        Calculates when to send signal to buy or sell.
        """

        signal = 0
        if (strategy.calculate_buy_signal() and signal == 0 and not binance.get_open_orders(symbol)):
            if (order_type == 'LIMIT'):
                price = binance.get_latest_price(symbol)['price']
            else:
                price = None

            buy_order = binance.create_new_order(
                symbol, 'BUY', order_type, position_size, price)
            take_profit = float(buy_order['price']) * win_target
            signal = 1
            print(datetime.utcnow(), 'Buying', position_size,
                  symbol1, 'for', buy_order['price'], symbol2)
            logging.info('OrderId:', buy_order['orderId'], 'Buying',
                         position_size, symbol1, 'for', buy_order['price'], symbol2)

            while (signal == 1):
                latest_price = float(binance.get_latest_price(symbol)['price'])
                stop_loss = float(buy_order['price']) * 0.92
                sell_signal = strategy.calculate_sell_signal()

                if ((stop_loss > latest_price) or (sell_signal and latest_price > float(buy_order['price']))
                        or (sell_signal and latest_price > take_profit)):
                    sell_order = binance.create_new_order(
                        symbol, 'SELL', order_type, position_size, price)
                    print(datetime.utcnow(), 'Selling', position_size,
                          symbol1, 'for', sell_order['price'], symbol2)
                    logging.info('OrderId:', sell_order['orderId'], 'Selling',
                                 position_size, symbol1, 'for', sell_order['price'], symbol2)

                    pl = Performance.calculate_pl(
                        buy_order['price'], sell_order['price'])
                    print(
                        datetime.utcnow(), 'Margin:', str(
                            round(
                                pl, 3)) + '%')
                    logging.info('Margin:' + str(round(pl, 3)) + '%')
                    signal = 0

    try:
        while True:
            calculate_signals(strategy, symbol, symbol1, symbol2,
                              order_type, position_size, time_frame, win_target)

    except KeyboardInterrupt:
        print('Exiting')
        logging.warning('Exiting')
        sys.exit(0)
