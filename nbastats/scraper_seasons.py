import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import requests
import ipdb
from bs4 import BeautifulSoup


COMPETITIONS = ['nba', 'ncaa', 'jleague', 'international']

SEASONS = range(2005, 2021)

STATS_BASIC = ['Id', 'Player', 'Link', 'Competition', 'Team', 'Season', 'GP', 'MIN']

STATS_DICT = {'Totals': ['FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%',
                         'FTM', 'FTA', 'FT%', 'TOV', 'PF', 'ORB',
                         'DRB', 'REB', 'AST', 'STL', 'BLK', 'PTS'],

              'Misc_Stats': ['DDBL', 'TDBL', '40PTS', '20REB', '20AST',
                             '5STL', '5BLK', 'HIGHGAME', 'TECHS', 'HOB',
                             'AST/TO', 'STL/TO', 'FT/FGA', 'W-S', 'L-S',
                             'WIN%', 'OWS', 'DWS', 'WS'],

              'Advanced_Stats': ['TS%', 'EFG%', 'TOTALS%', 'ORB%', 'DRB%',
                                 'TRB%', 'AST%', 'TOV%', 'STL%', 'BLK%',
                                 'USG%', 'PPS', 'ORTG', 'DRTG', 'EDIFF',
                                 'FIC', 'PER']}


def create_dataframe(totals=True, misc_stats=False, advanced_stats=False):
    ''' Create an empty dataframe for the data '''
    cols = STATS_BASIC

    if totals:
        cols = cols + STATS_DICT['Totals']

    if misc_stats:
        cols = cols + STATS_DICT['Misc_Stats']

    if advanced_stats:
        cols = cols + STATS_DICT['Advanced_Stats']

    return pd.DataFrame(columns=cols)


def get_totals(compet, season, info):
    ''' Get a dict with totals info '''

    link = info[1].find('a', href=True)['href']
    data = {'Id': int(link.split("/")[-1]),
            'Player': info[1].text,
            'Link': link,
            'Competition': compet.upper(),
            'Team': info[2].text,
            'Season': season,
            'GP': info[3].text,
            'MIN': info[4].text,
            'FGM': info[5].text,
            'FGA': info[6].text,
            'FG%': info[7].text,
            '3PM': info[8].text,
            '3PA': info[9].text,
            '3P%': info[10].text,
            'FTM': info[11].text,
            'FTA': info[12].text,
            'FT%': info[13].text,
            'TOV': info[14].text,
            'PF': info[15].text,
            'ORB': info[16].text,
            'DRB': info[17].text,
            'REB': info[18].text,
            'AST': info[19].text,
            'STL': info[20].text,
            'BLK': info[21].text,
            'PTS': info[22].text}
    return data


def get_misc_stats(info):
    ''' Get a dict with misc_stats info '''

    data = {'DDBL': info[3].text,
            'TDBL': info[4].text,
            '40PTS': info[5].text,
            '20REB': info[6].text,
            '20AST': info[7].text,
            '5STL': info[8].text,
            '5BLK': info[9].text,
            'HIGHGAME': info[10].text,
            'TECHS': info[11].text,
            'HOB': info[12].text,
            'AST/TO': info[13].text,
            'STL/TO': info[14].text,
            'FT/FGA': info[15].text,
            'W-S': info[16].text,
            'L-S': info[17].text,
            'WIN%': info[18].text,
            'OWS': info[19].text,
            'DWS': info[20].text,
            'WS': info[21].text}
    return data


def get_advanced_stats(info):
    ''' Get a dict with advanced_stats info '''

    data = {'TS%': info[3].text,
            'EFG%': info[4].text,
            'TOTALS%': info[5].text,
            'ORB%': info[6].text,
            'DRB%': info[7].text,
            'TRB%': info[8].text,
            'AST%': info[9].text,
            'TOV%': info[10].text,
            'STL%': info[11].text,
            'BLK%': info[12].text,
            'USG%': info[13].text,
            'PPS': info[14].text,
            'ORTG': info[15].text,
            'DRTG': info[16].text,
            'EDIFF': info[17].text,
            'FIC': info[18].text,
            'PER': info[19].text}
    return data


def add_to_row(df, pid, season, competition, stype, info):
    ''' Add info to the respective dataframe row '''

    new_df = df.copy()
    target_cols, target_info = list(info.keys()), list(info.values())
    mask = (new_df.Id == pid) & (new_df.Season == season) & (new_df.Competition == competition.upper())
    new_df.loc[mask, target_cols] = np.array(target_info)
    return new_df


def scrape_data(df, competition, season, universe, stype):
    ''' Collect data from the origin '''

    page = 1
    next_page = True

    while next_page:
        if competition == 'nba':
            url = f'https://basketball.realgm.com/nba/stats/{season}/{stype}/{universe}/points/All/desc/{page}/Regular_Season'
        elif competition == 'ncaa':
            url = f'https://basketball.realgm.com/ncaa/stats/{season}/{stype}/{universe}/All/Season/All/points/desc/{page}/'
        elif competition == 'gleague':
            url = f'https://basketball.realgm.com/dleague/stats/{season}/{stype}/{universe}/points/All/desc/{page}/Regular_Season'
        elif competition == 'international':
            url = f'https://basketball.realgm.com/international/stats/{season}/{stype}/{universe}/All/points/All/desc/{page}/Regular_Season'

        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.select('table.tablesaw.compact > tbody > tr')

        if rows:
            for row in rows:
                info = row.find_all('td')
                player_id = int(info[1].find('a', href=True)['href'].split("/")[-1])

                if stype == 'Totals':
                    row_data = get_totals(competition, season, info)
                    df = df.append(row_data, ignore_index=True)

                elif stype == 'Misc_Stats':
                    row_data = get_misc_stats(info)
                    df = add_to_row(df, player_id, season, competition, stype, row_data)

                elif stype == 'Advanced_Stats':
                    row_data = get_advanced_stats(info)
                    df = add_to_row(df, player_id, season, competition, stype, row_data)


            page += 1

        else:
            next_page = False

    return df


def scrape_run(competition='nba', universe='All', totals=True, misc_stats=True, advanced_stats=True):
    ''' Run scraper '''

    df = create_dataframe(totals=totals, misc_stats=misc_stats, advanced_stats=advanced_stats)
    rows = 0

    for season in SEASONS:
        print(f'Scraping season {season}!')

        for stype in STATS_DICT.keys():
            print(f'> Getting {stype}...')

            # Calling the scrape_data function
            df = scrape_data(df, competition, season, universe, stype)

        new_rows = df.shape[0] - rows
        rows = df.shape[0]
        print(f'> New {new_rows} rows added, total of {rows}.')

    print('Scraping done!')

    df.sort_values(by=['Id', 'Season'], inplace=True)
    df.reset_index(inplace=True)
    return df


def save_raw_data(df, filename):
    ''' Save to raw_data folder '''

    path = f'raw_data/{filename}.csv'
    df.to_csv(path, index=False)
    print('Saved!')


if __name__ == '__main__':
    competition = 'international'
    save_raw_data(scrape_run(competition=competition), competition)
