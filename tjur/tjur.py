#!/usr/bin/env python3
import config
import curses
import sys

from analysis.performance import Performance
from argument_parser import Parser
from decimal import Decimal
from criterion import Criterion
from exchanges.binance import Binance
from log.logger import Logger
from sockets import Socket
from ui.colors import Colors
from ui.components.actions import Actions
from ui.components.history import History
from ui.components.logo import Logo
from ui.components.recent import Recent
from ui.components.rolling import Rolling


API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

binance = Binance(API_KEY, API_SECRET)
logger = Logger()
criterias = Criterion(binance, logger)


class Tjur:

    def __init__(self, strategy, trade_mode):
        self.strategy = strategy['strategy']
        self.trade_mode = trade_mode
        self.symbol = strategy['symbol']['symbol']
        self.symbol1 = strategy['symbol'][0]['symbol']
        self.symbol2 = strategy['symbol'][1]['symbol']
        self.action = []
        self.socket = Socket(self.symbol)
        if (trade_mode):
            self.order_type = strategy['position']['order_type']
            self.amount_type = strategy['position']['amount_type']
            self.position_size = strategy['position']['size']
            self.position_percentage = strategy['position']['percentage']
            self.time_frame = strategy['time_frame']
            self.win_target = strategy['win_target']

    def trade(self, stdscr):
        """
        Running calculations and drawing ui
        """

        self.init_curses(stdscr)
        if not (self.trade_mode):
            self.action.append('Demo mode')
        else:
            self.action.append('Calculating buy signal')
        k = 0
        while (k != ord('q')):

            k = stdscr.getch()
            signal = 0
            self.update_ui(stdscr)
            if (self.trade_mode and self.strategy.calculate_buy_signal()
                    and not binance.get_open_orders(self.symbol)):
                position_size = self.get_position_size('BUY')
                price = self.get_position_price()
                buy_order = self.buy(position_size, price)
                signal = buy_order['signal']
                self.update_ui(stdscr)
                self.action.append('Calculating sell signal')

                while (signal == 1):
                    latest_price = Decimal(
                        binance.get_latest_price(self.symbol)['price']
                        or buy_order['price'])
                    stop_loss = buy_order['price'] * Decimal(0.92)
                    sell_signal = self.strategy.calculate_sell_signal()
                    self.update_ui(stdscr)
                    k = stdscr.getch()

                    if ((stop_loss >= latest_price)
                            or (sell_signal and latest_price
                                >= buy_order['take_profit'])):
                        position_size = self.get_position_size('SELL')
                        price = self.get_position_price()
                        sell_order = self.sell(position_size, price)

                        pl = Performance.calculate_pl(
                            buy_order['price'], sell_order['price'])
                        logger.log('Margin: ' + str(round(pl, 3)) + '%')
                        self.action.append('Sold! Margin: ' + str(round(pl, 3))
                                           + '%')
                        signal = sell_order['signal']
                        self.action.append('Calculating buy signal')
                        self.update_ui(stdscr)

    def get_position_size(self, side):
        if (self.amount_type == 2):
            account = binance.get_account_information()
            if (side == 'BUY'):
                balance_symbol2 = binance.get_symbol_balance(
                    account, self.symbol2)
                cur_avg_price = binance.get_cur_avg_price(self.symbol)
                return (Decimal(
                    self.position_percentage * balance_symbol2)
                    / cur_avg_price.quantize(Decimal(10) ** -8))
            elif(side == 'SELL'):
                balance_symbol1 = binance.get_symbol_balance(
                    account, self.symbol1)
                return Decimal(
                    self.position_percentage * balance_symbol1).quantize(
                    Decimal(10) ** -8)
        else:
            return self.position_size

    def get_position_price(self):
        if (self.order_type == 'LIMIT'):
            return binance.get_latest_price(self.symbol)['price']
        else:
            return None

    def buy(self, position_size, price):
        buy_order = binance.create_new_order(
            self.symbol, 'BUY', self.order_type, position_size, price)
        buy_price = Decimal(buy_order['fills'][0]['price'])
        take_profit = buy_price * self.win_target
        logger.log('OrderId: ' + str(buy_order['orderId']) + ' Buying '
                   + str(position_size) + ' ' + self.symbol1 + ' for '
                   + '{:.8f}'.format(buy_price) + self.symbol2)
        logger.log('Aiming to sell at ' + str(take_profit) + ' '
                   + self.symbol2)
        self.action.append('Bought at ' + str(buy_price))
        self.update_history()
        order = {
            'price': buy_price,
            'take_profit': take_profit,
            'signal': 1}
        return order

    def sell(self, position_size, price):
        sell_order = binance.create_new_order(
            self.symbol, 'SELL', self.order_type, position_size, price)
        sell_price = Decimal(sell_order['fills'][0]['price'])
        logger.log('OrderId: ' + str(sell_order['orderId'] + ' Selling '
                                     + position_size + ' ' + self.symbol1
                                     + ' for ' + '{:.8f}'.format(sell_price)
                                     + self.symbol2))
        self.action.append('Sold at ' + str(sell_price))
        self.update_history()
        order = {
            'price': sell_price,
            'signal': 0}
        return order

    def update_history(self):
        self.history = binance.get_trade_history(self.symbol, 15)
        self.history.reverse()

    def init_curses(self, stdscr):
        curses.curs_set(0)
        stdscr.clear()
        stdscr.refresh()
        stdscr.nodelay(1)
        Colors.init_colors()

    def update_ui(self, stdscr):
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        Logo(self.symbol, curses, stdscr, ' tjur ').draw()
        Rolling(self.socket, strategy['symbol'], curses, stdscr, width,
                ' 24h ').draw()
        History(binance, strategy['symbol'], self.history, 1, curses, stdscr,
                height, width, ' history ').draw()
        Actions(binance, self.action, curses, stdscr, height, width,
                ' actions ').draw()
        Recent(self.socket, binance, strategy['symbol'], curses, stdscr,
               height, width, ' recent trades ').draw()
        stdscr.refresh()

    def run(self):
        try:
            self.update_history()
            curses.wrapper(self.trade)

        except KeyboardInterrupt:
            logger.log_print_and_exit('Exiting')


if __name__ == '__main__':
    parser = Parser()
    args = parser.parse()

    if (args.help):
        parser.print_help()
        sys.exit(0)
    if (args.version):
        print(parser.get_version())

    trade_mode = args.trade
    strategy = criterias.select_strategy(trade_mode)
    Tjur(strategy, trade_mode).run()
