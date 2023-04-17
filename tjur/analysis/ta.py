from analysis.indicators import Indicators
from exchanges.binance import Binance
from decimal import Decimal

CANDLE_INTERVAL = '5m'
EMA_LENGTH = 20
RSI_LENGTH = 14
RSI_LEVEL = 55


class Ta():

    def __init__(self, logger, config, symbols, exchange):
        self.logger = logger
        self.config = config
        self.symbols = symbols
        self.exchange = exchange
        self.history = exchange.get_historical_data(
            self.symbols, CANDLE_INTERVAL, 1000)
        self.last_price = Decimal(
            exchange.get_latest_price(self.symbols)['price'])

    def matches_entry_criteria(self):
        above_ema = self.is_price_above_ema()
        above_vwap = self.is_above_vwap()
        below_rsi = self.is_below_rsi()

        if above_ema == above_vwap == below_rsi == True:
            self.logger.info(f'All criterias matching')
            return True

    def matches_exit_criteria(self):
        return False  # TODO

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

    def is_below_rsi(self):
        rsi = Indicators(self.logger, self.history).calculate_rsi(RSI_LENGTH)
        if rsi is None:
            return False
        if rsi > RSI_LEVEL:
            self.logger.debug(
                f'RSI({round(rsi, 2)}) above {RSI_LEVEL}')
            return False
        else:
            self.logger.debug(
                f'RSI({round(rsi, 2)}) below {RSI_LEVEL}')
            return True
