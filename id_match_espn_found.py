# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 13:05:17 2022

@author: surma
"""
import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import pandas as pd
import numpy as np
from espn_match_func import comp_score_espn_found, pos_mapper
from namespace import league_path
pd.set_option('display.max_columns', None)

def test_edge_session():
    service = EdgeService(executable_path=EdgeChromiumDriverManager().install())

    driver = webdriver.Edge(service=service)

    driver.quit()
    
driver = webdriver.Edge(service=EdgeService(executable_path=EdgeChromiumDriverManager().install()))
driver.implicitly_wait(10)
lougle = '{} {} football'

match_file = os.path.join(league_path,'espn_unmatched.csv')
search_file = os.path.join(league_path,'espn_found.csv')
df_match = pd.read_csv(match_file, index_col = 0)
df_search = pd.read_csv(search_file, index_col= 0)

for col in ('found_match','not_found_match'):
    if col not in df_match.columns:
        df_match[col] = False
if 'comp_score_found' not in df_match.columns:
    df_match['comp_score_found'] = np.NaN
df_unmatched = df_match[(df_match['found'] == True) & 
                        (df_match['found_match'] == False) & 
                        (df_match['not_found_match'] == False)].copy()
df_search[['college_recruited','position']] = df_search[['college_recruited','position']].fillna('')
if 'pos' not in df_search.columns:
    df_search['pos'] = df_search['position'].map(pos_mapper)
for col2 in ('player_id', 'comp_score'):
    if col2 not in df_search.columns:
        df_search[col2] = np.NaN
df_find_id = df_search[df_search['player_id'].isna()]

# Loop through the players in df_match and identify the best matches from df_search
for index, row in df_unmatched.iterrows():
    df_rank = df_find_id.copy()
    df_rank['comp_score'] = df_rank.apply(comp_score_espn_found, axis=1, args=(row,))
    # Handle the easy "no's" automatically
    max_score = df_rank['comp_score'].max()
    match_dex = None    
    if max_score < 150.0:
        match_dex = -1
    df_rank = df_rank.sort_values('comp_score', ascending = False)
    if max_score > 250.0 and df_rank.iloc[0]['season'] > 2019:
        match_dex = 0
    if match_dex == None:
        url = 'https://www.google.com/'
        driver.get(url)

        try:
            search_box = driver.find_element(By.CLASS_NAME,"gLFyf")
            search_box.send_keys(lougle.format(row['full_name'], row['team']))
            search_box.send_keys('\t')
            lougle_it = driver.find_elements(By.NAME, "btnK")[1]
            lougle_it.click()
        except:
            print('Player search failed')
            
        print(row[['full_name','college_recruited','current_eligible_year', 
                   'season_position','height','weight']])
        print(df_rank.iloc[:8][['name','team','season','previous_school',
                                'pos','ht.','wt.','comp_score']])
        match_input = input('Which row is a match? Enter 1-8, or 0 for no match')
        while match_dex not in [-1,*list(range(5))]:
            try:
                match_dex = int(match_input)-1
                if match_dex < -1 or match_dex > 7:
                    match_dex = None
                    match_input = input('Try again. Enter 1-8, 0 for no match')
                    continue
            except:
                match_input = input('Try again. Enter 1-8, or 0 for no match')
    if match_dex > -1:
        match_row = df_rank.iloc[match_dex]
        print('{} matched with player id {}'.format(match_row['name'],row['player_id']))
        df_search.at[match_row.name,'player_id'] = row['player_id']
        df_search.at[match_row.name,'comp_score'] = match_row['comp_score']
        df_match.at[index,'found_match'] = True
        df_match.at[index,'comp_score_found'] = match_row['comp_score']
    else:
        df_match.at[index,'not_found_match'] = True
        df_match.at[index,'comp_score_found'] = df_rank.iloc[0]['comp_score']
    df_find_id = df_search[df_search['player_id'].isna()]
    df_search.to_csv(search_file)
    df_match.to_csv(match_file)
    