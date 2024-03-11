from datetime import datetime, timedelta
import time
import pandas as pd
import os 
import pickle
import createFrame
import copy
import itertools
import random

def group(df): #returns sets of teams playing (today!!)  
    df = df[df.iloc[:, 1] == "xxx"]

    sorted_df = df.sort_values(by=list(df.columns[1:len(df.columns)-1]), ascending=False).reset_index(drop=True)
    #print(sorted_df)
    labels = sorted_df["Name"]
    sorted_df = sorted_df.drop("Name", axis=1)
    total = []
    vector = []
    for i in range(len(sorted_df)):
        if i != len(sorted_df) - 1:
            if sorted_df.iloc[i].equals(sorted_df.iloc[i+1]):
                vector.append(labels.iloc[i])
            else:
                vector.append(labels.iloc[i])
                total.append(vector) 
                vector = []
        else:
            vector.append(labels.iloc[i])
            total.append(vector)          
    return total

import dtree

def construct(acq_limit : int, matchup_acq : int, teams_list : list, is_playn : bool, df, swap_df):
    
    if is_playn:
        value = 1
    else:
        value = 0

    tree = dtree.Node(matchup_acq, value, teams_list)

    if matchup_acq == acq_limit or swap_df.shape[1] == 1: #base case
        return tree
   
    tmp_df = swap_df.drop(swap_df.columns[1], axis=1)

    matchup_acq2 = matchup_acq + 1
    for team in group(swap_df):
        is_playn2 = False
        if swap_df[swap_df["Name"] == team[0]][swap_df.columns[1]].values[0] != "---":
            is_playn2 = True
        df2 = df.drop(df.columns[1], axis=1)
        tmp_tree = construct(acq_limit, matchup_acq2, team, is_playn2, df2, tmp_df)
        tree.add_swap_list(tmp_tree)

    is_playn3 = False
    # print(teams_list)
    # print(df)
    if df[df["Name"] == teams_list[0]][df.columns[1]].values[0] != "---":
        is_playn3 = True
    df = df.drop(df.columns[1], axis=1)
    tmp_tree2 = construct(acq_limit, matchup_acq, teams_list, is_playn3, df, tmp_df)
    tree.add_swap_list(tmp_tree2)
    return tree

def get_leaf_nodes(tree, vect2 : list, vect3 : list, days : int):
    if len(tree.swap) == 0 or (tree.swap)[0] == None:
        for i in range(days - len(vect2)):
            vect2.append(0)
            vect3.append(-1)
        return [(tree.matchup_acquisitions, vect2, vect3)]
    
    vect = []
    for i in range(len(tree.swap)):
        tmp_vect = copy.deepcopy(vect2)
        tmp_vect2 = copy.deepcopy(vect3)
        tmp_vect.append(tree.swap[i].value)
        tmp_vect2.append(i)
        vect.extend(get_leaf_nodes(tree.swap[i], tmp_vect, tmp_vect2, days))
    return vect


def numeric_combos(matchup_limit : int, matchup_used : int, n : int): #given n trees, find combinations of f from 0 to matchup_limit:
    range_list = [x for x in range(matchup_limit + 1)] 
    combinations = list(itertools.product(range_list, repeat=n))
    vect = []
    for i in list(combinations):
        if sum(i) == matchup_limit + (n * matchup_used) - matchup_used:
            less = False
            for x in i:
                if x < matchup_used:
                    less = True
                    break
            if not less:
                vect.append(i)
    return vect


def group_by_first_element(tuples_list):
    grouped_dict = {}
    for tpl in tuples_list:
        key = tpl[0]
        if key in grouped_dict:
            grouped_dict[key].append(tpl)
        else:
            grouped_dict[key] = [tpl]
    return grouped_dict

def calculate_max(big_list : list, keep_list : list): #given list of n lists and our keep_max_list
    x = combinations_without_repeats(big_list)
    length = len(keep_list)
    zero = [0 for i in range(length)]
    curr_max = 0
    track = []
    
    for tup_comb in x:
        zero_internal = copy.deepcopy(zero)
        for tup in tup_comb:
            zero_internal = [x + y for x, y in zip(zero_internal, tup[1])]
        total = [ i + j for i, j in zip(zero_internal, keep_list)]
        for p in range(length):
            if total[p] > 10:
                total[p] = 10
        this = sum(total)
        if this > curr_max:
            curr_max = this
            track.clear()
            track.append(tup_comb)
        elif this == curr_max:
            track.append(tup_comb)

    return (curr_max, track)


def combinations_without_repeats(lists):
    if not lists:
        return [[]]
    first, *rest = lists
    combinations_rest = combinations_without_repeats(rest)
    result = []
    for elem in first:
        for combination in combinations_rest:
            if elem not in combination:
                result.append([elem, *combination])
    return result

def perms(list_of_tuples_list, matchup_limit : int, matchup_used : int, keep_list : list):
    n = len(list_of_tuples_list)
    if n == 0:
        return []
    
    nums = numeric_combos(matchup_limit, matchup_used, n)
    keys = group_by_first_element(list_of_tuples_list[0]).keys()

    for tupp_combo in nums:
        for elem in tupp_combo:
            if elem not in keys:
                nums.remove(tupp_combo)
    storage = []
    for pair in nums: #tuple combo
        big_list = []
        for idx in range(n):
            smaller_list = group_by_first_element(list_of_tuples_list[idx])[pair[idx]]
            big_list.append(smaller_list)
        storage.append(calculate_max(big_list, keep_list))
        print("done")
    curr_max = 0
    for element in storage:
        if element[0] > curr_max:
            curr_max = element[0]

    filtered_storage = [x for x in storage if x[0] == curr_max]

    return filtered_storage

