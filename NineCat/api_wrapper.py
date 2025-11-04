import sys, os
root_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(root_dir)


from create_schedule import schedule_to_csv, csv_to_team_dates
from espn_api.basketball import League
from espn_api.basketball.constant import NINE_CAT_STATS
from typing import List
import requests
import pandas as pd
import time
from datetime import date, datetime, timedelta

class LeagueWrapper:
    def __init__(self, league_id : int, s2 : str, swid : str, year : int, sortOrder : str, end_date : date = None):
        if sortOrder not in ["average", "projected", "last 7", "last 15", "last 30"]:
            raise "Unknown Filter"
        
        print("Fetching Schedule...")
        file_path = f"../Schedules/Team/{year}_schedule.json"

        if not os.path.exists(file_path):
            file_path2 = f"../Schedules/Total/{year}_schedule.csv"
            if not os.path.exists(file_path2):
                schedule_to_csv("../", year - 1)
                
            csv_to_team_dates(f"../Schedules/Total/{year}_schedule.csv", file_path)
        print("Schedule is loaded")



        self.today = date.today()
        self.end_date = None
        if not end_date or end_date < self.today:
            self.end_date = self.first_sunday()
        else:
            self.end_date = end_date

        print("Fetching ESPN API...")    
        self.league = League(league_id=league_id, year=year, espn_s2=s2, swid=swid, debug=False)
        self.sortOrder = sortOrder
        self.base_player_dataframe = self.build_player_df(self.sortOrder)
        #dataframe of scores, list of tuple containing matchups
        (self.scoreboard, self.matchups) = self.get_scoreboard()

        print("Initializing Images...")
        self.initialize_images()
        print("Finished Intitializing Images")

        self.build_percentile()

    def initialize_images(self):
        folder = "../PlayerHeadshots"
        ids = {os.path.splitext(f)[0] for f in os.listdir(folder) if f.endswith(".png")}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/118.0.5993.90 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        }

        for i, pid in enumerate(self.base_player_dataframe['Player ID']):
            if str(pid) not in ids:
                url = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/{pid}.png"
                save_path = f"{folder}/{pid}.png"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                elif response.status_code == 404:
                    print(f"❌ No current available image for {self.base_player_dataframe['Player Name'][i]}")
                else:
                    print(f"❌ Unknown Error while fetching for {self.base_player_dataframe['Player Name'][i]}'s headshot. Status code: {response.status_code}")
                time.sleep(0.1)


    
    def build_player_df(self, sortOrder : str):
        # builds rostered players first
        free_agents = self.league.free_agents(size=200)
        teams = self.league.teams

        positions = ['PG','SG','SF','PF','C']
        columns = ['Player Name', 'Player ID', 'Team', 'Team ID'] + list(NINE_CAT_STATS) + \
            ['FT%', 'FG%', 'Expected Games'] + positions + \
            [f"Expected {stat}" for stat in NINE_CAT_STATS] + ["ProTeam"] 
        player_df = pd.DataFrame(columns=columns)

        for team in teams:
            for player in team.roster:
                player_data = {
                    'Player Name' : player.name,
                    'Player ID' : player.playerId,
                    'Team' : team.team_name,
                    'Team ID' : team.team_id,
                }
                if sortOrder == "average":
                    for k, v in player.nine_cat_averages.items():
                        player_data[k] = v
                elif sortOrder == "projected":
                    for k, v in player.nine_cat_projected.items():
                        player_data[k] = v
                elif sortOrder == "last 7":
                    for k, v in player.nine_cat_last_7.items():
                        player_data[k] = v                    
                elif sortOrder == "last 15":
                    for k, v in player.nine_cat_last_15.items():
                        player_data[k] = v
                elif sortOrder == "last 30":
                    for k, v in player.nine_cat_last_30.items():
                        player_data[k] = v
                
                expected_games = 0
                if player.injuryStatus and player.injuryStatus != "OUT":
                    if player.schedule:
                        dates = [datetime.strptime(entry, "%Y-%m-%d").date() for entry in player.schedule]
                        expected_games = self.calculate_num_games(dates)
                
                player_data['FT%'] = round(
                    float(player_data['FTM'] / player_data['FTA']) if player_data['FTA'] != 0 else 0.0,
                    2
                )
                player_data['FG%'] = round(
                    float(player_data['FGM'] / player_data['FGA']) if player_data['FGA'] != 0 else 0.0,
                    2
                )
                player_data['Expected Games'] = expected_games
                for pos in positions:
                    if pos in player.eligibleSlots:
                        player_data[pos] = 1
                    else:
                        player_data[pos] = 0

                for stat in NINE_CAT_STATS:
                    player_data[f'Expected {stat}'] = round(float(player_data[stat]) * expected_games, 2)
                player_data["ProTeam"] = player.proTeam

                player_df.loc[len(player_df)] = player_data

        for fa in free_agents:
            player_data = {
                'Player Name' : fa.name,
                'Player ID' : fa.playerId,
                'Team' : "**Free Agent**",
                'Team ID' : -1,
            }
            if sortOrder == "average":
                for k, v in fa.nine_cat_averages.items():
                    player_data[k] = v
            elif sortOrder == "projected":
                for k, v in fa.nine_cat_projected.items():
                    player_data[k] = v
            elif sortOrder == "last 7":
                for k, v in fa.nine_cat_last_7.items():
                    player_data[k] = v                    
            elif sortOrder == "last 15":
                for k, v in fa.nine_cat_last_15.items():
                    player_data[k] = v
            elif sortOrder == "last 30":
                for k, v in fa.nine_cat_last_30.items():
                    player_data[k] = v

            expected_games = 0

            if fa.injuryStatus and fa.injuryStatus != "OUT":
                if fa.schedule:
                    dates = [datetime.strptime(entry, "%Y-%m-%d").date() for entry in fa.schedule]
                    expected_games = self.calculate_num_games(dates)

            player_data['FT%'] = round(
                float(player_data['FTM'] / player_data['FTA']) if player_data['FTA'] != 0 else 0.0,
                2
            )
            player_data['FG%'] = round(
                float(player_data['FGM'] / player_data['FGA']) if player_data['FGA'] != 0 else 0.0,
                2
            )
            player_data['Expected Games'] = expected_games
            for pos in positions:
                if pos in fa.eligibleSlots:
                    player_data[pos] = 1
                else:
                    player_data[pos] = 0

            for stat in NINE_CAT_STATS:
                player_data[f'Expected {stat}'] = round(float(player_data[stat]) * expected_games, 2)
            player_data["ProTeam"] = fa.proTeam

            player_df.loc[len(player_df)] = player_data
        
        return player_df
    

    def get_scoreboard(self):
        columns = ['Team', 'Team ID', 'Score'] + list(NINE_CAT_STATS)
        scoreboard = pd.DataFrame(columns=columns)
        opponents = []

        matchups = self.league.scoreboard()
        for matchup in matchups:
            home_data = {
                'Team' : matchup.home_team.team_name,
                'Team ID' : matchup.home_team.team_id,
                'Score' : matchup.home_team_live_score
            }
            for stat in list(NINE_CAT_STATS):
                home_data[stat] = matchup.home_team_cats[stat]['score']
            away_data = {
                'Team' : matchup.away_team.team_name,
                'Team ID' : matchup.away_team.team_id,
                'Score' : matchup.away_team_live_score
            }
            for stat in list(NINE_CAT_STATS):
                away_data[stat] = matchup.away_team_cats[stat]['score']
            
            scoreboard.loc[len(scoreboard)] = home_data
            scoreboard.loc[len(scoreboard)] = away_data
            opponents.append((matchup.home_team.team_id, matchup.away_team.team_id,))

            

        return scoreboard, opponents
    
    def build_percentile(self):
        rostered = self.base_player_dataframe[self.base_player_dataframe['Team ID'] != -1]

        cols = ['FT%','FG%','PTS','AST','REB','BLK','STL','TO','3PM']

        # For each stat, compute percentile ranks among rostered players
        for col in cols:
            # Map each player's value to its percentile
            # We use interpolation because not all players may exist in the rostered subset
            if col == 'TO':
                self.base_player_dataframe[f'{col}_percentile'] = round(self.base_player_dataframe[col].map(
                    lambda x: 
                    (rostered[col] >= x).sum() / len(rostered) * 100
                ), 2)
            else:
                self.base_player_dataframe[f'{col}_percentile'] = round(self.base_player_dataframe[col].map(
                    lambda x: 
                    (rostered[col] <= x).sum() / len(rostered) * 100
                ), 2)

    
    def first_sunday(self):
        days_until_sunday = (6 - self.today.weekday()) % 7
        return self.today + timedelta(days=days_until_sunday)
    
    def calculate_num_games(self, dates : List[date]):
        if not dates:
            return 0 
        
        start = self.today
        end = self.end_date
        return sum(1 for d in dates if start <= d <= end)