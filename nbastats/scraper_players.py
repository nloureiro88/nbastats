import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import requests
import ipdb
from bs4 import BeautifulSoup


NEW_COLS = ['Position', 'Birthdate', 'Birthplace', 'Height', 'Weight',
            'Status', 'Agent', 'Highschool', 'HsLocation', 'DraftEntry',
            'DraftEarly', 'Drafted', 'PreDraftTeam', 'Photo']


def scrape_player(pid):
    ''' Get data for each player '''

    url = f'https://basketball.realgm.com/player/a/Summary/{pid}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    box = soup.find(class_="profile-box")

    if box:
        position_info = box.select('h2 > span')
        if position_info:
            position = box.select('h2 > span')[0].text
        else:
            position = None

        birthdate_info = box.find("strong", string="Born:")
        if birthdate_info:
            birthdate = birthdate_info.parent.find('a').text
        else:
            birthdate = None

        birthplace_info = box.find("strong", string="Birthplace/Hometown:")
        if birthplace_info:
            birthplace = birthplace_info.parent.find('a').text
        else:
            birthplace = None

        size_info = box.find("strong", string="Height:")
        if size_info:
            size = size_info.parent.text.split()
            height, weight = size[1], size[4]
        else:
            height, weight = None, None

        nba_status_info = box.find("strong", string="Current NBA Status:")
        if nba_status_info:
            nba_status = nba_status_info.parent.text.split(":")[1].strip()
        else:
            nba_status = None

        agent_info = box.find("strong", string="Agent:")
        if agent_info:
            agent = agent_info.parent.find('a').text
        else:
            agent = None

        hs_info = box.find("strong", string="High School:")
        if hs_info:
            hs = hs_info.parent
            highschool = hs.find('a').text
            hslocation = hs.text.split('[')[1].strip(']')
        else:
            highschool = None
            hslocation = None

        draft_entry_info = box.find("strong", string="Draft Entry:")
        if draft_entry_info:
            draft_entry = draft_entry_info.parent.text
        else:
            draft_entry = None

        draft_early_info = box.find("strong", string="Early Entry Info:")
        if draft_early_info:
            draft_early = draft_early_info.parent.find('a').text
        else:
            draft_early = None

        drafted_info = box.find("strong", string="Drafted:")
        if drafted_info:
            drafted = drafted_info.parent.text
        else:
            drafted = None

        predraft_team_info = box.find("strong", string="Pre-Draft Team:")
        if predraft_team_info:
            link = predraft_team_info.parent.find('a')
            if link:
                predraft_team = predraft_team_info.parent.find('a').text
            else:
                predraft_team = predraft_team_info.parent.text
        else:
            predraft_team = None

        photo = box.find('img', src=True)['src']

        data = {'Position': position,
                'Birthdate': birthdate,
                'Birthplace': birthplace,
                'Height': height,
                'Weight': weight,
                'Status': nba_status,
                'Agent': agent,
                'Highschool': highschool,
                'HsLocation': hslocation,
                'DraftEntry': draft_entry,
                'DraftEarly': draft_early,
                'Drafted': drafted,
                'PreDraftTeam': predraft_team,
                'Photo': photo}
        return data

    return None


def get_players():
    ''' Get list of all players with stats '''

    stats_df = pd.read_csv('raw_data/stats_clean.csv')
    df = stats_df[['Id', 'Player']].drop_duplicates()
    df.reset_index(inplace=True)
    df.drop(columns="index", inplace=True)

    return df


def scrape_run(min_id=None):
    ''' Run scraper '''

    if min_id:
        df = pd.read_csv('raw_data/players.csv', low_memory=False)
    else:
        df = get_players()
        for col in NEW_COLS:
            df[col] = np.nan

    for index, row in df.iterrows():
        pid = int(row['Id'])
        if pid >= min_id:
            print(f'> Scraping player #{pid} ({round(index/df.shape[0] * 100, 2)}%)!')
            info = scrape_player(pid)
            target_cols, target_info = list(info.keys()), list(info.values())
            df.loc[index, target_cols] = np.array(target_info)
            save_raw_data(df)

    print('Scraping done!')

    return df


def save_raw_data(df):
    ''' Save to raw_data folder '''

    path = f'raw_data/players.csv'
    df.to_csv(path, index=False)
    print('Saved!')


if __name__ == '__main__':
    scrape_run(94629)
