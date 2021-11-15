import pandas as pd
import os
import selenium
from selenium import webdriver
import time
import requests
from webdrivermanager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException
from requests import get
from collections import defaultdict
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from dateutil import parser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv


bunq_comments = 'https://together.bunq.com/all'
OUTPUT_CSV = 'bunq_together.csv'


def scrape_bunq_comments_250(soup):
    comments_urls = []    
    
    url = soup
    driver = webdriver.Chrome()
    driver.get(url)
    
    date = driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div/div[2]/ul/li/div/div/a[2]/ul/li/span/time')
    
    last_date = date[-1].get_attribute('datetime')
    last_date_f= parser.parse(last_date)
    
    
    while last_date_f > parser.parse('2020-06-01T18:00:52+02:00'):
        date1 = driver.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div/div/div[2]/ul/li/div/div/a[2]/ul/li/span/time')
        last_date = date1[-1].get_attribute('datetime')
        last_date_f= parser.parse(last_date)

        button = driver.find_element_by_xpath('//*[@id="content"]/div/div[3]/div/div/div[2]/div/button')
        button.click()
        wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div/div[3]/div/div/div[2]/div/button')))
        
    links = driver.find_elements_by_xpath('//*[@id="content"]/div/div/div/div/div/ul/li/div/div/a[2]')
    
    for element in links:
        comments_urls.append(element.get_attribute('href'))
     
        
    

    driver.quit()
    
    return comments_urls

def scrape_comment_page(dom):
    all_data = {}
    
    all_data['Users']= []
    all_data['Title']= []
    all_data['Time']= []
    all_data['Comments']= []
    all_data['Time_per_comment']= []

    driver = webdriver.Chrome()
    driver.get(dom)
    wait = WebDriverWait(driver, 10)
    
    
    
    users = driver.find_elements_by_xpath('//*[@id="content"]/div/div/div/div/div/div/article/div/header/ul/li/div/h3/a')
    time = driver.find_elements_by_xpath('//*[@id="content"]/div/div/div/div/div/div/article/div/header/ul/li/div/a/time')
    title = driver.find_element_by_xpath('//*[@id="content"]/div/div/header/div/ul/li/h2')
    
    
    x=0
    stop = 0
    while True:
        x += 1
        try:
            text = driver.find_element_by_xpath(f'//*[@id="content"]/div/div/div/div/div/div[{x}]/article/div/div/p[2]')
        
            all_data['Comments'].append(text.text)
        except NoSuchElementException:
            try:
                text = driver.find_element_by_xpath(f'//*[@id="content"]/div/div/div/div/div/div[{x}]/article/div/div/p')
                all_data['Comments'].append(text.text)
                
            except NoSuchElementException:
                stop += 1
                if stop > 2:
                    break
                    
    
    for element in users:
        all_data["Users"].append(element.text)
    for element in time:
        all_data['Time_per_comment'].append(element.get_attribute('datetime'))
    all_data['Title'].append(title.text)
    all_data['Time'].append(time[-1].get_attribute('datetime'))
    
    driver.quit()
    
    return all_data


def data(dom):
    url_strings = scrape_bunq_comments_250(dom)

    rows = []
    for i, url in enumerate(url_strings): 
        rows.append(scrape_comment_page(url))
    
    return rows

def save_csv(filename, rows):
    csv_columns = ['Users','Title','Users','Time','Title_per_comment','Comments']    
    with open(filename, 'w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(rows)


full_data = data(bunq_comments)
save_csv(OUTPUT_CSV, full_data)