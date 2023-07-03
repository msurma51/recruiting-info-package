# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 16:01:12 2022

@author: surma
"""
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
import sys


def name_score(full_search, first_search, last_search, full_match):
    # Assigns a score to how names compare based on full name comparison and
    # comparison of first, last from search to possible first, last 
    # from matching df
    full_ratio = 2*fuzz.ratio(full_search, full_match)
    if full_ratio == 200:
        return full_ratio
    full_match_split = full_match.split()
    first_match_1 = full_match_split[0]
    last_match_1 = ' '.join(full_match_split[1:])
    first_last_ratio_1 = fuzz.ratio(first_search, first_match_1) + fuzz.ratio(last_search, last_match_1)
    if len(full_match_split) > 2:
        first_match_2 = ' '.join(full_match_split[:2])
        last_match_2 = ' '.join(full_match_split[2:])
        first_last_ratio_2 = fuzz.ratio(first_search, first_match_2) + fuzz.ratio(last_search, last_match_2)
    else:
        first_last_ratio_2 = 0
    return max(full_ratio, first_last_ratio_1, first_last_ratio_2)

def height_inches(height):
    inches = height % 100
    feet = height // 100
    return feet*12 +inches
    
def height_dist_score(ht_search, ht_match):
    dist = abs(height_inches(ht_search) - height_inches(ht_match))
    if dist < 5:
        return 25 - 5*dist
    else:
        return 0

def weight_dist_score(wt_search, wt_match):
    penalty = abs(wt_search-wt_match)//2
    if penalty < 25:
        return 25 - penalty
    else:
        return 0
    

def comp_score_espn(entry_match, entry_search):
    score = name_score(entry_search['full_name'], entry_search['first_name'], 
                             entry_search['last_name'], entry_match['name'])
    score += height_dist_score(entry_search['height'],entry_match['ht.']) 
    score += weight_dist_score(entry_search['weight'],entry_match['wt.'])
    for hometown in (entry_match['hometown_id.x'], entry_match['hometown_id.y']):
        if entry_search['hometown_id'] == hometown:
            return score + 50
    return score

def comp_score_espn_found(entry_search, entry_match):
    score = name_score(entry_match['full_name'], entry_match['first_name'], 
                             entry_match['last_name'], entry_search['name'])
    score += height_dist_score(entry_match['height'],entry_search['ht.']) 
    score += weight_dist_score(entry_match['weight'],entry_search['wt.'])
    score += (fuzz.ratio(entry_search['team'],entry_match['college_recruited'])/4)
    if entry_search['pos'] == entry_match['season_position']:
            return score + 25
    return score

def inner_comp_score(row_merge):
    score = name_score(row_merge['full_name'], row_merge['first_name'], 
                             row_merge['last_name'], row_merge['name'])
    score += height_dist_score(row_merge['height'],row_merge['ht.']) 
    score += weight_dist_score(row_merge['weight'],row_merge['wt.'])
    for hometown in (row_merge['hometown_id.x'], row_merge['hometown_id.y']):
        if row_merge['hometown_id'] == hometown:
            return score + 50
    return score
  
def pos_mapper(position):
    # Maps position string taken from ESPN site to pos abbreviation
    easy_map = {'Wide Receiver': 'WR',
                'Running Back': 'HB',
                'Athlete': 'ATH',
                'Fullback': 'FB',
                'Offensive Tackle': 'T',
                'Offensive Guard': 'G',
                'Center': 'C',
                'Defensive Tackle': 'DI',
                'Defensive End': 'ED',
                'Outside Linebacker': 'ED',
                'Inside Linebacker': 'LB',
                'Safety': 'S', 
                'Cornerback': 'CB',
                'Kicker': 'K',
                'Punter': 'K',
                'Long Snapper': 'LS'
                }
    if position in easy_map.keys():
        return easy_map[position]
    if 'Quarterback' in position:
        return 'QB'
    if 'Tight End' in position:
        return 'TE'
    return ''
        
    
    
    
    
    