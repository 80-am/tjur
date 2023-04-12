from analysis.indicators import Indicators
from exchanges.binance import Binance
from decimal import Decimal

CANDLE_INTERVAL = '5m'
EMA_LENGTH = 20


class Ta():

    def __init__(self, logger, symbols, exchange):
        self.logger = logger
        self.symbols = symbols
        self.exchange = exchange
        self.history = exchange.get_historical_data(
            self.symbols, CANDLE_INTERVAL, 1000)
        self.last_price = Decimal(
            exchange.get_latest_price(self.symbols)['price'])

    def matches_entry_criteria(self):
        above_ema = self.is_price_above_ema()
        above_vwap = self.is_above_vwap()

        if above_ema == above_ema == True:
            return True

    def matches_exit_criteria(self):
        return False

    def is_price_above_ema(self):
        ema = Indicators(self.logger, self.history.tail(
            EMA_LENGTH)).calculate_ema(EMA_LENGTH)
        if ema is None:
            return False
        if self.last_price > ema:
            self.logger.debug(
                f'Last price({self.last_price}) is above EMA({ema})')
            return True
        else:
            self.logger.debug(
                f'Last price({self.last_price}) is below EMA({ema})')
            return False

    def is_above_vwap(self):
        vwap = Indicators(self.logger, self.history).calculate_vwap()
        if vwap is None:
            return False
        if self.last_price > vwap:
            self.logger.debug(
                f'Last price({self.last_price}) is above VWAP({vwap})')
            return True
        else:
            self.logger.debug(
                f'Last price({self.last_price}) is below VWAP({vwap})')
            return False
