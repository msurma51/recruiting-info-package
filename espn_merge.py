# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 08:33:41 2022

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
from namespace import league_path
from espn_match_func import inner_comp_score
from add_prospect_espn import espn_update, espn_update_sr


def test_edge_session():
    service = EdgeService(executable_path=EdgeChromiumDriverManager().install())

    driver = webdriver.Edge(service=service)

    driver.quit()

recruit_file = os.path.join(league_path, 'recruits.csv')
match_file = os.path.join('..\\data\\ESPN','espn_master.csv')
update_file = os.path.join(league_path, 'espn_update.csv')
search_file = os.path.join(league_path, 'espn_unmatched.csv')
found_file = os.path.join(league_path, 'espn_found.csv')
merge_file = os.path.join(league_path, 'espn_merge.csv')

if os.path.exists(update_file):
    df_merge_recruit = pd.read_csv(update_file, index_col = 0)
else:    
    df_recruit = pd.read_csv(recruit_file, index_col = 0)
    df_match = pd.read_csv(match_file, index_col = 0)
    df_merge_recruit = df_recruit.merge(df_match, on = 'player_id')
    df_merge_recruit['comp_score_espn'] = df_merge_recruit.apply(inner_comp_score, axis = 1)
    df_merge_recruit['e.stars'] = np.NaN

driver = webdriver.Edge(service=EdgeService(executable_path=EdgeChromiumDriverManager().install()))
driver.implicitly_wait(10)
url = 'https://www.google.com/'
lougle = '{} {} {} espn recruiting'
df_update = df_merge_recruit[df_merge_recruit['e.stars'].isna()]
for index, row in df_update.iterrows():
    i = 1
    while i < 4:
        try:  
            driver.get(url)
            search_box = driver.find_element(By.CLASS_NAME,"gLFyf")
            search_box.send_keys(lougle.format(row['name'], row['team'], row['previous_school']))
            search_box.send_keys('\t')
            search_button = driver.find_elements(By.CLASS_NAME, "gNO89b")[1]
            search_button.click()
        except Exception as e:
            i += 1
            continue
        try:
            result_tag = driver.find_elements(By.CLASS_NAME, "MjjYud")[0]
            link_button = result_tag.find_element(By.TAG_NAME, "a")
            link_button.click()
            ser = espn_update(driver)
            for j in range(len(ser)):
                df_merge_recruit.at[index,ser.index[j]] = ser[j]
            df_merge_recruit.to_csv(update_file)
        except:
            None
        break

if os.path.exists(merge_file):
    df_merge = pd.read_csv(merge_file, index_col = 0)
else:
    df_search = pd.read_csv(search_file, index_col = 0)
    df_search['comp_score_espn'] = df_search['comp_score_found']
    cols_to_drop = [col for col in df_search if col not in df_recruit and
                    col != 'comp_score_espn']
    df_search = df_search.drop(cols_to_drop, axis = 1)
    df_found = pd.read_csv(found_file, index_col = 0)
    df_merge_found = df_search.merge(df_found, on = 'player_id')
    
    df_merge = pd.concat((df_merge_recruit,df_merge_found))
    df_merge.drop(['comp_score_x','comp_score_y'], axis = 1, inplace=True)
    df_merge.reset_index(drop = True, inplace = True)
if 'sr_updated' not in df_merge.columns:
    df_merge['sr_updated'] = False
has_sr = df_merge[(df_merge['e.scouting_report'].str.len() > 20) &
                  (df_merge['sr_updated'] == False)]
for index, row in has_sr.iterrows():
    i = 1
    while i < 4:
        try:  
            driver.get(url)
            search_box = driver.find_element(By.CLASS_NAME,"gLFyf")
            search_box.send_keys(lougle.format(row['name'], row['team'], row['previous_school']))
            search_box.send_keys('\t')
            search_button = driver.find_elements(By.CLASS_NAME, "gNO89b")[1]
            search_button.click()
        except Exception as e:
            i += 1
            continue
        try:
            result_tag = driver.find_elements(By.CLASS_NAME, "MjjYud")[0]
            link_button = result_tag.find_element(By.TAG_NAME, "a")
            link_button.click()
            df_merge.at[index, 'e.scouting_report'] = espn_update_sr(driver)
        except:
            None
        df_merge.at[index, 'sr_updated'] = True
        df_merge.to_csv(merge_file)
        break
    
