from .api_wrapper import LeagueWrapper
import numpy as np

class FantasyPage:
    def __init__(self, league_id : int, s2 : str, swid : str, year : int, sortOrder : str = "total"):
        leagueWrapper = LeagueWrapper(league_id, s2, swid, year, sortOrder)
        self.player_dataframe = leagueWrapper.base_player_dataframe
        self.scoreboard = leagueWrapper.scoreboard
        self.matchups = leagueWrapper.matchups

    # def get_projected_score(self, matchup : tuple) -> tuple:
    #     away = 0.0
    #     home = 0.0
    #     for category in ['3PM','AST','BLK','PTS','REB','STL','TO']:
    #         stat1 = self.get_projected_stat(category, matchup[0])
    #         stat2 = self.get_projected_stat(category,  matchup[1])
    #         if stat1 > stat2:
    #             if category == "TO":
    #                 home += 1.0
    #             else:
    #                 away += 1.0
    #         elif stat1 == stat2:
    #             away += 0.5 
    #             home += 0.5
    #         else:
    #             if category == "TO":
    #                 away += 1.0
    #             else:
    #                 home += 1.0
    #     for category in ['FG%','FT%']:
    #         stat1 = self.get_projected_percentage_stat(category, matchup[0])[2]
    #         stat2 = self.get_projected_percentage_stat(category, matchup[1])[2]
    #         if stat1 > stat2:
    #             away += 1.0
    #         elif stat1 == stat2:
    #             away += 0.5 
    #             home += 0.5
    #         else:
    #             home += 1.0

    #     return (away, home)

    # def get_score(self, team_id : int) -> float:
    #     df = self.scoreboard[self.scoreboard['Team ID'] == team_id]
    #     return df['Score'].iloc[0]

    # def get_team_name(self, team_id : int) -> str:
    #     df = self.scoreboard[self.scoreboard['Team ID'] == team_id]
    #     return df['Team'].iloc[0]


    # def get_current_stat(self, category : str, team_id : int) -> float:
    #     assert category in ['3PM','AST','BLK','PTS','REB','STL','TO','FGM','FGA','FTM','FTA']
    #     df = self.scoreboard[self.scoreboard['Team ID'] == team_id]
    #     return round(float(df[category].iloc[0]),2)

    # def get_current_percentage_stat(self, category : str, team_id : int) -> str:
    #     assert category in ['FG%', 'FG%']
    #     if category == 'FG%':
    #         fm = self.get_current_stat('FGM', team_id)
    #         fa = self.get_current_stat('FGA', team_id)
    #     else:
    #         fm = self.get_current_stat('FTM', team_id)
    #         fa = self.get_current_stat('FTA', team_id)      
    #     return f"{round((fa / fm), 2) if fm != 0.0 else 0.0}%"     


    # def get_projected_stat(self, category : str, team_id : int) -> float:
    #     assert category in ['3PM','AST','BLK','PTS','REB','STL','TO']
    #     df = self.player_dataframe[self.player_dataframe['Team ID'] == team_id]
    #     return self.get_current_stat(category, team_id) + \
    #         round(float(np.round((df[category] * df['Expected Games']).sum())),2)


    # def get_projected_percentage_stat(self, category : str, team_id : int) -> tuple: # (made, attempted, percentage)
    #     assert category in ['FG%', 'FT%']
    #     df = self.player_dataframe[self.player_dataframe['Team ID'] == team_id]
    #     if category == 'FG%':
    #         total_shots_attempt = self.get_current_stat('FGA', team_id) + \
    #             round(float(np.round(df['FGA'] * df['Expected Games']).sum()),5)
    #         total_shots_made = self.get_current_stat('FGM', team_id) + \
    #             round(float(np.round(df['FGM'] * df['Expected Games']).sum()),5)
    #         percentage = round((total_shots_made / total_shots_attempt),5) if total_shots_attempt != 0.0 else 0.0
    #         return (total_shots_made, total_shots_attempt, percentage)
    #     else:
    #         total_shots_attempt = self.get_current_stat('FTA', team_id) + \
    #             round(float(np.round(df['FTA'] * df['Expected Games']).sum()),5)
    #         total_shots_made = self.get_current_stat('FTM', team_id) + \
    #             round(float(np.round(df['FTM'] * df['Expected Games']).sum()),5)
    #         percentage = round((total_shots_made / total_shots_attempt),5) if total_shots_attempt != 0.0 else 0.0
    #         return (total_shots_made, total_shots_attempt, percentage)