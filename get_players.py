# -*- coding: utf-8 -*-
import pandas as pd
import os
import make_league_path
from namespace import league_path

teams_file = '..\\data\\PFF\\teams.csv'

league_file = os.path.join(league_path,'league_teams.csv')
player_file = os.path.join(league_path,'recruits.csv')
df_teams = pd.read_csv(teams_file, index_col='id')
league_ids = []
team_id = input('Enter team id # (Enter 0 when done)')
while team_id != '0':
    if team_id.isdigit() and int(team_id) in df_teams.index:
        league_ids.append(int(team_id))
    else:
        print('Please try again')
    team_id = input('Enter team id # (Enter 0 when done)')
'''
# Find league ids from teams.csv and input
league_ids = [121, 140, 154, 167, 176, 210, 220,
              245, 248, 268, 304, 335, 337, 339]
'''
teams = df_teams.loc[league_ids]
teams.to_csv(league_file)

# Import team membership data
members = pd.read_csv('PFF/team_member.csv')
# Import PFF player data
players = pd.read_csv('PFF/players.csv')
# Get all players who were a member of the league at some point
# Some players may be included twice if they transferred within the league
team_members = members[members['franchise_id'].isin(teams.index)]
# Get instances for all the teams those players were members of at some point
members_all_teams = members[(members['player_id'].isin(team_members['player_id'])) & 
                            (members['league_id']==2)].copy()

def zero_pad(date_str):
    date_list = date_str.split(sep='/')
    for i in (0,1):
        if len(date_list[i]) < 2:
            date_list[i] = '0' + date_list[i]
    return('/'.join(date_list))        

# Convert effective start date to datetime object for chronological sorting
members_all_teams['effective_start'] = members_all_teams['effective_start'].apply(zero_pad)
members_all_teams['effective_start'] = pd.to_datetime(members_all_teams['effective_start'], format='%m/%d/%Y')
all_sorted=members_all_teams.sort_values(['player_id','effective_start'])
# For duplicate players, retain only the first entry
# As far as we know, this is the school that recruited them out of high school / JC
all_sifted = all_sorted.loc[all_sorted['player_id'].drop_duplicates().index]
# Filter out players who were not recruited by a team in the league
league_recruits = all_sifted[all_sifted['franchise_id'].isin(teams.index)].copy()
# Add a column with just the school name
league_recruits['college_recruited'] = league_recruits['franchise_id'].map(teams['city'])
# Some clean up for the merge
league_recruits.rename(columns = {'franchise_id': 'college_recruited_id'}, inplace = True)
players.rename(columns = {'id': 'player_id'}, inplace = True)
recruit_cols = ['player_id', 'team_member_id', 'college_recruited_id', 'college_recruited']
# Merge team membership info with player info
league_players = league_recruits[recruit_cols].merge(players, on = 'player_id')
# Some cleaning
league_players = league_players[~(league_players['full_name'] == 'Replace Me')]

player_file = league_file.replace('league_teams', 'recruits')
league_players.to_csv(player_file)