#!/usr/bin/python
# -*- coding: utf-8 -*-

# data.py

#Author Dawei Wang
#Nov 3 2016
from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime
import os, os.path

import numpy as np
import pandas as pd

from event import MarketEvent

class DataHandler(object):

    #Read CSV data, convert to set of bars(OHLCVI)
    # Using abc, so the following function can be used for all sub class
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bar(self, symbol):

        raise NotImplementedError("Should implement get_latest_bar()")

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars updated.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_datetime()")

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_value()")

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        raise NotImplementedError("Should implement get_latest_bars_values()")

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol
        in a tuple OHLCVI format: (datetime, open, high, low,
        close, volume, open interest).
        """
        raise NotImplementedError("Should implement update_bars()")


# 写 DataHandler's subclass to read CSV
#上面的DataHandler里面的function 用abstractmethod
#装饰过，下面的subclass要定义一样的function
#function 被call的时候，parent class和subclass function的内容都会被返回

class HistoricCSVDataHandler(DataHandler):
    def __init__(self, events, csv_dir, symbols_list):
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbols_list

        self.symbol_data = {}#返回的dictionary
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.bar_index = 0
        #读csv file
        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        #对symbol list里的美一只股票读csv data, convert to dictionary
        #Dictionary的key是股票名称
        #Dictionary的value是pd df形式的data
        #Dictionary的名字是self.symbol_data

        comb_index = None

        for s in self.symbol_list:
            self.symbol_data[s] = pd.io.parsers.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % s),
                header=0, index_col=0, parse_dates=True,
                names=[
                    'datetime', 'open', 'high',
                    'low', 'close', 'volume', 'adj_close'
                ]
            ).sort()
            ###把所有股票的index放在一起
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []
        #ReIndex by pad Method
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(
                index=comb_index, method='pad'
            )
            #看下returns columns 给的是什么
            print(self.symbol_data[s]["adj_close"].pct_change())
            self.symbol_data[s]["returns"] = self.symbol_data[s]["adj_close"].pct_change()
            #看下他为什么要返回iterrows的pair模式
            #print(self.symbol_data[s].iterrows())
            self.symbol_data[s] = self.symbol_data[s].iterrows()

    #用yield 来返回每个新的bar
    def _get_new_bar(self,symbol):
        for b in self.symbol_data[symbol]:
            yield b

    def get_latest_bar(self, symbol):

        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1][0]

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return getattr(bars_list[-1][1], val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])

    #这个很重要，每一个heartbeat更新一次bart,用marketevent 做trigger
    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        ###Event是queue，读新的一个数据，添加一个marketevent到trigger里
        self.events.put(MarketEvent())