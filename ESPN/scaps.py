import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import os
# from pywebcopy import save_website
# from pywebcopy import save_webpage
# import pywebcopy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from selenium import webdriver
import statistics


mapper ={'Phx' : "PHX", 'Phi' : "PHI", 
         'Det' : "DET", 'Sac' : "SAC", 'LAC' : "LAC", 'Cle' : "CLE", 'Bos' : "BOS", 'Hou' : "HOU", 
         'Mia' : "MIA", 'Tor' : "TOR", 'SA' : "SAS", 'Dal' : "DAL", 'Ind' : "IND", 'Orl' : "ORL", 
         'Den' : "DEN", 'Bkn' : "BKN", 'Wsh' : "WAS", 'NO' : "NOP", 'Chi' : "CHI", 'Por' : "POR", 
         'Utah' : "UTA", 'OKC' : "OKC", 'Cha' : "CHA", 'GS' : "GSW", 'NY' : "NYK", 
         'Mil' : "MIL", 'Min' : "MIN", 'LAL' : "LAL", 'Atl' : "ATL", 'Mem' : "MEM"}

def my_team(login, password0):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging']) 

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get("https://fantasy.espn.com/basketball/league?leagueId=1893541148")
    time.sleep(0.5)
    driver.switch_to.frame("oneid-iframe")
    inputt = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div/div[2]/div/div/form/div[2]/div/input")))
    inputt.click()
    ActionChains(driver).send_keys(login).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    password = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='InputPassword']")))
    password.click()
    password.clear()
    ActionChains(driver).send_keys(password0).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    time.sleep(0.5)
    driver.switch_to.default_content()
    my_team = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "View Roster")))
    my_team.click()
    driver.implicitly_wait(1)
    players_list = driver.find_elements(By.CLASS_NAME, "player__column")
    active = []
    injured = []
    for i in range(len(players_list)):
        if i != 0 and i != 14:
            active.append(players_list[i].get_attribute("title"))
        elif i == 14:
            injured.append(players_list[i].get_attribute("title"))

    teams_list = driver.find_elements(By.CLASS_NAME, "playerinfo__playerteam")
    teams = []
    injured_team = []
    for team in teams_list:
        teams.append(mapper[team.text])
    if len(teams) > 13:
        injured_team.append(teams[13])
        teams.pop()
    driver.quit()
    return (active, teams, injured, injured_team)

def get_free_agents(login, password0):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging']) 

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get("https://fantasy.espn.com/basketball/players/add?leagueId=1893541148")
    time.sleep(0.5)
    driver.switch_to.frame("oneid-iframe")
    inputt = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div/div[2]/div/div/form/div[2]/div/input")))
    inputt.click()
    ActionChains(driver).send_keys(login).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    password = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='InputPassword']")))
    password.click()
    password.clear()
    ActionChains(driver).send_keys(password0).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    driver.switch_to.default_content()
    #page1
    #driver.implicitly_wait(2)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div[2]/div/div/table[1]')))
    players_list1 = driver.find_elements(By.CLASS_NAME, "player-column__athlete")
    players_team1 = driver.find_elements(By.CLASS_NAME, "playerinfo__playerteam")
    tup1 = obtain_helper(driver, players_list1)
    players_list = [x.get_attribute("title") for x in players_list1]
    players_team = [x.text for x in players_team1]

    #page2
    next_page = driver.find_element(By.ID, "2")
    next_page.click()
    #driver.implicitly_wait(2.2)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div[2]/div/div/table[1]')))
    players_list1 = driver.find_elements(By.CLASS_NAME, "player-column__athlete")
    players_team1 = driver.find_elements(By.CLASS_NAME, "playerinfo__playerteam")
    tup2 = obtain_helper(driver, players_list1)
    players_list2 = [x.get_attribute("title") for x in players_list1]
    players_team2 = [x.text for x in players_team1]
    players_list.extend(players_list2)
    players_team.extend(players_team2)
    #page3
    next_page = driver.find_element(By.ID, "3")
    next_page.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="fitt-analytics"]/div/div[5]/div[2]/div[3]/div/div/div[2]/div/div/table[1]')))
    players_list1 = driver.find_elements(By.CLASS_NAME, "player-column__athlete")
    players_team1 = driver.find_elements(By.CLASS_NAME, "playerinfo__playerteam")
    tup3 = obtain_helper(driver, players_list1)
    players_list3 = [x.get_attribute("title") for x in players_list1]
    players_team3 = [x.text for x in players_team1]
    players_list.extend(players_list3)
    players_team.extend(players_team3)
    players_team_final = [mapper[x] for x in players_team]

    arr1 = tup1[0]
    arr2 = tup1[1]
    arr3 = tup1[2]
    arr1.extend(tup2[0])
    arr1.extend(tup3[0])
    arr2.extend(tup2[1])
    arr2.extend(tup3[1])
    arr3.extend(tup2[2])
    arr3.extend(tup3[2])

    data = {"Name" : players_list, "Team" : players_team_final, "Average" : arr2, "Last 5" : arr1, "SD" : arr3}
    df = pd.DataFrame(data)
    df.to_csv("free_agents.csv")


def obtain_helper(driver, players_list1):
    ftsy_data = []
    mean = []
    standard_dev = []
    #variance = []
    for ele in players_list1:
        print(ele.get_attribute("title"))
        ele.click()
        #driver.implicitly_wait(0.3)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "lightbox__closebtn")))
        #collect data
        inner_mean = 0
        n = 0
        vect = []
        x = driver.find_elements(By.CSS_SELECTOR, "tr.Table__TR--sm:not(.traded-separator)")
        for i in range(2, len(x)):
            tables = x[i].find_elements(By.CLASS_NAME, "Table__TD")
            if len(tables) != 10:
                continue
            data = tables[len(tables) - 1].text
            if data != "--":
                vect.append(int(data))
            else:
                vect.append(data)
            if data != "--":
                inner_mean += int(data)
                n += 1
        ftsy_data.append(tuple(vect))
        if n == 1:
            dat = [x for x in vect if x != "--"]
            mean.append(round(statistics.mean(dat), 2))
            standard_dev.append("--")
            #variance.append(0)
        elif n != 0:
            dat = [x for x in vect if x != "--"]
            mean.append(round(statistics.mean(dat), 2))
            standard_dev.append(round(statistics.stdev(dat), 2))
            #variance.append(round(statistics.variance(dat), 2))
        else:
            mean.append("--")
            standard_dev.append("--")
            #variance.append(0)
        exiting = driver.find_element(By.CLASS_NAME, "lightbox__closebtn")
        exiting.click()
    return (ftsy_data, mean, standard_dev)


def filter_df(average):
    if os.path.exists("free_agents.csv"):
        pass
    else: 
        return []
    df = pd.read_csv("free_agents.csv")
    df = df[df['Average'] != "--"]
    df = df[df['Dev'] != "--"]
    df['Dev'] = df['Dev'].astype(float)
    df['Average'] = df['Average'].astype(float)
    filter_df = df[(df['Average'] >= average) & (df['Dev'] <= 20)].reset_index(drop=True)
    filter_df = filter_df.drop(filter_df.columns[0], axis=1)
    filter_df = filter_df.sort_values(by='Average', ascending=False).reset_index(drop=True)
    filter_df = filter_df.sort_values(by='Team', ascending=True).reset_index(drop=True)
    filter_df.to_csv("filtered_agents.csv")
    result = df.groupby('Team').agg({'Average': 'max', 'Name': 'first'}).reset_index()
    result.to_csv("filtered_agents2.csv")
    return [x for x in list(mapper.values()) if (x not in filter_df['Team'].values)]
