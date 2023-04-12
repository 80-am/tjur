#!/usr/bin/env python3
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
        ta = Ta(self.logger, self.symbols, self.exchange)
        while k != ord('q'):
            if (ta.matches_entry_criteria() and not binance.get_open_orders(self.symbols)):
                self.position_size = self.get_position_size('BUY')
                price = self.get_position_price()
                buy_order = self.buy(self.position_size, price)
                signal = buy_order['signal']
                self.logger.info('Calculating sell signal.')

                while signal == 1:
                    latest_price = Decimal(
                        binance.get_latest_price(self.symbols)['price']
                        or buy_order['price'])
                    stop_loss = buy_order['price'] * Decimal(0.92)
                    sell_signal = ta.matches_exit_criteria()

                    if ((stop_loss >= latest_price) or (sell_signal and latest_price
                                                        >= buy_order['take_profit'])):
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
        if self.amount_type == 2:
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
        return self.position_size

    # TODO: Create price logic when using LIMIT, for now uses latest price.
    def get_position_price(self):
        if self.order_type == 'LIMIT':
            return self.exchange.get_latest_price(self.symbols)['price']
        return None

    def buy(self, position_size, price):
        buy_order = self.exchange.create_new_order(
            self.symbols, 'BUY', self.order_type, str(position_size), price)
        buy_price = Decimal(buy_order['fills'][0]['price'])
        take_profit = buy_price * 1.1  # TODO: create exit logic
        self.logger.info(
            f"OrderId: {buy_order['orderId']} Buying {position_size} {self.symbol1} @ {'{:.8f}'.format(buy_price)}")
        self.logger.info(f"Aiming to sell at {take_profit} {self.symbol2}")
        order = {
            'price': buy_price,
            'take_profit': take_profit,
            'signal': 1}
        return order

    def sell(self, position_size, price):
        sell_order = self.exchange.create_new_order(
            self.symbols, 'SELL', self.order_type, str(position_size), price)
        sell_price = Decimal(sell_order['fills'][0]['price'])
        self.logger.info(
            f"OrderId: {sell_order['orderId']} Selling {position_size} {self.symbol1} @ {'{:.8f}'.format(sell_price)}")
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
    with open(os.path.join(path, "config.yaml"), "r") as c, open(os.path.join(path, 'assets/start-up.txt')) as f:
        config = yaml.load(c, Loader=yaml.FullLoader)
        API_KEY = config['binance']['api_key']
        API_SECRET = config['binance']['api_secret']
        print(f.read())

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
