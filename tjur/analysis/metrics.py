# Historical metrics

from exchanges.binance import Binance


class Metrics():

    # Returns a list with OHLCV of given parameters
    def get_historical_data(self, exchange, pairing, candle_interval, start_time, end_time, limit):

        historical_data = list()

        historical_data = self.exchange.get_historical_data(
            self, pairing, candle_interval, start_time, end_time, limit)

        return historical_data
