import pandas as pd


def symbols(full_path):
    universe_df = pd.read_csv(full_path)
    universe_df['disabled'] = universe_df['disabled'].astype('str')
    universe_df = universe_df[~(universe_df.disabled.str.upper() == 'Y')]
    universe_df = universe_df.drop(['disabled'], axis=1)
    return universe_df
