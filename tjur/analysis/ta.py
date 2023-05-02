import sys

from analysis.indicators import Indicators
from exchanges.binance import Binance
from decimal import Decimal

CANDLE_INTERVAL = '5m'
EMA_LENGTH = 20
RSI_LENGTH = 14
RSI_LEVEL = 55
TAKE_PROFIT_PERCENTAGE = 1.01  # TODO


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
        above_resistance = self.is_above_restistance(history, last_price)
        self.logger.write_to_screen(3, 0, f'💰 Last price: {last_price}')
        self.get_adx(history)

        if above_ema == above_vwap == below_rsi == above_resistance == True:
            self.logger.info(f'All criterias matching')
            return True

    def matches_exit_criteria(self, purchase_price):
        last_price = Decimal(
            self.exchange.get_latest_price(self.symbols)['price'])
        history = self.exchange.get_historical_data(
            self.symbols, '1m', 1000)
        self.logger.write_to_screen(3, 0, f'💰 Last price: {last_price}')
        stop_loss = self.set_stop_loss(purchase_price)
        self.logger.write_to_screen(6, 0, f'🛑 Stop loss: {stop_loss:.8f}')
        self.get_adx(history)
        above_profit = self.is_above_take_profit(last_price, purchase_price)
        below_resistance = self.is_below_support(history, last_price)
        # TODO: make sure to not sell if potential upswing
        if (last_price < stop_loss and above_profit) or below_resistance:
            return True

    def set_stop_loss(self, purchase_price):
        # TODO: Define a good stop loss
        return purchase_price * Decimal(0.95)

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

    def is_above_restistance(self, history, last_price):
        levels = self.get_support_and_resistance(history, last_price)
        if last_price > levels['resistance']:
            return True

    def is_below_support(self, history, last_price):
        levels = self.get_support_and_resistance(history, last_price)
        if last_price < levels['support']:
            return True

    def is_above_take_profit(self, last_price, purchase_price):
        take_profit = Decimal(TAKE_PROFIT_PERCENTAGE) * purchase_price
        if last_price > take_profit:
            return True

    def get_adx(self, history):
        adx = Indicators(
            self.logger, history).calculate_adx().iloc[-1]['ADX_14']
        self.logger.write_to_screen(8, 0, f'💪 ADX(14): {adx:.2f}')

    def get_support_and_resistance(self, history, last_price):
        levels = Indicators(self.logger, history).calculate_levels(last_price)
        support = levels['support']
        resistance = levels['resistance']
        self.logger.write_to_screen(
            7, 0, f'🎚️  Levels(Sup/Res): {support} / {resistance}')
        return levels
