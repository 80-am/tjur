import numpy as np
import pandas_ta as ta
import pandas as pd


class Indicators():

    def __init__(self, logger, data):
        self.logger = logger
        self.data = data

    def calculate_ema(self, length):
        df = self.data['Close']
        df = df.ewm(span=length, min_periods=length - 1,
                    adjust=False, ignore_na=False).mean()

        return np.array(df.tail(1), dtype=float)

    def calculate_vwap(self):
        df = ta.vwap(self.data['High'], self.data['Low'],
                     self.data['Close'], self.data['Volume'], anchor='D')
        return df.iloc[-1]

    def calculate_rsi(self, length):
        if self.data['Close'] is not None and length <= len(self.data['Close']):
            return ta.rsi(self.data['Close'], length=length).iloc[-1]
