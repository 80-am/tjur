import math
import os
import sys
import time

import config
import logging

from datetime import datetime
from decimal import Decimal
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
    check_symbol = str(binance.get_cur_avg_price(symbol))
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
        win_target = 1 + Decimal(input('Profit target per trade (%): ')) / 100
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
    print('[2] Percentage of', symbol2, 'balance')
    amount_type = int(input('Select amount type: ') or 1)
    cur_avg_price = binance.get_cur_avg_price(symbol)
    if (amount_type == 1):
        position_size = Decimal(input('Select position sizing: '))
        position_percentage = Decimal(
            (cur_avg_price * position_size) / balance_symbol2).quantize(Decimal(10) ** -2) * 100
        if (position_percentage > Decimal(100.0) or position_percentage == Decimal(1.00)):
            print('Insufficient funds\nExiting')
            sys.exit(0)
        if (position_percentage < 0.01):
            print(str(position_size), symbol1, 'is less than 0.01% of',
                  symbol2, 'balance at current price')
        else:
            print(str(position_size), symbol1, 'is about', str(
                position_percentage) + '% of', symbol2, 'balance at current price')
    else:
        position_percentage = Decimal(
            input('Select position sizing (%): ')) / 100
        position_size = Decimal(
            ((position_percentage * balance_symbol2) / cur_avg_price).quantize(Decimal(10) ** -8))
        print(str(position_percentage * 100) + '% of', symbol2, 'is about',
              position_size, symbol1, 'at current price')

    while (position_percentage > 0.05):
        print('Using a position sizing above 5% is not recommended')
        confirm = input('Continue anyway? [y/N] ').upper()
        if not (confirm == 'Y'):
            if (amount_type == 1):
                position_size = Decimal(input('Select position sizing: '))
                position_percentage = (
                    cur_avg_price * position_size) / balance_symbol2
                position_percentage = Decimal(
                    position_percentage).quantize(Decimal(10) ** -2)
                print(str(position_size), 'is about', str(
                    position_percentage) + '% of', symbol2, 'balance at current price')
            else:
                position_percentage = Decimal(
                    input('Select position sizing (%): ')) / 100
                if (position_percentage <= Decimal(1.0)):
                    position_size = Decimal(
                        ((position_percentage * balance_symbol2) / cur_avg_price).quantize(Decimal(10) ** -8))
                    print(str(position_percentage * 100) + '% of', symbol2, 'is about',
                          position_size, symbol1, 'at current price')
                else:
                    print('Insufficient funds\nExiting')
                    sys.exit(0)
        else:
            break

    if (amount_type == 2):
        cur_avg_price = binance.get_cur_avg_price(symbol)
        position_size = (position_percentage * balance_symbol2) / cur_avg_price
        steps = steps.find('1') - 1
        step_precision = Decimal(10) ** -steps
        if (Decimal(steps) > 1):
            position_size = Decimal(position_size).quantize(step_precision)
        else:
            position_size = int(position_size)

    if (position_size < min_qty):
        print('Amount', str(position_size), 'too low\nExiting')
        sys.exit(0)

    print('\nAvailable order types:')
    print('[1] Market (Default)')
    print('[2] Limit')
    order_type = input('Select order type: ').upper()
    if (order_type == '2' or order_type == 'LIMIT'):
        order_type = 'LIMIT'
    else:
        order_type = 'MARKET'

    print('\nStart time(UTC):', datetime.utcnow())
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
            buy_price = Decimal(buy_order['fills'][0]['price'])
            take_profit = buy_price * win_target
            signal = 1
            print(datetime.utcnow(), 'Buying', position_size,
                  symbol1, 'for', '{:.8f}'.format(buy_price), symbol2)
            logging.info('OrderId: ' + str(buy_order['orderId']) + ' Buying ' +
                         str(position_size) + symbol1 + ' for' + '{:.8f}'.format(buy_price) + symbol2)

            while (signal == 1):
                latest_price = Decimal(
                    binance.get_latest_price(symbol)['price'])
                stop_percentage = Decimal(0.92)
                stop_loss = buy_price * stop_percentage
                sell_signal = strategy.calculate_sell_signal()

                if ((stop_loss > latest_price) or (sell_signal and latest_price > take_profit)):
                    if (amount_type == 2):
                        position_sell = Decimal(
                            position_percentage * balance_symbol1).quantize(Decimal(10) ** -8)
                    else:
                        position_sell = position_size
                    sell_order = binance.create_new_order(
                        symbol, 'SELL', order_type, position_sell, price)
                    sell_price = Decimal(sell_order['fills'][0]['price'])
                    print(datetime.utcnow(), 'Selling', position_sell,
                          symbol1, 'for', '{:.8f}'.format(sell_price), symbol2)
                    logging.info('OrderId: ' + str(sell_order['orderId']) + ' Selling ' +
                                 str(position_sell) + symbol1 + ' for ' + '{:.8f}'.format(sell_price) + symbol2)

                    pl = Performance.calculate_pl(buy_price, sell_price)
                    print(
                        datetime.utcnow(), 'Margin:', str(
                            round(
                                pl, 3)) + '%')
                    logging.info('Margin:' + str(round(pl, 3)) + '%\n')
                    signal = 0

    try:
        while True:
            calculate_signals(strategy, symbol, symbol1, symbol2,
                              order_type, position_size, time_frame, win_target)

    except KeyboardInterrupt:
        print('Exiting')
        logging.warning('Exiting')
        sys.exit(0)
