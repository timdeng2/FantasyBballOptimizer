from datetime import datetime, timedelta
import requests

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
def schedule_to_csv(year: str):
    r = requests.get('https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/' + year + '/league/00_full_schedule.json')
    json_data = r.json()

    current_dt = datetime.datetime.now() 
    # prepare output files
    fout = open("filtered_schedule.csv", "w")
    fout.writelines('GameDate, GameID, Visitor, Home')
    for i in range(len(json_data['lscd'])):
        for j in range(len(json_data['lscd'][i]['mscd']['g'])):
            gamedate = json_data['lscd'][i]['mscd']['g'][j]['gdte']
            gamedate_dt = datetime.datetime.strptime(gamedate, "%Y-%m-%d")
            #access only unplayed games
            if (gamedate_dt >= current_dt):  
                game_id = json_data['lscd'][i]['mscd']['g'][j]['gid']
                visiting_team = json_data['lscd'][i]['mscd']['g'][j]['v']['ta']
                home_team = json_data['lscd'][i]['mscd']['g'][j]['h']['ta'] 
                fout.write('\n' + gamedate +','+ game_id +','+ visiting_team +','+ home_team)
            #json is not sorted chronologically as games after the new year are placed first before the 
            #december games, easiest to rearrange manually.
    fout.close()
    r.close()

#schedule_to_csv("2023")

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