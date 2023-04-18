import sys

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

    def matches_entry_criteria(self):
        history = self.exchange.get_historical_data(
            self.symbols, CANDLE_INTERVAL, 1000)
        last_price = Decimal(
            self.exchange.get_latest_price(self.symbols)['price'])
        above_ema = self.is_price_above_ema(history, last_price)
        above_vwap = self.is_above_vwap(history, last_price)
        below_rsi = self.is_below_rsi(history)
        self.logger.write_to_screen(3, 0, f'💰 Last price: {last_price}')

        if above_ema == above_vwap == below_rsi == True:
            self.logger.info(f'All criterias matching')
            return True

    def matches_exit_criteria(self):
        last_price = Decimal(
            self.exchange.get_latest_price(self.symbols)['price'])
        self.logger.write_to_screen(3, 0, f'💰 Last price: {last_price}')
        return False  # TODO

    def is_price_above_ema(self, history, last_price):
        ema = Indicators(self.logger, history.tail(
            EMA_LENGTH)).calculate_ema(EMA_LENGTH)
        if ema is None:
            return False
        if last_price > ema:
            self.logger.debug(
                f'Last price({last_price}) is above EMA({ema})')
            self.logger.write_to_screen(4, 0, f'✅ EMA({EMA_LENGTH}): {ema}')
            return True
        else:
            self.logger.debug(
                f'Last price({last_price}) is below EMA({ema})')
            self.logger.write_to_screen(4, 0, f'❌ EMA({EMA_LENGTH}): {ema}')
            return False

    def is_above_vwap(self, history, last_price):
        vwap = Indicators(self.logger, history).calculate_vwap()
        if vwap is None:
            return False
        if last_price > vwap:
            self.logger.debug(
                f'Last price({last_price}) is above VWAP({vwap})')
            self.logger.write_to_screen(5, 0, f'✅ VWAP: {vwap}')
            return True
        else:
            self.logger.debug(
                f'Last price({last_price}) is below VWAP({vwap})')
            self.logger.write_to_screen(5, 0, f'❌ VWAP: {vwap}')
            return False

    def is_below_rsi(self, history):
        rsi = Indicators(self.logger, history).calculate_rsi(RSI_LENGTH)
        if rsi is None:
            return False
        if rsi > RSI_LEVEL:
            self.logger.debug(
                f'RSI({round(rsi, 2)}) above {RSI_LEVEL}')
            self.logger.write_to_screen(6, 0, f'❌ RSI({RSI_LEVEL}): {rsi}')
            return False
        else:
            self.logger.debug(
                f'RSI({round(rsi, 2)}) below {RSI_LEVEL}')
            self.logger.write_to_screen(6, 0, f'✅ RSI({RSI_LEVEL}): {rsi}')
            return True
