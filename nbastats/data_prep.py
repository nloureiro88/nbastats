import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scraper_seasons import STATS_DICT


def concat_stats_data():
    ''' Concatenate all scraped data properly '''

    ncaa = pd.read_csv('raw_data/ncaa.csv')
    gl = pd.read_csv('raw_data/gleague.csv')
    it = pd.read_csv('raw_data/international.csv')
    nba = pd.read_csv('raw_data/nba.csv')

    # ncaa['Competition'] = 'NCAA'
    # gl['Competition'] = 'G-League'
    # it['Competition'] = 'International'
    # nba['Competition'] = 'NBA'

    df = pd.concat([ncaa, gl, it, nba])
    df.sort_values(by=['Id', 'Season'], inplace=True)
    df.reset_index(inplace=True)
    df.drop(columns=['level_0', 'Link'], inplace=True)

    df.to_csv('raw_data/stats.csv', index=False)
    print('Saved!')

    return df


def convert_stats_columns(df):
    ''' Convert misc / advanced columns to numerics '''

    cols = STATS_DICT['Misc_Stats'] + STATS_DICT['Advanced_Stats']
    integer_cols = ['DDBL', 'TDBL', '40PTS', '20REB', '20AST', '5STL',
                    '5BLK', 'HIGHGAME', 'TECHS', 'W-S', 'L-S']

    for stat in cols:
        if stat in integer_cols:
            df[stat] = df[stat].astype(int)
        else:
            df[stat] = df[stat].astype(float)

    return df


def prepare_stats_data():
    ''' Process basic cleaning actions on all stats data '''

    df = concat_stats_data()
    # df = pd.read_csv('raw_data/stats.csv', low_memory=False)

    # df["Team"].fillna("Unknown", inplace=True)
    df.drop(columns=['index'], inplace=True)
    df.replace('-', None, inplace=True)

    df.to_csv('raw_data/stats_clean.csv', index=False)
    print('Saved!')

    # return convert_stats_columns(df)
    return df


def prepare_players_data():
    ''' Process basic cleaning actions on all player data '''

    df = pd.read_csv('raw_data/players.csv', low_memory=False)

    df['PreDraftTeam'] = df['PreDraftTeam'].map(lambda x: x.replace('Pre-Draft Team: ', '') \
                                                           .replace(' (Jr)', '') \
                                                           .replace(' (Fr)', '') \
                                                           .replace(' (Sr)', '') \
                                                           .replace(' (OR)', '') \
                                                           .replace(' ()', '') \
                                                          if type(x) != float else x)

    df['Drafted'] = df['Drafted'].map(lambda x: x.replace('Drafted: ', '') if type(x) != float else x)
    df['DraftEntry'] = df['DraftEntry'].map(lambda x: x.replace('Draft Entry: ', '') if type(x) != float else x)

    df.to_csv('raw_data/players_clean.csv', index=False)
    print('Saved!')

    # return convert_stats_columns(df)
    return df


def prepare_all_data():
    stats_df = prepare_stats_data()
    players_df = prepare_players_data()
    return stats_df, players_df


if __name__ == '__main__':
    prepare_all_data()
