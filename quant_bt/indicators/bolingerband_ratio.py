import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Use the 'Agg' backend


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


def plot(indicator_values):
    plt.plot(indicator_values['top3'], color='teal', label='Upper 3')
    plt.plot(indicator_values['top2'], color='teal',
             alpha=0.8, label='Upper 2')
    plt.plot(indicator_values['top1'], color='teal',
             alpha=0.6, label='Upper 1')
    plt.plot(indicator_values['bott1'], color='teal',
             alpha=0.6, label='Lower 1')
    plt.plot(indicator_values['bott2'], color='teal',
             alpha=0.8, label='Lower 2')
    plt.plot(indicator_values['bott3'], color='teal', label='Lower 3')
    plt.plot(indicator_values['sma'], 'r+', label='SMA')
    plt.fill_between(range(len(
        indicator_values['sma'])), indicator_values['bott3'], indicator_values['top3'], color='navy', alpha=0.5)
    plt.legend()
    plt.title("Bollingers Bands Fibonacci ratios")
    plt.show()


if __name__ == "__main__":
    lst_close = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    val = indicator(lst_close, period=20)
    plot(val)
