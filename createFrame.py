from datetime import timedelta
import datetime
import pandas as pd
import os
import itertools
from itertools import combinations_with_replacement

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


def schedule_start_date(year, month, day, desired_start: list):
    #three options:
        #from today, from tomorrow, from next monday represented by 3-array
    assert sum(desired_start) == 1  
    if year == 0:
        date_obj = datetime.datetime.now()
    else:
        date_obj = datetime.datetime(year, month, day)
    dates = []
    if desired_start[0] == 1:
        start_range = 0
        end_range = 7 - date_obj.weekday()
    elif desired_start[1] == 1:
        start_range = 1
        end_range = 8 - (date_obj + timedelta(1)).weekday()
    else: 
        start_range =  7 - date_obj.weekday()
        end_range = start_range + 7
    for i in range(start_range, end_range):
        dates.append(date_obj.date() + timedelta(i))
    return dates

def csv_to_pandas(option : list, year=0, month=0, day=0): #date in format "%Y-%m-%d"
    #check if file already exists
    if year == 0:
        date = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        if month < 10:
            month2 = f"0{str(month)}"
        date = f"{year}-{month2}-{day}"
    if os.path.exists(date):
        print("csv already exists")
        return date
    log = pd.read_csv("filtered_schedule.csv")
    gamedays = schedule_start_date(year, month, day, option)

    week_data = []
    #meanwhile, create empty return dataframe
    df = pd.DataFrame(columns = ['Name'])
    for days in gamedays:
        all_games_in_day = log.loc[log['GameDate'] == days.strftime("%Y-%m-%d")]
        if all_games_in_day.empty:
            continue
        else:
            df[days.strftime("%Y-%m-%d")] = ""
            day_dictionary = {}
            for i in all_games_in_day.index:
                one = all_games_in_day[' Visitor'][i]
                two = all_games_in_day[' Home'][i]
                day_dictionary.update({one : two})
        week_data.append(day_dictionary)
    for team in sorted(teams):
        team_data = [team]
        for weekday in week_data:
            opponent = "---"
            for key in weekday:
                if key == team:
                    opponent = "xxx"
                    break
                elif weekday[key] == team:
                    opponent = "xxx"
                    break
            team_data.append(opponent)
        df.loc[len(df)] = team_data
    df.to_csv(f'{date}.csv', index=False)
    return date

def calculate_days(keep_list : list, df):
    vect = []
    for i in range(len(df.columns) - 1):
        value = 0
        for team in keep_list:
            if df[df["Name"] == team][df.columns[i + 1]].values[0] != "---":
                value += 1
        if value >= 10:
            vect.append(10)
        else:
            vect.append(value)
    return vect

def join_df(first_filename, later_filename):
    if not os.path.exists(f'{first_filename}.csv') or not os.path.exists(f'{later_filename}.csv'): 
        return None

    df1 = pd.read_csv(f'{first_filename}.csv')
    df2 = pd.read_csv(f'{later_filename}.csv')
    df2 = df2.drop(df2.columns[0], axis=1)

    df3 = pd.concat([df1, df2], axis=1)
    
    df3.to_csv(f'combined.csv', index=False)

def combination(limit : int, day_count : int, swaps : list):
    n = len(swaps)
    objects = [1, 0]
    combinations = list(itertools.product(objects, repeat=n))

    
    if min(limit, 10 - day_count) < n:
        return [x for x in combinations if sum(x) <= limit]

    return combinations

