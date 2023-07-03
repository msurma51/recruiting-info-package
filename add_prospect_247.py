# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 21:06:57 2022

@author: surma
"""


import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import pandas as pd

def height_converter(height_string):
    parts = height_string.split('-')
    if len(parts[1]) > 1:
        return parts[0] + parts[1]
    else:
        return parts[0] + '0' + parts[1]
    
def scrape_247(driver, main_file, team_map):    
    df_main = pd.read_csv(main_file, index_col = 0)
    info_dict = dict()


    # url = 'https://247sports.com/Season/{}-Football/Recruits/'.format(str(search_year))
    # driver.get(url)


    # name_section = driver.find_element(By.CLASS_NAME, "form-section")
    # name_box = name_section.find_element(By.TAG_NAME, "input")
    # name_box.send_keys(name)
    # name_button = name_section.find_element(By.TAG_NAME, "button")
    # name_button.click()
    # results = driver.find_element(By.CLASS_NAME, "results")
    # if result_num > 1:
    #     best_result = results.find_elements(By.CLASS_NAME, "name")[result_num - 1]
    # else:
    #     best_result = results.find_element(By.CLASS_NAME, "name")
    # profile_button_1 = best_result.find_element(By.TAG_NAME, "a")
    # profile_button_1.click() 
    # try:
    #     profile_button_2 = driver.find_element(By.CLASS_NAME, "view-profile-link")
    #     profile_button_2.click()
    # except:
    #     None
    
    prospect_info = driver.find_element(By.CLASS_NAME, "upper-cards")
    info_dict['data.player'] = prospect_info.find_element(By.CLASS_NAME, "name").text
    metrics_list = prospect_info.find_element(By.CLASS_NAME, "metrics-list")
    metrics = metrics_list.find_elements(By.TAG_NAME, "span")
    metrics_text = [metric.text for metric in metrics]
    info_dict['data.position'] = metrics_text[1]
    info_dict['data.height'] = height_converter(metrics_text[3])
    info_dict['data.weight'] = metrics_text[5]
    details_list = prospect_info.find_element(By.CLASS_NAME, "details ")
    details = details_list.find_elements(By.TAG_NAME, "span")
    details_text = [detail.text for detail in details]  
    info_dict['data.previous_school'] = details_text[1]
    info_dict['data.hometown'] = details_text[3]
    info_dict['season'] = details_text[5]
    
    ranking_info = driver.find_elements(By.CLASS_NAME, "rankings-section")[1]
    info_dict['data.stars'] = len(ranking_info.find_elements(By.CLASS_NAME, "icon-starsolid.yellow"))   
    info_dict['data.rating'] = ranking_info.find_element(By.CLASS_NAME, "rank-block").text
    ranks_list = ranking_info.find_element(By.CLASS_NAME, "ranks-list")
    ranks = ranks_list.find_elements(By.TAG_NAME, "a")
    ranks_text = [rank.text for rank in ranks]
    if 'History' in ranks_text:
        ranks_text.remove('History')
    rank_tups = list(zip(('data.nat','data.pos','data.st'), ranks_text))
    info_dict.update({tup[0]:tup[1] for tup in rank_tups})       
    
    try:
        team_info = driver.find_element(By.CLASS_NAME, "college-comp")
        info_dict['data.status'] = team_info.find_element(By.TAG_NAME, "h2").text  
        info_dict['data.team'] = team_info.find_element(By.CLASS_NAME, "college-comp__team-name-link").text
        info_dict['data.team_id'] = team_map.loc[info_dict['data.team']]['data.team_id']
    except:
        None
    ser = pd.Series(info_dict)
    ser = ser.replace('N/A', '')
    add_row = ser.to_frame().transpose()
    df_main = pd.concat((df_main,add_row)) 
    df_main.reset_index(drop=True, inplace=True)
    
    df_main.to_csv(main_file)
    
