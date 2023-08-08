from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
matplotlib.use('TkAgg')  # Use the 'Agg' backend


def plot(dates, indicator_values):
    # Convert ISO 8601 datetime strings to datetime objects
    datetime_objects = [datetime.fromisoformat(date_str) for date_str in dates]

    # Plot the indicator values starting from the 20th period
    start_index = 20  # Change this index to adjust the starting point
    datetime_objects = datetime_objects[start_index:]
    indicator_values = {key: values[start_index:]
                        for key, values in indicator_values.items()}

    # Format x-axis as dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M:%S%z'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()

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
    plt.xticks(rotation=45)
    plt.show()
