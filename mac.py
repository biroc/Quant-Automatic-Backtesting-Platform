#!/usr/bin/python
# -*- coding: utf-8 -*-

#mac.py CH15  Moving Average strategy implement
#Nov 2

# @Aurthor: Dawei Wang

import datetime
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

from strategy import Strategy
from event import SignalEvent
from backtest import Backtest
from data import HistoricCSVDataHandler
from execution import SimulatedExecutionHandler
from portfolio import Portfolio


#######重点#########
#需要Strategy Subclass to creat MACS 这个策略
class MovingAverageCrossStrategy(Strategy):

    """
    Carries out a basic Moving Average Crossover strategy with a
    short/long simple weighted moving average. Default short/long
    windows are 100/400 periods respectively.
    """

    """
    Initialises the Moving Average Cross Strategy.

    Parameters:
    bars - The DataHandler object that provides bar information
    events - The Event Queue object.
    shortWindow - The short moving average lookback.
    longWindow - The long moving average lookback.
    """

    def __init__(
            self, bars, events, shortWindow = 100, longWindow = 400
    ):

        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.shortWindow = shortWindow
        self.longWindow = longWindow

        #初始资金
        # Set to True if a symbol is in the market
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
                Adds keys to the bought dictionary for all symbols
                and sets them to 'OUT'.
        """

        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'
        return bought
    ###下面这个function是这个策略的核心###
    def calculate_signals(self, event):
        """
        Generates a new set of signals based on the MAC
        SMA with the short window crossing the long window
        meaning a long entry and vice versa for a short entry.

        Parameters
        event - A MarketEvent object.
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars_values(
                    s, "adj_close", N=self.longWindow
                )
                bar_date = self.bars.get_latest_bar_datetime(s)
                if bars is not None and bars !=[]:
                    shortSma = np.mean(bars[-self.shortWindow:])
                    longSma = np.mean(bars[-self.longWindow:])

                    symbol = s
                    dt = datetime.datetime.utcnow()  #现在时刻
                    sigDir = ""

                    if shortSma > longSma and self.bought[s] == "OUT":
                        print("LONG: %s" % bar_date)
                        sig_dir = 'LONG'

                        ##找下signalEvent的class啥意思
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        ##events put 是什么意思？
                        #put 把这个signal event加到event query里面
                        self.events.put(signal)
                        self.bought[s] = 'LONG'
                    elif shortSma < longSma and self.bought[s] == "LONG":
                        print("SHORT: %s" % bar_date)
                        sig_dir = 'EXIT'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'OUT'

if __name__ == "__main__":
    csv_dir = os.path.abspath('/home/dawei/Desktop/Quant/quantstart/algo-ebook-full-source-code-20150618/Data/')  # CHANGE THIS!
    symbol_list = ['AAPL']
    initial_capital = 10000
    heartBeat = 0.0
    startDate = datetime.datetime(2016, 1, 1, 0, 0, 0)

    backtest = Backtest(
        csv_dir, symbol_list, initial_capital, heartBeat,
        startDate, HistoricCSVDataHandler, SimulatedExecutionHandler,
        Portfolio, MovingAverageCrossStrategy
    )
    '''

    execute backtesting

    '''
    backtest.simulate_trading()