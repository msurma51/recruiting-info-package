# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 15:31:06 2023

@author: surma
"""

import pandas as pd
import os

main_file = '..\\data\\ESPN\\espn_master.csv'
year_strings = [str(year) for year in range(2010,2020)]
season_dfs = []
fpath_format = '..\\data\\ESPN\\recruiting_ESPN_{}.csv'
for year in year_strings:
    season_dfs.append(pd.read_csv(fpath_format.format(year), index_col = 0))
master_df = pd.concat(season_dfs).drop_duplicates()
master_df.reset_index(inplace = True)   
master_df_prev = pd.read_csv(main_file, index_col = 0)
master_df_prev = master_df_prev[:-1].copy()
master_df_prev['city'] = master_df['city']
master_df_prev.to_csv(main_file)
