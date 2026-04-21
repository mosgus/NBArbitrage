'''
    NBA.py = parent script for nba_api data collection

    Gets Data for:
    - last season: 2024-25
    - current season: 2025-26

    gus
'''

import os
import datetime
import time
import pandas as pd
import random

from nba_api.stats.endpoints import leaguedashteamstats

# --- THE HEADERS FIX ---
# This makes your script look like a real browser to avoid being blocked
headers = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# const
path = "../data"
today = datetime.date.today()
seasons = ["2024-25", "2025-26"]




def get_teams_adv(season, retries=3):
    print(f"Grabbing advanced stats for {season}...")

    # Folder Logic (Done before the request so it's ready)
    dir_path = os.path.join(path, season, "teams")
    os.makedirs(dir_path, exist_ok=True)
    filename = os.path.join(dir_path, f"adv_stats_{season.replace('-', '_')}.csv")

    for attempt in range(retries):
        try:
            # We add a small random delay before each attempt to vary request timing
            time.sleep(random.uniform(1.5, 3.5))

            data_request = leaguedashteamstats.LeagueDashTeamStats(
                season=season,
                measure_type_detailed_defense='Advanced',
                season_type_all_star='Regular',
                headers=headers,
                timeout=60  # Bumped to 60 seconds because NBA servers are slow
            )
            data = data_request.get_data_frames()[0]

            if data.empty:
                raise ValueError("Dataframe is empty")

            data['DATA_RETRIEVED'] = today.strftime('%Y-%m-%d')
            data.to_csv(filename, index=False)
            print(f"Successfully saved {season} data.")
            return data

        except Exception as e:
            wait_time = (attempt + 1) * 10
            print(f"Attempt {attempt + 1} failed for {season}: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"All {retries} attempts failed for {season}.")
                return None

if __name__ == "__main__":
    last_season_df = get_teams_adv(seasons[0])
    time.sleep(2)
    current_season_df = get_teams_adv(seasons[1])

    if current_season_df is not None:
        print("\n--- Current Season Snapshot (Top 5 Teams) ---")
        top_teams = current_season_df[['TEAM_NAME', 'OFF_RATING', 'DEF_RATING', 'NET_RATING']].sort_values(
            by='NET_RATING', ascending=False)
        print(top_teams.head())