import os

import numpy as np
import pandas as pd

from indicators.sma import SimpleMovingAverage

class Maco:
    """
    Moving Average(MA) Cross-Over strategy.

    Takes two MA's of different time windows.
    When the line crosses we detect a potential change of trend.

    Args:
    pairings (str): Symbol pair to operate on i.e BTCUSDT
    candle_interval (str): Trading time frame i.e 5m or 4h
    short_ma (int): Number of candles for short period
    long_ma (int): Number of candles for long period
    price_type (str): Type of price (OHLC) i.e High or Close
    """

    def __init__(self, pairings, candle_interval, short_ma, long_ma, price_type):
        self.pairings = pairings
        self.candle_interval = candle_interval
        self.short_ma = short_ma
        self.long_ma = long_ma
        self.price_type = price_type

    def calculate_signals(self):
        """
        Returns:
        pandas.DataFrame: 1 for long, -1 for short or 0 for hold.
        """

        signals = pd.DataFrame()
        signals['signal'] = 0


        sma_short = SimpleMovingAverage.get_sma(self.short_ma[self.price_type], 25)
        sma_long = SimpleMovingAverage.get_sma(self.long_ma[self.price_type], 50)

        signals['short_ma'] = sma_short
        signals['long_ma'] = sma_long


        """
        Creates a signal when the short MA period crosses the long MA period from below.

        TODO:
        """

        signals['signal'] = np.where(signals['short_ma'] > signals['long_ma'], 1.0, 0.0)

        signals['positions'] = signals['signal'].diff()

        return signals
