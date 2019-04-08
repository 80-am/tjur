import numpy as np

# Simple Moving Average
class SimpleMovingAverage:

    def get_sma(price, period):
        j = next(i for i, x in enumerate(price) if x is not None)
        our_range = range(len(price))[j + period - 1:]
        empty_list = [None] * (j + period - 1)
        sub_result = [np.mean(price[i - period + 1: i + 1]) for i in our_range]
                      
        return np.array(sub_result)

