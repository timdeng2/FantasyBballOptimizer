from datetime import datetime, timedelta
import requests
import os
from collections import defaultdict
import pandas as pd
import json

teams = [
    "MIN",
    "NYK",
    "CLE",
    "TOR",
    "DET",
    "HOU",
    "IND",
    "MIL",
    "CHA",
    "DEN",
    "POR",
    "PHX",
    "DAL",
    "UTA",
    "MIA",
    "LAC",
    "CHI",
    "PHI",
    "SAS",
    "MEM",
    "BKN",
    "NOP",
    "BOS",
    "OKC",
    "ORL",
    "GSW",
    "SAC",
    "WAS",
    "ATL",
    "LAL"
    ]
def schedule_to_csv(relative_path : str, year: int):
    year_num = year + 1
    year = str(year)
    url =f'https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/' + year + '/league/00_full_schedule.json'
    print(url)
    r = requests.get(url)
    if r.status_code == 200:
        json_data = r.json()

        current_dt = datetime.now() 
        path = os.path.join(relative_path, f"Schedules/Total/{year_num}_schedule.csv")
        f = open(path, "w")
        f.writelines('GameDate, GameID, Visitor, Home')
        for i in range(len(json_data['lscd'])):
            for j in range(len(json_data['lscd'][i]['mscd']['g'])):
                gamedate = json_data['lscd'][i]['mscd']['g'][j]['gdte']
                gamedate_dt = datetime.strptime(gamedate, "%Y-%m-%d")
                #access only unplayed games
                if (gamedate_dt >= current_dt):  
                    game_id = json_data['lscd'][i]['mscd']['g'][j]['gid']
                    visiting_team = json_data['lscd'][i]['mscd']['g'][j]['v']['ta']
                    home_team = json_data['lscd'][i]['mscd']['g'][j]['h']['ta'] 
                    f.write('\n' + gamedate +','+ game_id +','+ visiting_team +','+ home_team)

                #json is not sorted chronologically as games after the new year are placed first before the 
                #december games, easiest to rearrange manually.
        f.close()
    else:
        print(r.json())
        print(f"Error: Could not create schedule / Status Code: {r.status_code}")


def csv_to_team_dates(csv_path, json_path):
    # Read the CSV
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    # Use defaultdict to accumulate dates
    team_dates = defaultdict(list)
    
    # Iterate over each row
    for _, row in df.iterrows():
        date = row['GameDate']
        visitor = row['Visitor']
        home = row['Home']
        
        team_dates[visitor].append(date)
        team_dates[home].append(date)
    
    # Convert defaultdict to regular dict
    team_dates = dict(team_dates)
    
    # Write to JSON file
    with open(json_path, 'w') as f:
        json.dump(team_dates, f, indent=4)

def schedule_start_date(desired_start: list):
    #three options:
        #from today, from tomorrow, from next monday represented by 3-array
    assert sum(desired_start) == 1  
    dates = []
    if desired_start[0] == 1:
        start_range = 0
        end_range = 7 - datetime.now().weekday()
    elif desired_start[1] == 1:
        start_range = 1
        end_range = 8 - (datetime.now() + timedelta(1)).weekday()
    else: 
        start_range =  7 - datetime.now().weekday()
        end_range = start_range + 7
    for i in range(start_range, end_range):
        dates.append(datetime.now().date() + timedelta(i))
    return dates