def get_advice(path, dates, swappables): #path is tuples
    df = pd.read_csv("filtered_agents2.csv")

    extract = []
    for i in path: 
        extract.append(i[2])
    file_names = []
    for j in swappables:
        file_names.append(j[0])
    
    idx = 0
    advices = []
    for filen in file_names:
        advice = []
        with open(f"{filen}.pkl", 'rb') as fff:
            baby = pickle.load(fff)
            path = extract[idx]
            curr = baby.matchup_acquisitions
            for p in range(len(path)):
                choice = path[p]
                baby = baby.swap[choice]
                if baby.matchup_acquisitions != curr:
                    advice.append(baby.teams)
                else:
                    advice.append([])
                curr = baby.matchup_acquisitions
        idx += 1
        advices.append(advice)
    
    idx2 = 0
    for date in dates:
        print(f"On {date}\n---------------")
        for n in range(len(advices)):
            # if idx2 == 0:
            print(f"Player {n} ({file_names[n]})", end = " ")
            # else:
            #     player = df.loc[df['Team'] == file_names[n], 'Name'].iloc[0]
            #     print(f"Player {n} ({player})", end = " ")
            if len(advices[n][idx2]) == 0:
                print("should do nothing")
            else:
                vect = []
                vect2 = []
                for i in range(len(advices[n][idx2])):
                    player1 = df.loc[df['Team'] == (advices[n][idx2])[i], 'Name'].iloc[0]
                    vect.append(player1)
                    vect2.append((advices[n][idx2])[i])
                file_names[n] = vect2
                print(f"should swap to one of these teams: {vect2} {vect} (+1)")
        idx2 += 1


def final(matchup_limit, matchup_used, year, month, day, swappables, keep_list, removals):
    start_time = time.time()
    print("started")

    string = createFrame.csv_to_pandas([1,0,0], year, month, day)
    dataframe = pd.read_csv(f'{string}.csv')

    y = createFrame.calculate_days(keep_list, dataframe)
    #print(y)
    swapframe = dataframe.copy()

    for remove in removals:
        swapframe = swapframe[swapframe['Name'] != remove]
        
    print(f"new dataframe: {swapframe['Name'].values}")
 
    #just the first team is needed
    with open(f'{swappables[0][0]}.pkl', 'wb') as outp:
        baby = construct(matchup_limit, matchup_used, swappables[0], True, dataframe, swapframe)
        pickle.dump(baby, outp, pickle.HIGHEST_PROTOCOL)
        print("part tree done")

    for idx, ele in enumerate(swappables):
        if idx == 0:
            continue
        else:
            with open(f'{swappables[0][0]}.pkl', 'rb') as ff:
                copy = pickle.load(ff)
                head = copy
                df2 = dataframe.copy()
                for p in range(dataframe.shape[1] - 1):
                    if p != 0:
                        if df2[df2["Name"] == ele[0]][df2.columns[1]].values[0] != "---":
                            head.value = 1
                        else:
                            head.value = 0
                        df2 = df2.drop(df2.columns[1], axis=1)
                    head.teams = ele
                    head = head.swap[len(head.swap) - 1]
                head.teams = ele
                if df2[df2["Name"] == ele[0]][df2.columns[1]].values[0] != "---":
                    head.value = 1
                else:
                    head.value = 0
                with open(f'{ele[0]}.pkl', 'wb') as outp:
                    pickle.dump(copy, outp, pickle.HIGHEST_PROTOCOL)
    print("finished tree construction")

    filenames = []
    for j in swappables:
        name = f"{j[0]}.pkl"
        filenames.append(name)

    list_of_tuples_list = []
    for fname in filenames:
        with open(fname, 'rb') as f:
            baby = pickle.load(f)
            tuples_list = get_leaf_nodes(baby,[], [], dataframe.shape[1] - 1)
            list_of_tuples_list.append(tuples_list)

    with open('tree.pkl', 'wb') as ff:
        perm = perms(list_of_tuples_list, matchup_limit, matchup_used, y)
        pickle.dump(perm, ff, pickle.HIGHEST_PROTOCOL)
        print("Sample\n------------------------------")
        column_names = list(dataframe.columns)
        column_names.pop(0)
        get_advice(perm[0][1][0], column_names, swappables)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

def generate_random(dates, swappables):
      with open('tree.pkl', 'rb') as ff:
        baby = pickle.load(ff)
        print(f"MAX {baby[0][0]}")
        length = len(baby)
        x = random.randrange(0, length)
        internal_length = len(baby[x][1])
        y = random.randrange(0, internal_length)
        get_advice(baby[x][1][y], dates, swappables)


def calculate_perms():
    with open('tree.pkl', 'rb') as ff:
        summ = 0
        baby = pickle.load(ff)
        length = len(baby)
        for i in range(length):
            for j in range(len(baby[i][1])):
                summ += 1
    return summ

# with open(f"TOR.pkl", 'rb') as fff:
#     baby = pickle.load(fff)

# test_keep = ["SAC", "MIN", "ORL", "SAC", "HOU", "PHI", "SAS", "TOR", "CHA", "CLE"]
# swappables = [['TOR'], ['DET'], ['CHA']]
# # #final(8, 3, 2024, 2, 22, swappables, test_keep)
# df = pd.read_csv("2024-02-26.csv")
# x = list(df.columns)
# x.pop(0)
# generate_random(x, swappables)
# print(calculate_perms())
# with open('TOR.pkl', 'rb') as ff:
#     copy = pickle.load(ff)
#     head = copy
#     for p in range(7):
#         head.teams = ["DET"]
#         head = head.swap[len(head.swap) - 1]
#     head.teams = ["DET"]
#     with open(f'DET.pkl', 'wb') as outp:
#         pickle.dump(copy, outp, pickle.HIGHEST_PROTOCOL)
