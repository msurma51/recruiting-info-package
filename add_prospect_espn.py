# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 09:49:01 2022

@author: surma
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import pandas as pd
import numpy as np
import re
import os

star_dict = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}

def height_converter(hstring):
    hlist = hstring.split(sep = '-')
    if len(hlist[1]) > 1:
        return hlist[0] + hlist[1]
    else:
        return hlist[0] + '0' + hlist[1]

def espn_scrape(driver, main_file):
    if os.path.exists(main_file):    
        df_main = pd.read_csv(main_file, index_col = 0)
    else:
        df_main = pd.DataFrame()
    info_dict = dict()
    info_dict['name'] = driver.find_element(By.CLASS_NAME, "player-name").text
    bio = driver.find_element(By.CLASS_NAME, "bio")
    bio_list = bio.text.split(sep = '\n')
    hwc_list = bio_list[0].split(sep = '|')
    pattern = '(\d-\d+), (\d+)'
    hw_tup = re.findall(pattern, hwc_list[0])
    info_dict['ht.'] = height_converter(hw_tup[0][0])
    info_dict['wt.'] = hw_tup[0][1]
    season = re.findall('\d+', hwc_list[-1])
    if len(season) > 0:
        info_dict['season'] = season[0]
    info_dict['city'] = bio_list[2]
    info_dict['previous_school'] = bio_list[4]
    info_dict['position'] = bio_list[6]
    bio_items = bio.find_elements(By.TAG_NAME, "li")
    team_list = bio_items[-1].find_elements(By.TAG_NAME, "a")
    if len(team_list) > 0:   
        info_dict['team'] = team_list[0].text.strip()
    
    try:
        stats = driver.find_element(By.CLASS_NAME, "stats")
        rating = stats.find_element(By.CLASS_NAME, "mod-rating")
        r_elements = rating.find_elements(By.TAG_NAME, "li")
        grade = r_elements[0].text
        star_element = r_elements[1]
        star_key = [key for key in star_dict.keys() if key in star_element.get_attribute('class')]
    except:
        grade = 'NR'
        star_key = []
    if len(star_key) > 0:
        stars = star_dict[star_key[0]]
    else: 
        stars = np.NaN
    try:
        rank = stats.find_element(By.CLASS_NAME, "rank")
        rank_str = rank.text
        rank_num = int(rank_str[:-2])
        img = rank.find_element(By.TAG_NAME, "img")
        rank_type = img.get_attribute('title')
    except:
        rank_num = np.NAN
        rank_type = ''

    info_dict['grade'] = grade
    info_dict['e.stars'] = stars
    info_dict['e.rank'] = rank_num
    info_dict['e.rank_type'] = rank_type
    
    
    # Find, get and add scouting report
    try:
        tabs = driver.find_element(By.CLASS_NAME, "ui-tabs")
        tab_buttons = tabs.find_elements(By.TAG_NAME, "a")
        report_tab = [button for button in tab_buttons if button.text == 'Scouting Report']
    except:
        report_tab = []
        
    if len(report_tab) > 0:
        try:
            report_tab[0].click() 
            files = driver.find_element(By.ID, "PlayerFiles") 
            table_list = files.find_elements(By.TAG_NAME, "table")
            report_string = ''
            if len(table_list) > 0:
                table = table_list[0]
                table_data = table.find_elements(By.TAG_NAME, "td")
                for i in range(int(len(table_data)/2)):
                    report_string += '{}: {} '.format(table_data[2*i].text, table_data[2*i+1].text)
            else:
                article = files.find_element(By.CLASS_NAME, "mod-content.article")
                report_list = article.find_elements(By.TAG_NAME, "p")
                if len(report_list) > 1:
                    report = report_list[1]
                else:
                    try: 
                        report = driver.find_element(By.NAME, "bottomLine")
                    except:
                        report = driver.find_element(By.NAME, "juniorEval")
            try:
                if len(report_string) > 0:
                    info_dict['e.scouting_report'] = report_string
                elif len(report.text) > 0:
                    info_dict['e.scouting_report'] = report.text
                else:
                    info_dict['e.scouting_report'] = 'No article confirmed'
            except:
                info_dict['e.scouting_report'] = 'No article error'                         
        except:
            info_dict['e.scouting_report'] = 'No article confirmed'
        
    #Find, get and add testing results
    try:
        tabs = driver.find_element(By.CLASS_NAME, "ui-tabs")
        tab_buttons = tabs.find_elements(By.TAG_NAME, "a")
        testing_tab = [button for button in tab_buttons if button.text == 'Testing Results']
    except:
        testing_tab = []
     
    if len(testing_tab) > 0:        
        try:
            testing_tab[0].click()    
            files = driver.find_element(By.ID, "PlayerFiles") 
            combine_ids = files.find_elements(By.CLASS_NAME, "combine-id")
            combine_data = files.find_elements(By.CLASS_NAME, "combine-bar-data")
            combine_dict = {tup[0].text:tup[1].text for tup in zip(combine_ids,combine_data)}
            for key in combine_dict.keys():
                info_dict[key] = combine_dict[key]                             
        except:
            None

    ser = pd.Series(info_dict)
    ser = ser.replace('N/A', '')
    add_row = ser.to_frame().transpose()
    df_main = pd.concat((df_main,add_row)) 
    df_main.reset_index(drop=True, inplace=True)
    
    df_main.to_csv(main_file)
    
