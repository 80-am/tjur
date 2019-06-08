import datetime
import pandas as pd
import pandas_datareader as pdr

from backtesting.market_on_close_portfolio import MarketOnClosePortfolio
from exchanges.binance import Binance
from strategies.maco import Maco

class Backtesting:

    pairings = 'AAPL'
    start_period = datetime.datetime(1990,1,1)
    end_period = datetime.datetime(2002,1,1)
    bars = pdr.DataReader(pairings, "yahoo", start_period, end_period)

    mac = Maco(pairings, bars, 25, 50, 4)
    signals = mac.calculate_signals()

    portfolio = MarketOnClosePortfolio(pairings, bars, signals, 100000.0)
    returns = portfolio.backtest_portfolio()

    # Plot two charts to assess trades and equity curve
    fig = plt.figure()
    fig.patch.set_facecolor('white')     # Set the outer colour to white
    ax1 = fig.add_subplot(211,  ylabel='Price in $')

    # Plot the AAPL closing price overlaid with the moving averages
    bars['Close'].plot(ax=ax1, color='r', lw=2.)
    signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=2.)

    # Plot the "buy" trades against AAPL
    ax1.plot(signals.ix[signals.positions == 1.0].index,
             signals.short_mavg[signals.positions == 1.0],
             '^', markersize=10, color='m')

    # Plot the "sell" trades against AAPL
    ax1.plot(signals.ix[signals.positions == -1.0].index,
             signals.short_mavg[signals.positions == -1.0],
             'v', markersize=10, color='k')

    # Plot the equity curve in dollars
    ax2 = fig.add_subplot(212, ylabel='Portfolio value in $')
    returns['total'].plot(ax=ax2, lw=2.)

    # Plot the "buy" and "sell" trades against the equity curve
    ax2.plot(returns.ix[signals.positions == 1.0].index,
             returns.total[signals.positions == 1.0],
             '^', markersize=10, color='m')
    ax2.plot(returns.ix[signals.positions == -1.0].index,
             returns.total[signals.positions == -1.0],
             'v', markersize=10, color='k')

    # Plot the figure
    fig.show()
