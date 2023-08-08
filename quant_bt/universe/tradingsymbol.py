import pandas as pd


def symbols(filename):
    universe_df = pd.read_csv('data/' + filename)
    universe_df['disabled'] = universe_df['disabled'].astype('str')
    universe_df = universe_df[~(universe_df.disabled.str.upper() == 'Y')]
    universe_df = universe_df.drop(['disabled'], axis=1)
    return universe_df
