import talib as ta
import numpy as np
import pandas as pd

from exchanges.binance import Binance

binance = Binance('apikey', 'apisecret')


class Macd:
    """
    Moving Average Convergence/Divergence(MACD) strategy.

    The MACD is calculated by subtracting a slow EMA from a fast EMA.
    When the MACD crosses the signal line (often EMA(9)), it indicates a change of trend.

    Args:
    symbol (str): Symbol pair to operate on i.e BTCUSDT
    time_frame (str): Trading time frame i.e 5m or 4h
    """

    def __init__(self, symbol, time_frame):
        self.symbol = symbol
        self.time_frame = time_frame

    def calculate_buy_signal(self):
        """
        When the MACD crosses the signal line from below it indicates a bullish trend.

        Returns:
        bool
        """

        raw_price = binance.get_historical_price(
            self.symbol, self.time_frame, 60)
        prices = raw_price['Close']
        df = pd.DataFrame()
        df['macd'], df['macdsignal'], df['macdhist'] = ta.MACD(
            prices, fastperiod=12, slowperiod=26, signalperiod=9)

        macd = float(df['macd'].tail(1))
        prev_macd = float(df['macd'].tail(2).iloc[-2])
        macd_signal = float(df['macdsignal'].tail(1))
        prev_macd_signal = float(df['macdsignal'].tail(2).iloc[-2])

        if (macd > macd_signal and prev_macd < prev_macd_signal):
            return True

    def calculate_sell_signal(self):
        """
        When the MACD crosses the signal line from above it indicates a bearish trend.

        Returns:
        bool
        """

        raw_price = binance.get_historical_price(
            self.symbol, self.time_frame, 60)
        prices = raw_price['Close']
        df = pd.DataFrame()
        df['macd'], df['macdsignal'], df['macdhist'] = ta.MACD(
            prices, fastperiod=12, slowperiod=26, signalperiod=9)

        macd = float(df['macd'].tail(1))
        macd_signal = float(df['macdsignal'].tail(1))

        if (macd < macd_signal):
            return True

    # TODO: Add validation
    def is_ready(self):
        """
        Checking if strategy should start sending signals.

        Returns:
        bool
        """

        return True
