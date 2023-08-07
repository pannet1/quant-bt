import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Use the 'Agg' backend


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