def espn_update(driver):
    info_dict = dict()
    bio = driver.find_element(By.CLASS_NAME, "bio")
    bio_list = bio.text.split(sep = '\n')
    hwc_list = bio_list[0].split(sep = '|')
    info_dict['position'] = bio_list[6]
    try:
        stats = driver.find_element(By.CLASS_NAME, "stats")
        rating = stats.find_element(By.CLASS_NAME, "mod-rating")
        r_elements = rating.find_elements(By.TAG_NAME, "li")
        star_element = r_elements[1]
        star_key = [key for key in star_dict.keys() if key in star_element.get_attribute('class')]
    except:
        star_key = []
    if len(star_key) > 0:
        stars = star_dict[star_key[0]]
    else: 
        stars = 0
    try:
        rank = stats.find_element(By.CLASS_NAME, "rank")
        rank_str = rank.text
        rank_num = int(rank_str[:-2])
        img = rank.find_element(By.TAG_NAME, "img")
        rank_type = img.get_attribute('title')
    except:
        rank_num = np.NAN
        rank_type = ''

    info_dict['e.stars'] = stars
    info_dict['e.rank'] = rank_num
    info_dict['e.rank_type'] = rank_type
    
    
    # Find, get and add scouting report
    try:
        tabs = driver.find_element(By.CLASS_NAME, "ui-tabs")
        tab_buttons = tabs.find_elements(By.TAG_NAME, "a")
        report_tab = [button for button in tab_buttons if button.text == 'Scouting Report']
    except:
        report_tab = []
        
    if len(report_tab) > 0:
        try:
            report_tab[0].click() 
            files = driver.find_element(By.ID, "PlayerFiles") 
            table_list = files.find_elements(By.TAG_NAME, "table")
            report_string = ''
            if len(table_list) > 0:
                table = table_list[0]
                table_data = table.find_elements(By.TAG_NAME, "td")
                for i in range(int(len(table_data)/2)):
                    report_string += '{}: {} '.format(table_data[2*i].text, table_data[2*i+1].text)
            else:
                article = files.find_element(By.CLASS_NAME, "mod-content.article")
                report_list = article.find_elements(By.TAG_NAME, "p")
                if len(report_list) > 1:
                    report = report_list[1]
                else:
                    try: 
                        report = driver.find_element(By.NAME, "bottomLine")
                    except:
                        report = driver.find_element(By.NAME, "juniorEval")
            try:
                if len(report_string) > 0:
                    info_dict['e.scouting_report'] = report_string
                elif len(report.text) > 0:
                    info_dict['e.scouting_report'] = report.text
                else:
                    info_dict['e.scouting_report'] = 'No article confirmed'
            except:
                info_dict['e.scouting_report'] = 'No article error'                         
        except:
            info_dict['e.scouting_report'] = 'No article confirmed'
        
    #Find, get and add testing results
    try:
        tabs = driver.find_element(By.CLASS_NAME, "ui-tabs")
        tab_buttons = tabs.find_elements(By.TAG_NAME, "a")
        testing_tab = [button for button in tab_buttons if button.text == 'Testing Results']
    except:
        testing_tab = []
     
    if len(testing_tab) > 0:        
        try:
            testing_tab[0].click()    
            files = driver.find_element(By.ID, "PlayerFiles") 
            combine_ids = files.find_elements(By.CLASS_NAME, "combine-id")
            combine_data = files.find_elements(By.CLASS_NAME, "combine-bar-data")
            combine_dict = {tup[0].text:tup[1].text for tup in zip(combine_ids,combine_data)}
            for key in combine_dict.keys():
                info_dict[key] = combine_dict[key]                             
        except:
            None

    ser = pd.Series(info_dict)
    ser = ser.replace('N/A', '')
    return ser

def espn_update_sr(driver):
    scouting_report = ''
    # Find, get and add scouting report
    try:
        tabs = driver.find_element(By.CLASS_NAME, "ui-tabs")
        tab_buttons = tabs.find_elements(By.TAG_NAME, "a")
        report_tab = [button for button in tab_buttons if button.text == 'Scouting Report']
    except:
        report_tab = []
        
    if len(report_tab) > 0:
        try:
            report_tab[0].click() 
            files = driver.find_element(By.ID, "PlayerFiles") 
            table_list = files.find_elements(By.TAG_NAME, "table")
            report_string = ''
            if len(table_list) > 0:
                table = table_list[0]
                table_data = table.find_elements(By.TAG_NAME, "td")
                for i in range(int(len(table_data)/2)):
                    report_string += '{}: {} '.format(table_data[2*i].text, table_data[2*i+1].text)
            else:
                article = files.find_element(By.CLASS_NAME, "mod-content.article")
                report_list = article.find_elements(By.TAG_NAME, "p")
                if len(report_list) > 1:
                    report = report_list[1]
                else:
                    try: 
                        report = driver.find_element(By.NAME, "bottomLine")
                    except:
                        report = driver.find_element(By.NAME, "juniorEval")
            try:
                if len(report_string) > 0:
                    scouting_report = report_string
                elif len(report.text) > 0:
                    scouting_report = report.text
                else:
                    scouting_report = 'No article confirmed'
            except:
                scouting_report = 'No article error'                         
        except:
            scouting_report = 'No article confirmed'
    return scouting_report
        
