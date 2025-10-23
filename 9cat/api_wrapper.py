import sys, os
root_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(root_dir)

from espn_api.basketball import League
from espn_api.basketball.constant import NINE_CAT_STATS
from typing import List
import pandas as pd
from datetime import date, timedelta

class LeagueWrapper:
    def __init__(self, league_id : int, s2 : str, swid : str, year : int, sortOrder : str, end_date : date = None):
        if sortOrder not in ["average", "projected", "last 7", "last 15", "last 30"]:
            raise "Unknown Filter"
        self.today = date.today()
        self.end_date = None
        if not end_date or end_date < self.today:
            self.end_date = self.first_sunday()
        else:
            self.end_date = end_date
            
        self.league = League(league_id=league_id, year=year, espn_s2=s2, swid=swid, debug=False)
        self.sortOrder = sortOrder
        self.base_player_dataframe = self.build_player_df(self.sortOrder)
        #dataframe of scores, list of tuple containing matchups
        (self.scoreboard, self.matchups) = self.get_scoreboard()

    
    def build_player_df(self, sortOrder : str):
        # builds rostered players first
        free_agents = self.league.free_agents(size=200)
        teams = self.league.teams

        columns = ['Player Name', 'Player ID', 'Team', 'Team ID'] + list(NINE_CAT_STATS) + ['Expected Games']
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
                    dates = [entry['date'].date() for entry in player.schedule.values()]
                    if not player.schedule:
                        print(player.name)
                    expected_games = self.calculate_num_games(dates)
                
                player_data['Expected Games'] = expected_games

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
                dates = [entry['date'].date() for entry in fa.schedule.values()]
                expected_games = self.calculate_num_games(dates)
            
            player_data['Expected Games'] = expected_games

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
    
    def first_sunday(self):
        days_until_sunday = (6 - self.today.weekday()) % 7
        return self.today + timedelta(days=days_until_sunday)
    
    def calculate_num_games(self, dates : List[date]):
        if not dates:
            return 0 
        
        start = self.today
        end = self.end_date
        return sum(1 for d in dates if start <= d <= end)