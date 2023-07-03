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
from add_prospect_espn import espn_scrape
from namespace import league_path



def test_edge_session():
    service = EdgeService(executable_path=EdgeChromiumDriverManager().install())

    driver = webdriver.Edge(service=service)

    driver.quit()
    

match_file = os.path.join(league_path,'recruits.csv')
unmatched_file = os.path.join(league_path,'espn_unmatched.csv')
search_file = os.path.join('..\\data\\ESPN','espn_master.csv')
main_file = os.path.join(league_path,'espn_found.csv')
lougle = '{} {} espn recruiting'

df_match = pd.read_csv(match_file, index_col = 0)
df_search = pd.read_csv(search_file, index_col = 0)
df_match['match_espn'] = df_match['player_id'].isin(df_search['player_id'])
if os.path.exists(unmatched_file):
    df_unmatched = pd.read_csv(unmatched_file, index_col = 0)
else:
    df_unmatched = df_match[df_match['match_espn'] == False].copy()
    for field in ('searched', 'found'):
        df_unmatched[field] = False
    df_unmatched.to_csv(unmatched_file)

df_find = df_unmatched[df_unmatched['searched'] == False].copy()        

driver = webdriver.Edge(service=EdgeService(executable_path=EdgeChromiumDriverManager().install()))
driver.implicitly_wait(10)

for index, row in df_find.iterrows():
    try:
        url = 'https://www.google.com/'
        driver.get(url)
        search_box = driver.find_element(By.CLASS_NAME,"gLFyf")
        search_box.send_keys(lougle.format(row['full_name'], row['team']))
        search_box.send_keys('\t')
        search_button = driver.find_elements(By.CLASS_NAME, "gNO89b")[1]
        search_button.click()
    except Exception as e:
        break
    df_unmatched.at[index,'searched'] = True 
    try:
        result_tag = driver.find_elements(By.CLASS_NAME, "MjjYud")[0]
        link_button = result_tag.find_element(By.TAG_NAME, "a")
        link_button.click()
        espn_scrape(driver, main_file)
        df_unmatched.at[index, 'found'] = True
    except:
        None
    df_unmatched.to_csv(unmatched_file)
    
driver.quit()
        
        
        

  
