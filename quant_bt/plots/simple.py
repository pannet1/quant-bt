import finplot as fplt


def Plot(title, ohlc, lst_plot_data):
    ax1 = fplt.create_plot(title)
    for plot_data in lst_plot_data:
        fplt.plot(plot_data, legend=plot_data.name.upper(), ax=ax1)
    fplt.candlestick_ochl(ohlc)
    fplt.show()
