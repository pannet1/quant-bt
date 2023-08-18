import finplot as fplt


def Plot(title, ohlc, lst_plot_data):
    """
    lst = [symbol_data['top2'], symbol_data['top1'], symbol_data['sma'],
           symbol_data['bott1'], symbol_data['bott2']]
    Plot(symbol, symbol_data[['Open', 'Close', 'High', 'Low']], lst)
    """
    ax1 = fplt.create_plot(title)
    for plot_data in lst_plot_data:
        fplt.plot(plot_data, legend=plot_data.name.upper(), ax=ax1)
    fplt.candlestick_ochl(ohlc)
    fplt.show()
