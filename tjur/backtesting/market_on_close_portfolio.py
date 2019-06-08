import pandas as pd

class MarketOnClosePortfolio:
    """
    Encapsulates the notion of a portfolio of positions based
    on a set of signals as provided by a Strategy.

    Args:
    pairings (str): Symbol pair to operate on i.e BTCUSDT
    bars (DataFrame): Bars for a symbol set TODO
    signals (DataFrame): Signals (1, 0, -1) for each pairing TODO
    initial_capital (int): The capital to start with TODO
    """

    def __init__(self, pairings, bars, signals, initial_capital):
        self.pairings = pairings
        self.bars = bars
        self.signals = signals
        self.initial_capital = float(initial_capital)
        self.positions = self.generate_positions()

    def generate_positions(self):
        positions = pd.DataFrame(index=signals.index).fillna(0.0)
        positions[self.pairings] = 100*signals['signal'] # this buys 100 shares

        return positions

    def backtest_portfolio(self):
        portfolio = self.positions*self.bars['Close']
        position_diff = self.position.diff()

        portfolio['holdings'] = (self.positions*self.bars['Close']).sum(axis=1)
        portfolio['cash'] = self.initial_capital - (position_diff*self.bars['Close']).sum(axis=1).cumsum()

        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()

        return portfolio

