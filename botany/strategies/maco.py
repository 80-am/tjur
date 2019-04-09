import os

import pandas as pd

class Maco:
    """
    Moving Average(MA) Cross-Over strategy.

    Takes two MA's of different time windows.
    When the line crosses we detect a potential change of trend.

    Args:
    pairing (str): Symbol pair to operate on i.e BTCUSDT
    candle_interval (str): Trading time frame i.e 5m or 4h
    short_ma (int): Number of candles for short period
    long_ma (int): Number of candles for long period
    price_type (int): Type of price (OHLC) i.e 2 as in High or 4 as in Close
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

        signals = pd.DataFrame(index=self.candle_interval.index)
        signals['signal'] = 0.0

        signals['short_ma'] = pd.rolling_mean(candle_interval['Close'], self.short_ma, min_periods=1)
        signals['long_ma'] = pd.rolling_mean(candle_interval['Close'], self.long_ma, min_periods=1)

        """
        Creates a signal when the short MA period crosses the long MA period from below.
        """
        signals['signal'][self.short_ma:] = np.where(signals['short_ma'][self.short_ma:]
                                                    > signals['long_ma'][self.short_ma:], 1.0, 0.0)

        signals['positions'] = signals['signal'].diff()

        return signals
