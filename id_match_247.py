# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 16:01:12 2022

@author: surma
"""
import pandas as pd
import numpy as np
import os
from match_247_func import height_clean, comp_score_247
from namespace import league_path


match_file = os.path.join(league_path,'espn_merge.csv')
search_file = '..\\data\\247\\recruiting_247_master.csv'

# Initialize dataframes from filename inputs
df_search = pd.read_csv(search_file, index_col = 0)
df_search['data.height'] = df_search['data.height'].map(height_clean)
df_search['data.weight'].replace('-',0, inplace = True)
df_search['data.weight'] = df_search['data.weight'].astype('float64')
for col in ('data.hometown','data.previous_school','data.position'):
    df_search[col].fillna('', inplace = True)
df_match = pd.read_csv(match_file, index_col = 0)
for col in ('city', 'previous_school','pos'):
    df_match[col].fillna('', inplace = True)
df_match['match_247'] = df_match['player_id'].isin(df_search['PFF_ID'])
if 'no_match_247' not in df_match.columns:
    df_match['unmatched_247'] = False
df_unmatched = df_match[(df_match['match_247'] == False) & 
                        (df_match['unmatched_247'] == False)].copy()
df_find_id = df_search[df_search['PFF_ID'].isna()]

    
# Loop through the players in df_match and identify the best matches from df_search
for index, row in df_unmatched.iterrows():
    try:
        df_rank = df_find_id.copy()
        df_rank['season'] = df_rank['season'].astype(str).str.extract('(20\d{2})')
        df_rank['season'] = df_rank['season'].astype('int64')
        max_score = 0.0
        if row['current_eligible_year'] > 0:
            min_year = row['current_eligible_year'] - 6
            assert min_year < 2020, 'No potential matches before 2020'
            max_year = row['current_eligible_year'] - 2
            df_rank = df_rank[(df_rank['season'] >= min_year) & (df_rank['season'] <= max_year)]
            assert len(df_rank) > 0, 'No matches in range of seasons'
        df_rank['comp_score'] = df_rank.apply(comp_score_247, axis=1, args=(row,))
        df_rank = df_rank.sort_values('comp_score', ascending = False)   
        max_score = df_rank.iloc[0]['comp_score']
        if max_score > 450 and df_rank.iloc[1]['comp_score'] < 325:
            match_dex = 0
        elif max_score < 325:
            match_dex = -1
        else:
            print(row[['full_name','current_eligible_year', 'team', 'college_recruited',
                                    'previous_school','pos','ht.','wt.']])
            print(df_rank.iloc[:5][['data.player','season','data.previous_school',
                                    'data.position','data.height','data.weight','comp_score']])
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
        print('{} matched with player id {}'.format(match_row['data.player'],row['player_id']))
        df_search.at[match_row.name,'PFF_ID'] = row['player_id']
        df_search.at[match_row.name,'comp_score_247'] = match_row['comp_score']
        df_match.at[index,'match_247'] = True
    except Exception as e:
        print(e)
        df_match.at[index,'unmatched_247'] = True
        if max_score > 0.0:    
            df_match.at[index,'comp_score_247'] = max_score
    df_find_id = df_search[df_search['PFF_ID'].isna()]
    df_search.to_csv(search_file)
    df_match.to_csv(match_file)
        
        
    
    
    
    
    