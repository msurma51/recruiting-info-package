# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 05:47:41 2023

@author: surma
"""

import pandas as pd
import subprocess as sp
import os
from namespace import league_path

unmatched_file = os.path.join(league_path,'espn_unmatched.csv')
df_unmatched = pd.read_csv(unmatched_file, index_col = 0)
while (df_unmatched['searched'] == False).any():
    try:
        proc = sp.run(['python','espn_add_unmatched.py'], text=True)
    except:
        df_unmatched = pd.read_csv(unmatched_file, index_col = 0)

