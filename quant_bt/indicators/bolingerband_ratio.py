import numpy as np


def indicator(lst_close, *args, **kwargs):
    fibratio1 = 1.618
    fibratio2 = 2.618
    fibratio3 = 4.236
    # Sample price data (replace this with your actual price data)
    period = kwargs.get('period', 20)

    # Calculate SMA
    sma = np.convolve(lst_close, np.ones(period)/period, mode='valid')

    # Calculate ATR
    atr = np.mean(np.abs(np.diff(lst_close)))

    # Calculate Fibonacci levels
    r1 = atr * fibratio1
    r2 = atr * fibratio2
    r3 = atr * fibratio3

    top3 = sma + r3
    top2 = sma + r2
    top1 = sma + r1
    bott1 = sma - r1
    bott2 = sma - r2
    bott3 = sma - r3
    return {
        'top3': top3,
        'top2': top2,
        'top1': top1,
        'bott1': bott1,
        'bott2': bott2,
        'bott3': bott3,
        'sma': sma
    }
