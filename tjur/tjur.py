import config

from decimal import Decimal
from analysis.performance import Performance
from criterion import Criterion
from exchanges.binance import Binance
from log.logger import Logger


API_KEY = config.BINANCE['api_key']
API_SECRET = config.BINANCE['api_secret']

binance = Binance(API_KEY, API_SECRET)
logger = Logger()
criterias = Criterion(binance, logger)


class Tjur:

    def __init__(self, strategy):
        self.strategy = strategy['strategy']
        self.symbol = strategy['symbol']['symbol']
        self.symbol1 = strategy['symbol'][0]['symbol']
        self.symbol2 = strategy['symbol'][1]['symbol']
        self.order_type = strategy['position']['order_type']
        self.amount_type = strategy['position']['amount_type']
        self.position_size = strategy['position']['size']
        self.position_percentage = strategy['position']['percentage']
        self.time_frame = strategy['time_frame']
        self.win_target = strategy['win_target']

    def calculate_signals(self):
        """
        Calculates when to send signal to buy or sell.
        """

        signal = 0
        if (self.strategy.calculate_buy_signal()
                and not binance.get_open_orders(self.symbol)):
            position_size = self.get_position_size('BUY')
            price = self.get_position_price()
            buy_order = self.buy(position_size, price)
            signal = buy_order['signal']

            while (signal == 1):
                latest_price = Decimal(
                    binance.get_latest_price(self.symbol)['price']
                    or buy_order['price'])
                stop_loss = buy_order['price'] * Decimal(0.92)
                sell_signal = self.strategy.calculate_sell_signal()

                if ((stop_loss >= latest_price)
                        or (sell_signal and latest_price
                            >= buy_order['take_profit'])):
                    position_size = self.get_position_size('SELL')
                    price = self.get_position_price()
                    sell_order = self.sell(position_size, price)

                    pl = Performance.calculate_pl(
                        buy_order['price'], sell_order['price'])
                    logger.log_print('Margin: ' + str(round(pl, 3)) + '%')
                    signal = sell_order['signal']

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
        logger.log_print('OrderId: ' + str(buy_order['orderId']) + ' Buying '
                         + str(position_size) + ' ' + self.symbol1 + ' for '
                         + '{:.8f}'.format(buy_price) + self.symbol2)
        logger.log('Aiming to sell at ' + str(take_profit) + ' '
                   + self.symbol2)
        order = {
            'price': buy_price,
            'take_profit': take_profit,
            'signal': 1}
        return order

    def sell(self, position_size, price):
        sell_order = binance.create_new_order(
            self.symbol, 'SELL', self.order_type, position_size, price)
        sell_price = Decimal(sell_order['fills'][0]['price'])
        logger.log_print('OrderId: ' + str(sell_order['orderId'] + ' Selling '
                         + position_size + ' ' + self.symbol1 + ' for '
                         + '{:.8f}'.format(sell_price) + self.symbol2))
        order = {
            'price': sell_price,
            'signal': 0}
        return order

    def trade(self):
        try:
            while True:
                self.calculate_signals()

        except KeyboardInterrupt:
            logger.log_print_and_exit('Exiting')


if __name__ == '__main__':
    strategy = criterias.select_strategy()
    if (criterias.is_strategy_ready(strategy['strategy'])):
        Tjur(strategy).trade()
