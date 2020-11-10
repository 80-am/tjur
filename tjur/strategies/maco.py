from indicators.ma import MovingAverages


class Maco():
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

    def __init__(self, exchange, ma_type, symbol, time_frame, short_ticks, long_ticks,
                 logger):
        self.exchange = exchange
        self.ma_type = ma_type.lower()
        self.symbol = symbol
        self.time_frame = time_frame
        self.short_ticks = short_ticks
        self.long_ticks = long_ticks
        self.logger = logger

    def calculate_buy_signal(self):
        """
        Golden Cross (Bullish Signal).

        The golden cross appears when a symbols short-term MA
        crosses its long-term MA from below.

        Returns:
        bool
        """

        short_ma_price = self.exchange.get_historical_price(
            self.symbol, self.time_frame, self.short_ticks)
        long_ma_price = self.exchange.get_historical_price(
            self.symbol, self.time_frame, self.long_ticks)
        if self.ma_type == 'sma':
            short_ma = MovingAverages.get_sma(short_ma_price, self.short_ticks)
            long_ma = MovingAverages.get_sma(long_ma_price, self.long_ticks)
        elif self.ma_type == 'ema':
            short_ma = MovingAverages.get_ema(short_ma_price, self.short_ticks)
            long_ma = MovingAverages.get_ema(long_ma_price, self.long_ticks)
        else:
            self.logger.log_print('Please use a supported moving average')

        if short_ma > long_ma:
            self.logger.log(f"Golden crossing: Short MA ({short_ma}) greater than long MA ({long_ma})")
            return True

    def calculate_sell_signal(self):
        """
        Death Cross (Bearish Signal).

        The death cross appears when a symbols short-term MA
        crosses its long-term MA from above.

        Returns:
        bool
        """

        short_ma_price = self.exchange.get_historical_price(
            self.symbol, self.time_frame, self.short_ticks)
        long_ma_price = self.exchange.get_historical_price(
            self.symbol, self.time_frame, self.long_ticks)
        if self.ma_type == 'sma':
            short_ma = MovingAverages.get_sma(short_ma_price, self.short_ticks)
            long_ma = MovingAverages.get_sma(long_ma_price, self.long_ticks)
        elif self.ma_type == 'ema':
            short_ma = MovingAverages.get_ema(short_ma_price, self.short_ticks)
            long_ma = MovingAverages.get_ema(long_ma_price, self.long_ticks)
        else:
            self.logger.log_print('Please use a supported moving average')

        if long_ma > short_ma:
            self.logger.log(f"Death crossing: Long MA ({long_ma}) greater than short MA ({short_ma})")
            return True

    def is_ready(self):
        """
        Checking if strategy should start sending signals.

        If short-term MA is above long-term, dont start trading.

        Returns:
        bool
        """

        return self.calculate_sell_signal()
