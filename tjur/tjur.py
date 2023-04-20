#!/usr/bin/env python3
import datetime
import sys
import os
import yaml

from analysis.performance import Performance
from analysis.ta import Ta
from argument_parser import Parser
from criteria.criteria import Criteria
from decimal import Decimal
from exchanges.binance import Binance
from log.logger import Logger


class Tjur():

    def __init__(self, logger, config, criteria, exchange):
        self.logger = logger
        self.config = config
        self.live_trading = config['live_trading']
        self.criteria = criteria
        self.exchange = exchange
        self.symbols = criteria['symbol']['symbol']
        self.symbol1 = criteria['symbol'][0]['symbol']
        self.symbol2 = criteria['symbol'][1]['symbol']
        self.steps = criteria['symbol']['filters']['steps']
        self.position = criteria['position']
        self.position_size = criteria['position']['size']
        self.position_percentage = criteria['position']['percentage']

    def trade(self):
        """
        Running calculations
        """
        k = 0
        ta = Ta(self.logger, self.config, self.symbols, self.exchange)
        self.logger.write_to_screen(0, 0, 'Trading ' + self.symbols)
        self.logger.write_to_screen(1, 0, '🔎 Looking for entry position')
        while k != ord('q'):
            if (ta.matches_entry_criteria() and not binance.get_open_orders(self.symbols)):
                self.position_size = self.get_position_size('BUY')
                price = self.get_position_price()
                buy_order = self.buy(self.position_size, price)
                signal = buy_order['signal']
                self.logger.info('Calculating sell signal.')
                self.logger.write_to_screen(1, 0, '🚀 Calculating sell signal.')
                self.logger.clear_lines(4, 8)
                self.logger.write_to_screen(4, 0, f'🛒 Purchase price: {price}')
                now = str(datetime.datetime.now(datetime.timezone.utc)).split('.')[0]
                self.logger.write_to_screen(5, 0, f'⏱️ Purchase time: {now}')

                while signal == 1:
                    latest_price = Decimal(
                        binance.get_latest_price(self.symbols)['price']
                        or buy_order['price'])
                    sell_signal = ta.matches_exit_criteria(buy_order['price'])

                    if (sell_signal):
                        self.position_size = self.get_position_size('SELL')
                        price = self.get_position_price()
                        sell_order = self.sell(self.position_size, price)
                        pl = Performance.calculate_pl(
                            buy_order['price'], sell_order['price'])
                        self.logger.info(
                            f"Sold @ {sell_order['price']} with a margin of {round(pl, 3)}%")
                        acc = self.exchange.get_account_information()
                        self.exchange.get_symbol_balance(
                            acc, self.symbol2)

    def get_position_size(self, side):
        steps = str(self.steps).find('1') - 1
        step_precision = Decimal(10) ** -steps
        account = self.exchange.get_account_information()
        if side == 'BUY':
            balance_symbol2 = self.exchange.get_symbol_balance(
                account, self.symbol2)
            cur_avg_price = self.exchange.get_cur_avg_price(self.symbols)
            position = Decimal((self.position_percentage * balance_symbol2) / cur_avg_price
                               ).quantize(Decimal(10) ** -steps)
        elif side == 'SELL':
            position = self.position_size
        if Decimal(steps) > 1:
            return Decimal(position).quantize(step_precision)
        return int(position)

    # TODO: Create price logic when using LIMIT, for now uses latest price.
    def get_position_price(self):
        return self.exchange.get_latest_price(self.symbols)['price']

    def buy(self, position_size, price):
        if self.live_trading:
            buy_order = self.exchange.create_new_order(
                self.symbols, 'BUY', str(position_size), price)
        else:
            position_size = 1
            buy_order = self.exchange.create_new_order_mocked(
                self.symbols, self.symbol2, str(position_size), price)
        buy_price = Decimal(buy_order['fills'][0]['price'])
        self.logger.info(
            f"OrderId: {buy_order['orderId']} Buying {position_size} {self.symbol1} @ {buy_price:.8f}")
        order = {
            'price': buy_price,
            'signal': 1}
        return order

    def sell(self, position_size, price):
        if self.live_trading:
            sell_order = self.exchange.create_new_order(
                self.symbols, 'SELL', str(position_size), price)
        else:
            sell_order = self.exchange.create_new_order_mocked(
                self.symbols, self.symbol2, quantity, price)
        sell_price = Decimal(sell_order['fills'][0]['price'])
        self.logger.info(
            f"OrderId: {sell_order['orderId']} Selling {position_size} {self.symbol1} @ {sell_price:.8f}")
        order = {
            'price': sell_price,
            'signal': 0}
        return order

    def run(self):
        try:
            while True:
                self.trade()

        except KeyboardInterrupt:
            self.logger.log_print_and_exit('Exiting')


if __name__ == '__main__':
    path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(path, "config.yaml"), "r") as c:
        config = yaml.load(c, Loader=yaml.FullLoader)
        API_KEY = config['binance']['api_key']
        API_SECRET = config['binance']['api_secret']
        LIVE_TRADING = config['live_trading']
        if LIVE_TRADING:
            confirm = input('Starting live trading. Continue? [y/N] ').upper()
            if not confirm == 'Y':
                print('Exiting')
                sys.exit(0)

    parser = Parser()
    args = parser.parse()
    if args.help:
        parser.print_help()
        sys.exit(0)
    if args.version:
        print(parser.get_version())

    logger = Logger(config)
    binance = Binance(API_KEY, API_SECRET, logger)
    criteria = Criteria(logger, config, binance)
    Tjur(logger, config, criteria.define_criteria(), binance).run()
