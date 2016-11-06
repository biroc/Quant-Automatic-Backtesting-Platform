#!/usr/bin/python
# -*- coding: utf-8 -*-

# performance.py

#Author Dawei Wang
#Nov 4 2016

'''

Calculating Sharp Ration and Max Drawdown/Duration
Based on return/pnl

'''
from __future__ import print_function

import numpy as np
import pandas as pd


#Sharp Ratio based on returns
def create_sharpe_ratio(returns, periods=252):
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

def create_drawdowns(pnl):
    """
        Calculate the largest peak-to-trough drawdown of the PnL curve
        as well as the duration of the drawdown. Requires that the
        pnl_returns is a pandas Series.

        Parameters:
        pnl - A pandas Series representing period percentage returns.

        Returns:
        drawdown, duration - Highest peak-to-trough drawdown and duration.
    """

    # Calculate the cumulative returns curve
    # and set up the High Water Mark
    hwm = [0]

    idx = pnl.index
    drawdown = pd.Series(index = idx)
    duration = pd.Series(index = idx)

    for t in range(1, len(idx)):
        hwm.append(max(hwm[t-1], pnl[t]))
        drawdown[t] = (hwm[t] - pnl[t])
        duration[t] = (0 if drawdown[t] == 0 else duration[t-1]+1)

    return drawdown, drawdown.max(),duration.max()

