# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 08:02:36 2023

@author: surma
"""
import os

league = input('Which league are you matching for?')
#league = 'ACC'
league_fstring = '_'.join(league.split())
league_path = os.path.join('..\\data', league_fstring.upper())
if not os.path.exists(league_path):
    os.makedirs(league_path)
with open('league_path.txt', 'w') as outfile:
    outfile.write(league_path)