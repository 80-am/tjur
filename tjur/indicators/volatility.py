import numpy as np


class Volatility():

    # Average True Range
    @staticmethod
    def get_atr(data, trend_periods=14, open_col='Open', high_col='High', low_col='Low', close_col='Close'):
        for index, row in data.iterrows():
            prices = [row[high_col], row[low_col],
                      row[close_col], row[open_col]]
            if index > 0:
                val1 = np.amax(prices) - np.amin(prices)
                val2 = abs(np.amax(prices) - data.at[index - 1, close_col])
                val3 = abs(np.amin(prices) - data.at[index - 1, close_col])
                true_range = np.amax([val1, val2, val3])

            else:
                true_range = np.amax(prices) - np.amin(prices)

            data.at[index, 'True range'] = true_range
        data['ATR'] = data['True range'].ewm(
            ignore_na=False, min_periods=0, com=trend_periods, adjust=True).mean()

        return data
