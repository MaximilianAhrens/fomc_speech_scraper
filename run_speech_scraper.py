# -*- coding: utf-8 -*-
# by Maximilian Ahrens | Oxford 2021

#=================================
# Imports
#=================================
import os, glob
import sys
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
import time, random, schedule
from datetime import datetime, date
import urllib.request, urllib.error
from wrapt_timeout_decorator import *
from urllib.error import HTTPError
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper import *

#=================================
# Set arguments
#=================================
parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, default=None, help="choose which speaker position to start from.")
parser.add_argument("--end", type=int, default=None, help="choose which speaker position to end on.")
args = parser.parse_args()

#=================================
# Define paths and url
#=================================
url = 'https://fraser.stlouisfed.org/series/statements-speeches-federal-open-market-committee-participants-3761'

user_path = os.getcwd()
download_path = os.path.join(user_path,'output')

try:
    os.makedirs(download_path)
    print(f'creating new download folder:\n{download_path}')
except FileExistsError:
    print(f'using existing download folder:\n{download_path}')

if sys.platform == "darwin":
    input_list = pd.read_csv(os.path.join(user_path,'input','input_list.csv'), header=0, index_col=0)
elif sys.platform == "linux":
    input_list = pd.read_csv(os.path.join(user_path,'input','input_list.csv'), header=0, index_col=0)

if args.start is not None or args.end is not None:
    if args.end is None:
        assert isinstance(args.start,int)
        input_list = input_list[args.start:]
    elif args.start is None:
        assert isinstance(args.end,int)
        input_list = input_list[:args.end]
    else:
        assert isinstance(args.start,int) and isinstance(args.end,int)
        input_list = input_list[args.start:args.end]

