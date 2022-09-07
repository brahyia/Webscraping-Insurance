#!/usr/bin/env python
# coding: utf-8

# In[6]:


# %%
import datetime
import os
import random
import re
import time
import inspect
import ssl
import csv

import numpy as np
import pandas as pd


import Functions.utils as ut
import Functions.config as cf
from selenium.webdriver.common.by import By
from sqlalchemy import update
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


pd.set_option('display.max_rows', 300)

print(os.getcwd())


# In[27]:


driver = ut.chrome_init('jan')


# In[46]:


tunnel, eng = ut.mysql_connect()


# In[9]:


sql_find_car = r"""
Select * 
    FROM SE_input_plates 
    WHERE 
        'Status' IS NOT NULL AND
        "Fordonskategori EU" LIKE 'M_' AND
        error IS NULL
    ORDER BY RANDOM() 
    limit 1;
"""

sql_find_person = r"""
Select * 
    FROM SE_input_personnummers_all_combinations 
    WHERE error IS NULL
    ORDER BY RANDOM() 
    limit 1;
"""


# In[48]:


driver.get('https://www.compricer.se/forsakring/bil/')
driver.click_text("Jag godkänner", error=False)

while True:
    # Find person and car
    print('Getting data from SQL')
    car = pd.read_sql(sql_find_car, con=eng)
    plate = car['Registreringsnummer'][0]
    person = pd.read_sql(sql_find_person, con=eng)
    pid = person['personnummer'][0]
    with open("sweden_telephone.csv", "r") as number_csv_file:
        csv_reader = csv.reader(number_csv_file)
        next(csv_reader)
        number = (random.choice([line[0] for line in csv_reader]))
    print('Got data from SQL')

    # go to website
    driver.get('https://www.compricer.se/forsakring/bil/')

    # Cookie window

    #     if driver.element_exists(path='onetrust-pc-btn-handler', by=By.ID):
    #         driver.click(path='onetrust-pc-btn-handler', by=By.ID, error=False)
    #         driver.click(path="//button[text() = 'Spara och godkänn']", by=By.XPATH, error=False)

    driver.click_text('Trafik­försäkring')

    # First website

    driver.send_keys(path='carregnumber', by=By.ID, keys=plate) # Car plate

    driver.click_text("Jämför nu")

    driver.send_keys(path='civicnumber', by=By.ID, keys=pid) # Person ID
    driver.send_keys(path='phonenumber', by=By.ID, keys=number) #person telephone number
    
    

        # accident in the last two years

    option = (random.choice(['Nej','Ja']))
    xpath = f"//*[@id='damagelast2years']//*[text()='{option}']//..//..//.."
    box1 = driver.find_element(By.XPATH, xpath).click()


    option2 = (random.choice(['Nej', 'Ja']))

    xpath = f"//*[@id='driverbelow25']//*[text()='{option2}']//..//..//.."
    box1 = driver.find_element(By.XPATH, xpath).click()

    # parking choice
    rand_parking = (random.choice([1,2,3,4,5]))

    parking_xpaths = f"//*[@id='parking']/option[{rand_parking}]"
    parking_options = driver.find_element(By.XPATH, parking_xpaths).click()
    parking_option = driver.find_element(By.XPATH, parking_xpaths)
    parking = parking_option.get_attribute('value')

    #housing
    randss = (random.choice([1,2,3,4,5,6]))

    house_xpath = f"//*[@id='housing']/option[{randss}]"
    housing_options = driver.find_element(By.XPATH, house_xpath).click()
    housing_option = driver.find_element(By.XPATH, house_xpath)
    housing = housing_option.get_attribute('value')
    
# mileage

    rands = (random.choice([1,2,3,4,5,6,7,8,9,10]))

    mileage_xpathss = f"//*[@id='yearlymileage']/option[{rands}]"
    mileagess = driver.find_element(By.XPATH, mileage_xpathss).click()
    mileages = driver.find_element(By.XPATH, mileage_xpathss)
    mileages = mileages.get_attribute('value')
    
  
    
    driver.click_text("Jämför nu!")
    
     # Price website
    if driver.element_exists(path="//*[text() = 'Din sökning gav inga resultat']", by=By.XPATH):
        eng.execute(f"""
            UPDATE SE_input_plates
            SET error = 'WARNING: Car uninsurable by compricer'
            WHERE Registreringsnummer = '{plate}'
        """)
        continue
    boxes = driver.find_elements(By.CLASS_NAME, 'card-body')

    prices = []
    images = []
    for box in boxes:
        try:
            price = box.find_element(By.XPATH, ".//h2[contains(text(),'kr')]").text
            image = box.find_element(By.XPATH, ".//*[@class = 'tw-w-full tw-max-w-32 lg:tw-min-w-24 tw-cursor-pointer']").get_attribute('alt')
        except NoSuchElementException:
            continue
        else:
            prices.append(price)
            images.append(image)

    df = pd.DataFrame({
        'price': prices,
        'insurer': images,
        'personnummer': pid,
        'plate': plate,
        'cover': 'Trafikförsäkring',
        'mileage': mileages,
        'housing': housing,
        'nightparking': parking,
        'accidents_last2years': option,
        'young_driver': option2
    })

    df = df.drop_duplicates()
    print(df)


    df.to_sql(name='SE_output_compricer', con=eng, if_exists= 'append', index=False)


# In[33]:


df


# In[37]:


df2 = df.copy(deep = True)


# In[39]:


df2['price']=[477,1042]


# In[40]:


df2


# In[47]:


df2.to_sql(name='SE_output_compricer', con=eng, if_exists= 'replace', index=False)


# In[ ]:




