import numpy as np


class MovingAverages():

    # Simple Moving Average
    @staticmethod
    def get_sma(price, period):
        j = next(i for i, x in enumerate(price) if x is not None)
        our_range = range(len(price))[j + period - 1:]
        sub_result = [np.mean(price[i - period + 1: i + 1]) for i in our_range]

        return np.array(sub_result, dtype=float)

    # Exponential Moving Average
    # TODO: Might transfer into ta-lib for better accuracy
    @staticmethod
    def get_ema(price, period):
        df = price['Close']
        df = df.ewm(span=period, min_periods=period - 1,
                    adjust=False, ignore_na=False).mean()

        return np.array(df.tail(1), dtype=float)