#========================================
# Define functions
#========================================
def main(url, input_list):
    ''' main methods for FOMC speech collections'''
    def start_driver():
        driver = start_selenium_browser(headless = False)
        return driver


    def wait_for(item, secs=60):
        WebDriverWait(driver, secs).until(EC.visibility_of_element_located((By.XPATH, item)))

    
    def sleep(min_sec=25,max_sec=150):
        time.sleep(random.randint(min_sec,max_sec)/100)
    
    
    # iterate through speakers
    for p,n in zip(input_list.index,input_list.name):
        try:
            speaker = n.replace('Statements and Speeches of ','')
            speaker_pos = p
            os.makedirs(os.path.join(download_path,speaker))
            #break
        except FileExistsError:
            continue
        speaker_path = os.path.join(download_path,speaker)
        print(f'\n\n\n#####downloading speeches by:{speaker,speaker_pos} of {len(input_list.name)}#####\n')
        
        # start selenium search for selected speaker
        driver = start_driver()
        driver.get(url)
        wait_for(f'//*[@id="list-container"]/ul/li[{speaker_pos}]/span')
        sleep()
        driver.find_element_by_xpath(f'//*[@id="list-container"]/ul/li[{speaker_pos}]/span').click()
        wait_for('//*[@id="records"]/div/div[2]/p[1]/span[2]')
        speaker_time_frame = driver.find_element_by_xpath('//*[@id="records"]/div/div[2]/p[1]/span[2]').get_attribute("innerHTML").replace('\t','').replace('\n','')
        speaker_position = driver.find_element_by_xpath('//*[@id="records"]/div/div[2]/ul[2]/li/a').get_attribute('innerHTML').replace('\t','').replace('\n','')
        # click on speaker to get to speech list
        wait_for('//*[@id="records"]/div/div[2]/p[1]/span[2]')
        n_speeches = driver.find_element_by_xpath(f'//*[@id="records"]/div/div[2]/p[2]/a/span').get_attribute('innerHTML').replace('\n','').strip().replace('(','').split(' ')[0]
        driver.find_element_by_xpath(f'//*[@id="records"]/div/div[2]/p[2]/a/span').click()
        speaker_url = driver.current_url

        # get IDs of speeches
        sids = [] # speech IDs
        titles = []
        dates = []
        contents = []
        for d in range(1,6): # try at maximum 5 decades per person
            decade_sids = []
            try:
                sleep()
                driver.find_element_by_xpath(f'//*[@id="issues"]/div/nav/ul/li[{d}]/a').click()
                speaker_url_decade = driver.current_url
                wait_for('//*[@id="list-container"]')
                inner_html = driver.find_element_by_xpath('//*[@id="list-container"]').get_attribute('innerHTML')
                for i in inner_html.split('data-id="')[1:]:
                    decade_sids.append(i.split('"')[0])
            except:
                pass
                break # maximum decade range reached
            new_sids = list(set(decade_sids) - set(sids))
            sids = list(set(sids + decade_sids))
            print(f'\n{len(new_sids)} speeches found in decade #{d} for speaker {speaker}\n')
 
            # iterate through speech IDs and download txt files
            for sid in tqdm(new_sids[6:]):
                sleep()
                wait_for(f'//*[@id="item-{sid}"]/span')
                driver.find_element_by_xpath(f'//*[@id="item-{sid}"]/span').click()
                wait_for('//*[@id="issues"]/div/div[2]/p[2]/a')  
                driver.find_element_by_xpath('//*[@id="issues"]/div/div[2]/p[2]/a').click()
                wait_for('//*[@id="content"]/div[2]/div[2]/h2')
                speech_title =  driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/h2').get_attribute('innerHTML').replace('\t','').replace('\n','')
                wait_for('//*[@id="content"]/div[2]/div[2]/p[1]/span[2]')
                speech_date = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/p[1]/span[2]').get_attribute('innerHTML').replace('\t','').replace('\n','')
                matched = 0
                for idx in range(2,8):
                    try:
                        sleep()
                        wait_for(f'//*[@id="content"]/div[2]/div[2]/p[{idx}]/a[2]',secs=5)
                        driver.find_element_by_xpath(f'//*[@id="content"]/div[2]/div[2]/p[{idx}]/a[2]').click()
                        wait_for('//*[@id="content"]/div[2]/div/pre',secs=5)
                        speech_content = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div/pre').get_attribute('innerHTML')
                        matched = 1
                        break
                    except:
                        pass
                if not matched:
                    for idx in range(2,8):
                        try:
                            sleep()
                            wait_for(f'//*[@id="content"]/div[2]/div[2]/p[{idx}]/a[3]',secs=5)
                            driver.find_element_by_xpath(f'//*[@id="content"]/div[2]/div[2]/p[{idx}]/a[3]').click()
                            wait_for('//*[@id="content"]/div[2]/div/pre',secs=5)
                            speech_content = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div/pre').get_attribute('innerHTML')
                            break
                        except:
                            if idx == 7:
                                raise ValueError
                            else:
                                pass
          
                titles.append(speech_title)
                dates.append(speech_date)
                contents.append(speech_content)
                # go to next speech by this speaker
                sleep()
                driver.get(speaker_url_decade)

        speaker_ids = [speaker]*len(contents)
        speaker_positions = [speaker_position]*len(contents)
        speaker_df = pd.DataFrame(data=[speaker_ids,speaker_positions,dates,titles,contents],index=['speaker','position','date','title','content']).T
        # drop duplicates
        speaker_df.drop_duplicates(inplace=True, ignore_index=True)
        # error logbook checks
        if len(sids) != int(n_speeches):
            diff = n_speeches - len(sids)
            with open(os.path.join(speaker_path,f'1_error_log: {diff} speeches not parsed.txt'), 'w') as f:
                f.write(str(diff))
        if speaker_df.isnull().values.any():
            n_nan = speaker_df.isnull().sum().sum()
            with open(os.path.join(speaker_path,f'2_error_log: {n_nan} of {n_speeches} parsed as nan.txt'), 'w') as f:
                f.write(str(n_nan))
        # save data
        speaker_df.to_csv(os.path.join(speaker_path,f'{speaker}.csv'))
        driver.quit()

if __name__ == '__main__':
    main(url, input_list)
        