import talib as ta
import numpy as np
import pandas as pd

from exchanges.binance import Binance

binance = Binance('apikey', 'apisecret')

class DoubleCross:
    """
    Moving Average Convergence/Divergence(MACD) and Stochastic, double-cross strategy.
    Args:
    ma_type (str): Type of moving average i.e EMA or SMA
    symbol (str): Symbol pair to operate on i.e BTCUSDT
    candle_interval (str): Trading time frame i.e 5m or 4h
    short_ticks (int): Number of candles for short period
    long_ticks (int): Number of candles for long period
    """

    def __init__(self, ma_type, symbol, candle_interval, short_ticks, long_ticks):
        self.ma_type = ma_type.lower()
        self.symbol = symbol
        self.candle_interval = candle_interval
        self.short_ticks= short_ticks
        self.long_ticks = long_ticks

    def calculate_buy_signal(self):
        """
        TODO: Add support for custom parameters

        Returns:
        True or False (Boolean)
        """

        raw_price = binance.get_historical_price(self.symbol, self.candle_interval, 60)
        prices = raw_price['Close']
        df = pd.DataFrame()
        df['macd'], df['macdsignal'], df['macdhist'] = ta.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)

        macd = float(df['macd'].tail(1))
        macd_signal = float(df['macdsignal'].tail(1))

        if (macd > macd_signal):
            return True
        else:
            return False

    def calculate_sell_signal(self):
        """
        TODO: ...

        Returns:
        ...
        """

        return False
