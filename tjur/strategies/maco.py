import os

import numpy as np
import pandas as pd

from exchanges.binance import Binance
from indicators.ma import MovingAverages

binance = Binance('apikey', 'apisecret')

class Maco:
    """
    Moving Average(MA) Cross-Over strategy.

    Takes two MA's of different time windows.
    When the line crosses we detect a potential change of trend.

    Args:
    ma_type (str): Type of moving average i.e EMA or SMA
    symbol (str): Symbol pair to operate on i.e BTCUSDT
    time_frame (str): Trading time frame i.e 5m or 4h
    short_ticks (int): Number of candles for short period
    long_ticks (int): Number of candles for long period
    TODO: price_type (str): Type of price (OHLC) i.e High or Close
    """

    def __init__(self, ma_type, symbol, time_frame, short_ticks, long_ticks):
        self.ma_type = ma_type.lower()
        self.symbol = symbol
        self.time_frame = time_frame
        self.short_ticks= short_ticks
        self.long_ticks = long_ticks

    def calculate_buy_signal(self):
        """
        Golden Cross (Bullish Signal).

        The golden cross appears when a symbols short-term MA
        crosses its long-term MA from below.

        Returns:
        bool
        """

        short_ma_price = binance.get_historical_price(self.symbol, self.time_frame, self.short_ticks)
        long_ma_price = binance.get_historical_price(self.symbol, self.time_frame, self.long_ticks)
        if (self.ma_type == 'sma'):
            short_ma = MovingAverages.get_sma(short_ma_price, self.short_ticks)
            long_ma = MovingAverages.get_sma(long_ma_price, self.long_ticks)
        elif (self.ma_type == 'ema'):
            short_ma = MovingAverages.get_ema(short_ma_price, self.short_ticks)
            long_ma = MovingAverages.get_ema(long_ma_price, self.long_ticks)
        else:
            print('Please use a supported moving average')

        if (short_ma > long_ma):
            return True

    def calculate_sell_signal(self):
        """
        Death Cross (Bearish Signal).

        The death cross appears when a symbols short-term SMA
        crosses its long-term SMA from above.

        Returns:
        bool
        """

        short_ma_price = binance.get_historical_price(self.symbol, self.time_frame, self.short_ticks)
        long_ma_price = binance.get_historical_price(self.symbol, self.time_frame, self.long_ticks)
        if (self.ma_type == 'sma'):
            short_ma = MovingAverages.get_sma(short_ma_price, self.short_ticks)
            long_ma = MovingAverages.get_sma(long_ma_price, self.long_ticks)
        elif (self.ma_type == 'ema'):
            short_ma = MovingAverages.get_ema(short_ma_price, self.short_ticks)
            long_ma = MovingAverages.get_ema(long_ma_price, self.long_ticks)
        else:
            print('Please use a supported moving average')

        if long_ma > short_ma:
            return True

