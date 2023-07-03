# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 05:47:41 2023

@author: surma
"""

import pandas as pd
import subprocess as sp
import os
from namespace import league_path

unmatched_file = os.path.join(league_path,'unmatched_247.csv')
log_dir = os.path.join(league_path, 'logs')
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_file = os.path.join(log_dir, 'unmatched_247_looper_log.txt')
df_unmatched = pd.read_csv(unmatched_file, index_col = 0)
while (df_unmatched['searched'] == False).any():
    try:
        proc = sp.run(['python','add_unmatched_247.py'], capture_output = True, text = True)
        with open(log_file, 'a') as outfile:
            outfile.write(proc.stderr)
    except:
        None    
    df_unmatched = pd.read_csv(unmatched_file, index_col = 0)

