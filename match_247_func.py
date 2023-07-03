# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 07:58:35 2023

@author: surma
"""

from fuzzywuzzy import fuzz
from espn_match_func import name_score, height_dist_score, weight_dist_score

def height_clean(height_info):
    if isinstance(height_info,str):
        height_list = height_info.split()
        return float(height_list[-1])
    else:
        return height_info
    
def height_fix(height_float):
    if height_float < 100.0:
        feet = height_float // 10
        inches = height_float % 10
        return feet*100 + inches
    else:
        return height_float
    
def comp_score_247(entry_search, entry_match):
    score = name_score(entry_match['full_name'], entry_match['first_name'], 
                             entry_match['last_name'], entry_search['data.player'])
    alt_name_score = fuzz.ratio(entry_match['name'],entry_search['data.player'])*2
    if alt_name_score > score:
        score = alt_name_score
    score += height_dist_score(entry_match['ht.'], entry_search['data.height']) 
    score += weight_dist_score(entry_match['wt.'], entry_search['data.weight'])
    score += fuzz.ratio(entry_match['city'], entry_search['data.hometown'])
    score += fuzz.ratio(entry_match['previous_school'], entry_search['data.previous_school'])
    if entry_match['pos'] == entry_search['data.position']:
        return score + 50
    return score

def pos_mapper(position_247):
    if any(('DE' in position_247, 'OLB' in position_247, position_247 == 'Edge')):
        return 'ED'
    elif 'LB' in position_247:
        return 'LB'
    if position_247 in ('DL', 'DT'):
        return 'DI'
    if position_247.startswith('O'):
        return position_247[1]
    if position_247 == 'IOL':
        return 'G'
    if position_247 == 'ATH':
        return 'WR'
    if position_247 in ('RB','APB'):
        return 'HB'
    if position_247 in ('PRO', 'DUAL'):
        return 'QB'
    else:
        return position_247
    
    

def comp_score_247_no_espn(entry_search, entry_match):
    score = name_score(entry_match['full_name'], entry_match['first_name'], 
                             entry_match['last_name'], entry_search['data.player'])
    score += height_dist_score(entry_match['height'], entry_search['data.height']) 
    score += weight_dist_score(entry_match['weight'], entry_search['data.weight'])
    score += (fuzz.ratio(entry_match['college_recruited'],entry_search['data.team'])/4)
    if entry_match['season_position'] == entry_search['pff_position']:
        return score + 25
    return score