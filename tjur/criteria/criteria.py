from decimal import Decimal
from exchanges.binance import Binance


class Criteria():

    def __init__(self, logger, config, exchange):
        self.logger = logger
        self.config = config
        self.exchange = exchange

    def define_criteria(self):
        symbols = self.get_symbols()
        return self.get_position(symbols)

    def get_symbols(self):
        account = self.exchange.get_account_information()
        symbol1 = self.config['symbols']['one']
        balance_symbol1 = self.exchange.get_symbol_balance(account, symbol1)
        if balance_symbol1:
            symbol2 = self.config['symbols']['two']
            balance_symbol2 = self.exchange.get_symbol_balance(
                account, symbol2)
        else:
            self.logger.log_print_and_exit(
                f"No holdings in account for {symbol1}")
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
            'filters': filter_rules,
            'cur_avg_price': self.exchange.get_cur_avg_price(symbol)}
        if not isinstance(symbols['cur_avg_price'], Decimal):
            self.logger.log_print_and_exit(
                f"{symbols['symbol']} is not a valid symbol")
        return symbols

    def get_position(self, symbols):
        symbol1 = symbols[0]['symbol']
        symbol2 = symbols[1]['symbol']
        position_percentage = Decimal(self.config['position_percentage']) / 100
        position_size = Decimal(
            ((position_percentage * symbols[1]['balance']
              / symbols['cur_avg_price']).quantize(Decimal(10) ** -8)))
        self.logger.info(
            f'{str(position_percentage * 100)}% of {symbol2} is about {position_size} {symbol1} at current price')
        position = {
            'size': position_size,
            'percentage': position_percentage
        }
        criteria = {
            'symbol': symbols,
            'position': position
        }
        self.validate_position(symbols, position)
        return criteria

    def validate_position(self, symbols, position):
        if position['percentage'] < 0.05:
            return None
        while position['percentage'] > 0.05:
            print('Using a position sizing above 5% is not recommended')
            confirm = input('Continue anyway? [y/N] ').upper()
            cur_avg_price = self.exchange.get_cur_avg_price(symbols['symbol'])
            if not confirm == 'Y':
                position['percentage'] = Decimal(
                    input('Select position sizing (%): ')) / 100
                if position['percentage'] <= Decimal(1.0):
                    position['size'] = Decimal(
                        ((position['percentage'] * symbols[1]['balance'])
                            / cur_avg_price).quantize(Decimal(10) ** -8))
                    self.logger.info(
                        f'{str(position_percentage * 100)}% of {symbol2} is about {position_size} {symbol1} at current price')
                else:
                    self.logger.log_print_and_exit('Insufficient funds')
            else:
                break

        cur_avg_price = self.exchange.get_cur_avg_price(symbols['symbol'])
        position['size'] = ((position['percentage']
                            * symbols[1]['balance']) / cur_avg_price)
        steps = str(symbols['filters']['steps']).find('1') - 1
        step_precision = Decimal(10) ** -steps
        if Decimal(steps) > 1:
            position['size'] = Decimal(position['size']).quantize(
                step_precision)
        else:
            position['size'] = int(position['size'])
        if position['size'] < symbols['filters']['min_qty']:
            self.logger.log_print_and_exit(
                f"Amount {position['size']} too low")
