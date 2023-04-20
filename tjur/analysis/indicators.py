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

    def calculate_adx(self):
        return ta.adx(
            high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window=14)

    def calculate_levels(self, last_price):
        levels = []
        support = []
        resistance = []
        s = np.mean(self.data['High'] - self.data['Low'])

        for i in range(2, self.data.shape[0]-2):
            if self.is_support(i):
                l = self.data['Low'][i]
                if self.is_far_from_level(l, s, support):
                    support.append(l)

            elif self.is_resistance(i):
                l = self.data['High'][i]
                if self.is_far_from_level(l, s, resistance):
                    resistance.append(l)

        closest_resistance = self.get_closest_level(
            resistance, float(last_price))
        closest_support = self.get_closest_level(
            support, float(last_price))
        return {"resistance": self.get_closest_level(resistance, float(last_price)), "support": self.get_closest_level(support, float(last_price))}

    def is_support(self, i):
        return self.data['Low'][i] < self.data['Low'][i-1] and self.data['Low'][i] < self.data['Low'][i+1] and self.data['Low'][i+1] < self.data['Low'][i+2] and self.data['Low'][i-1] < self.data['Low'][i-2]

    def is_resistance(self, i):
        return self.data['High'][i] > self.data['High'][i-1] and self.data['High'][i] > self.data['High'][i+1] and self.data['High'][i+1] > self.data['High'][i+2] and self.data['High'][i-1] > self.data['High'][i-2]

    def is_far_from_level(self, l, s, levels):
        return np.sum([abs(l-x) < s for x in levels]) == 0

    def get_closest_level(self, levels, last_price):
        arr = np.asarray(levels)
        i = (np.abs(arr - last_price)).argmin()
        return arr[i]
