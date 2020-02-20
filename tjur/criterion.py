import sys
import os

import config

from decimal import Decimal
from strategies.maco import Maco
from strategies.macd import Macd

API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']
tjur_dir = os.path.dirname(sys.argv[0])


class Criterion:
    with open(tjur_dir + '/assets/start-up.txt', 'r') as f:
        print(f.read())

    def __init__(self, exchange, logger):
        self.exchange = exchange
        self.logger = logger

    def define_symbols(self):
        account = self.exchange.get_account_information()
        symbol1 = input('Select first symbol to pair: ').upper()
        balance_symbol1 = self.exchange.get_symbol_balance(account, symbol1)
        if (balance_symbol1):
            symbol2 = input('Select second symbol to pair: ').upper()
            balance_symbol2 = self.exchange.get_symbol_balance(
                account, symbol2)
        else:
            self.logger.log_print_and_exit('No holdings in account for '
                                           + symbol1)
        symbol = symbol1 + symbol2
        filter_rules = self.exchange.get_symbol_filters(symbol)
        symbols = {
            0: {
                'symbol': symbol1,
                'balance': balance_symbol1},
            1: {
                'symbol': symbol2,
                'balance': balance_symbol2},
            'symbol': symbol,
            'filters': filter_rules}
        self.validate_symbol(symbols['symbol'])
        return symbols

    def validate_symbol(self, symbol):
        check_symbol = str(self.exchange.get_cur_avg_price(symbol))
        if ('Invalid symbol' in check_symbol):
            self.logger.log_print_and_exit(symbol + 'is not a valid symbol')

    def select_strategy(self, trade_mode):
        symbol = self.define_symbols()
        if not (trade_mode):
            strategy = {
                'symbol': symbol,
                'strategy': Maco('EMA', symbol['symbol'], '5m', 9, 26,
                                 self.logger)}
            return strategy

        print('\nAvailable strategies:')
        print('[1] Moving Average Cross Over (Default)')
        print('[2] Moving Average Convergence/Divergence (MACD)')

        selected = int(input('Select strategy: ') or 1)
        if (selected == 1):
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
            win_target = Decimal(input('Profit target per trade (%): ')) / 100
            win_target = Decimal(1 + win_target)

        else:
            average = 'sma'
            time_frame = '1h'
            short_term = 9
            long_term = 26
            win_target = Decimal(1.036)

        if (short_term <= 0 or long_term <= 0):
            self.logger.log_print_and_exit('Invalid period')
        self.validate_time_frame(time_frame)
        if (selected == 1):
            selected = Maco(average, symbol['symbol'], time_frame, short_term,
                            long_term, self.logger)
        elif (selected == 2):
            selected = Macd(symbol['symbol'], time_frame, self.logger)
        else:
            self.logger.log_print_and_exit('Invalid strategy')

        position = self.define_sizing(symbol)

        while not (self.is_strategy_ready(selected)):
            pass

        self.logger.log_print('Trading ' + symbol['symbol'])
        strategy = {
            'symbol': symbol,
            'strategy': selected,
            'average': average,
            'time_frame': time_frame,
            'short_term': short_term,
            'long_term': long_term,
            'win_target': win_target,
            'position': position}
        return strategy

    def define_sizing(self, symbols):
        order_type = self.select_order_type()
        print('\nAvailable amount types:')
        print('[1] Fixed amount (Default)')
        print('[2] Percentage of', symbols[1]['symbol'], 'balance')
        amount_type = int(input('Select amount type: ') or 1)
        cur_avg_price = self.exchange.get_cur_avg_price(symbols['symbol'])
        position_size = 10
        position_percentage = Decimal(
            (cur_avg_price * position_size) / symbols[1]['balance']
        ).quantize(Decimal(10) ** -2) * 100
        if (amount_type == 1):
            position_size = Decimal(input('Select position sizing: '))
            position_percentage = Decimal(
                (cur_avg_price * position_size) / symbols[1]['balance']
            ).quantize(Decimal(10) ** -2) * 100
            if (position_percentage > Decimal(100.0)
                    or position_percentage == Decimal(1.00)):
                self.logger.log_print_and_exit('Insufficient funds')
            if (position_percentage < 0.01):
                print(str(position_size), symbols[0]['symbol'],
                      'is less than 0.01% of', symbols[1]['symbol'],
                      'balance at current price')
            else:
                print(str(position_size), symbols[0]['symbol'], 'is about',
                      str(position_percentage) + '% of', symbols[1]['symbol'],
                      'balance at current price')
        else:
            position_percentage = Decimal(
                input('Select position sizing (%): ')) / 100
            position_size = Decimal(
                ((position_percentage * symbols[1]['balance']
                    / cur_avg_price).quantize(Decimal(10) ** -8)))
            print(str(position_percentage * 100) + '% of',
                  symbols[1]['symbol'], 'is about', position_size,
                  symbols[0]['symbol'], 'at current price')

        position = {
            'amount_type': amount_type,
            'size': position_size,
            'percentage': position_percentage,
            'order_type': order_type}
        self.validate_position(symbols, position)
        return position

    def select_order_type(self):
        print('\nAvailable order types:')
        print('[1] Market (Default)')
        print('[2] Limit')
        order_type = input('Select order type: ').upper()
        if (order_type == '2' or order_type == 'LIMIT'):
            return 'LIMIT'
        else:
            return 'MARKET'

    def validate_position(self, symbols, position):
        if (position['percentage'] > 0.05):
            return None
        while (position['percentage'] > 0.05):
            print('Using a position sizing above 5% is not recommended')
            confirm = input('Continue anyway? [y/N] ').upper()
            cur_avg_price = self.exchange.get_cur_avg_price(symbols['symbol'])
            if not (confirm == 'Y'):
                if (position['amount_type'] == 1):
                    position['size'] = Decimal(
                        input('Select position sizing: '))
                    position['percentage'] = ((
                        cur_avg_price * position['size'])
                        / symbols[1]['balance'])
                    position['percentage'] = Decimal(
                        position['percentage']).quantize(Decimal(10) ** -2)
                    print(str(position['size']), 'is about', str(
                        position['percentage']) + '% of', symbols[1]['symbol'],
                        'balance at current price')
                else:
                    position['percentage'] = Decimal(
                        input('Select position sizing (%): ')) / 100
                    if (position['percentage'] <= Decimal(1.0)):
                        position['size'] = Decimal(
                            ((position['percentage'] * symbols[1]['balance'])
                                / cur_avg_price).quantize(Decimal(10) ** -8))
                        print(str(position['percentage'] * 100) + '% of',
                              symbols[1]['symbol'], 'is about',
                              position['size'], symbols[0]['symbol'],
                              'at current price')
                    else:
                        self.logger.log_print_and_exit('Insufficient funds')
            else:
                break

        if (position['amount_type'] == 2):
            cur_avg_price = self.exchange.get_cur_avg_price(symbols['symbol'])
            position['size'] = ((position['percentage']
                                 * symbols[1]['balance']) / cur_avg_price)
            steps = position['filters']['steps'].find('1') - 1
            step_precision = Decimal(10) ** -steps
            if (Decimal(steps) > 1):
                position['size'] = Decimal(position['size']).quantize(
                    step_precision)
            else:
                position['size'] = int(position['size'])

        if (position['size'] < symbols['symbol']['filters']['min_qty']):
            self.logger.log_print_and_exit('Amount' + str(position['size'])
                                           + ' too low')

    def validate_time_frame(self, time_frame):
        if not (time_frame in {'1m', '3m', '5m', '15m', '30m', '45m',
                               '1h', '2h', '3h', '4h', '1d', '1w', '1mo'}):
            self.logger.log_print_and_exit('Invalid time frame')

    def is_strategy_ready(self, strategy):
        ready = False
        start = ''
        while not ready:
            try:
                if (strategy.is_ready()):
                    self.logger.log('Strategy ready')
                    return True
                elif (start == ''):
                    self.logger.log_print('Ongoing upward trend')
                    start = input('Start anyway? [y/N] ').lower()
                    if (start == 'y'):
                        return True
                    else:
                        start = 'n'
                        self.logger.log_print('Waiting for ready signal')
                else:
                    pass
            except KeyboardInterrupt:
                self.logger.log_print_and_exit('Exiting')
