# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 09:02:37 2022

@author: surma
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import pandas as pd
import numpy as np
import os
from add_prospect_247 import scrape_247
from namespace import league_path



def test_edge_session():
    service = EdgeService(executable_path=EdgeChromiumDriverManager().install())

    driver = webdriver.Edge(service=service)

    driver.quit()
    

match_file = os.path.join(league_path,'espn_merge.csv')
unmatched_file = os.path.join(league_path,'unmatched_247.csv')
search_file = os.path.join('..\\data\\247','recruiting_247_master.csv')
main_file = os.path.join(league_path,'found_247.csv')

df_match = pd.read_csv(match_file, index_col = 0)
df_search = pd.read_csv(search_file, index_col = 0)
team_map = df_search[['data.team', 'data.team_id']].copy()
team_map = team_map.drop_duplicates()
team_map = team_map.set_index('data.team', drop=True)

df_match['match_espn'] = df_match['player_id'].isin(df_search['PFF_ID'])
if os.path.exists(unmatched_file):
    df_unmatched = pd.read_csv(unmatched_file, index_col = 0)
else:
    df_unmatched = df_match.query('match_247 == False & season < 2020').copy()
    for field in ('searched', 'found'):
        df_unmatched[field] = False
    df_unmatched.to_csv(unmatched_file)
if not os.path.exists(main_file):
    df_main = pd.DataFrame(columns = df_search.columns)
    df_main.to_csv(main_file)

df_find = df_unmatched[df_unmatched['searched'] == False].copy()        

driver = webdriver.Edge(service=EdgeService(executable_path=EdgeChromiumDriverManager().install()))
driver.implicitly_wait(10)

for index, row in df_find.iterrows():
    try:
        search_year = int(row['season'])
        url = 'https://247sports.com/Season/{}-Football/Recruits/'.format(str(search_year))
        driver.get(url)
        name = row['full_name']
        name_section = driver.find_element(By.CLASS_NAME, "form-section")
        name_box = name_section.find_element(By.TAG_NAME, "input")
        name_box.send_keys(name)
        name_button = name_section.find_element(By.TAG_NAME, "button")
        name_button.click()
        results = driver.find_element(By.CLASS_NAME, "results")
        result_list = results.find_elements(By.CLASS_NAME, "name")
    except Exception as e:
        print(e)
        break
    df_unmatched.at[index,'searched'] = True 
    try:
        assert len(result_list) > 0, f'No search results found for {name}'
        for result in result_list:
            profile_button_1 = result.find_element(By.TAG_NAME, "a")
            profile_button_1.click() 
            try:
                profile_button_2 = driver.find_element(By.CLASS_NAME, "view-profile-link")
                profile_button_2.click()
            except:
                None
        scrape_247(driver, main_file, team_map)
        df_unmatched.at[index, 'found'] = True
    except Exception as e:
        print(e)
    df_unmatched.to_csv(unmatched_file)
    
driver.quit()
        
        
        

  
