# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 13:05:17 2022

@author: surma
"""
import pandas as pd
import numpy as np
import os
from espn_match_func import comp_score_espn
from namespace import league_path
pd.set_option('display.max_columns', None)

match_file = os.path.join(league_path,'recruits.csv')
search_file = os.path.join('..\\data\\ESPN','espn_master.csv')
df_match = pd.read_csv(match_file, index_col = 0)
df_search = pd.read_csv(search_file, index_col = 0)

df_match['match_espn'] = df_match['player_id'].isin(df_search['player_id'])
if 'unmatched_espn' not in df_match.columns:
    df_match['unmatched_espn'] = False
df_unmatched = df_match[(df_match['match_espn'] == False) & (df_match['unmatched_espn'] == False)].copy()
df_find_id = df_search[df_search['player_id'].isna()]

# Loop through the players in df_match and identify the best matches from df_search
for index, row in df_unmatched.iterrows():
    try:
        df_rank = df_find_id.copy()
        if row['current_eligible_year'] > 0:
            min_year = row['current_eligible_year'] - 6
            max_year = row['current_eligible_year'] - 2
            df_rank = df_rank[(df_rank['season'] >= min_year) & (df_rank['season'] <= max_year)]
            assert min_year < 2020, 'No potential matches before 2020' 
        df_rank['comp_score'] = df_rank.apply(comp_score_espn, axis=1, args=(row,))
        max_score = df_rank['comp_score'].max()
        df_rank = df_rank.sort_values('comp_score', ascending = False)
        if max_score > 250.0 and df_rank.iloc[1]['comp_score'] < 165.0:
            match_dex = 0
        else:
            print(row[['full_name','current_eligible_year', 'season_position',
                       'college_recruited','height','weight','hometown_id']])
            print(df_rank.iloc[:5][['name','team','season','previous_school','pos','ht.','wt.',
                                    'hometown_id.x','hometown_id.y', 'comp_score']])
            match_input = input('Which row is a match? Enter 1-5, or 0 for no match')
            match_dex = None
            while match_dex not in [-1,*list(range(5))]:
                try:
                    match_dex = int(match_input)-1
                    if match_dex < -1 or match_dex > 4:
                        match_dex = None
                        match_input = input('Try again. Enter 1-5, 0 for no match')
                        continue
                except:
                    match_input = input('Try again. Enter 1-5, or 0 for no match')
        assert match_dex > -1, 'No match found'
        match_row = df_rank.iloc[match_dex]
        print('{} matched with player id {}'.format(match_row['name'],row['player_id']))
        df_search.at[match_row.name,'player_id'] = row['player_id']
        df_search.at[match_row.name,'comp_score'] = match_row['comp_score']
        df_match.at[index,'match_espn'] = True
    except Exception as e:
        print(e)
        df_match.at[index,'unmatched_espn'] = True
        df_match.at[index,'comp_score'] = max_score
    df_find_id = df_search[df_search['player_id'].isna()]
    df_search.to_csv(search_file)
    df_match.to_csv(match_file)
    