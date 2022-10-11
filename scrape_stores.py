# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 09:23:21 2022

@author: Mehrab
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup


#This function is based on an exploration done in scrape_stores_exploration.ipynb
def scrape_stores_URL(URL, base_df):
    #URL is the store-locator URL to scrape store info from
    #base_df is the existing dataframe to which newly scraped stores will be added.
    
    r = requests.get(URL)

    if not (r.status_code < 300):
        print('page not loaded.')
        
      
    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib
    #looking at level 0
    a = list(soup.children)
    b = list(a[1].children)
    c = list(b[2].children)
    d = list(c[19].children)
    type(d[0])
    data_str = str(d[0])
    
    #parsing text clump to get individual store records
    
    def get_tag_text(string, tag):
        #function to get text in pair of "" after text tag
        start_ind = string.find(tag) 
        if start_ind == -1:
            return None, None
        else:
            start_ind = start_ind + (len(tag) + 2)        
        ind1 = string.find('"', start_ind)
        ind2 = string.find('"', (ind1 + 1))
        
        quote_inds = [ind1, ind2]
        quote_text = string[(ind1 + 1):ind2]
        return quote_text, quote_inds
    
    def get_latlong(string):
        #function to get first pair of lat and long values in string, assuming fixed char formatting
        start_ind = string.find('latitude')
        ind1 = string.find(':', start_ind)
        ind2 = string.find(',', (ind1 + 1))
        lat = float(string[(ind1 + 1):ind2])
        ind1 = string.find(':', (ind2 + 1))
        ind2 = string.find(',', (ind1 + 1))
        long = float(string[(ind1 + 1):(ind2 - 1)])
        
        quote_inds = [start_ind, ind2]
        return [lat, long], quote_inds



    store_n = 0
    while 1:
        storeNumber, parse_inds = get_tag_text(data_str, 'storeNumber')
        #pdb.set_trace()
        if storeNumber == None:
            break
                    
        #if store_n == 100:
        #    pdb.set_trace()
            
        data_str = data_str[(parse_inds[1] + 1):]
        latlong, parse_inds = get_latlong(data_str)
        data_str = data_str[(parse_inds[1] + 1):]
        city, parse_inds = get_tag_text(data_str, 'city')
        data_str = data_str[(parse_inds[1] + 1):]
        countrySubdivisionCode, parse_inds = get_tag_text(data_str, 'countrySubdivisionCode')
        data_str = data_str[(parse_inds[1] + 1):]
        countryCode, parse_inds = get_tag_text(data_str, 'countryCode')
        data_str = data_str[(parse_inds[1] + 1):]
        addressLines, parse_inds = get_tag_text(data_str, 'addressLines')
        data_str = data_str[(parse_inds[1] + 1):]
        hours, parse_inds = get_tag_text(data_str, 'hours')
        data_str = data_str[(parse_inds[1] + 1):]
        
        
        curr_store = pd.DataFrame(
            {'storeNumber': [storeNumber],
             'city': [city],
             'countrySubdivisionCode': [countrySubdivisionCode],
             'countryCode': [countryCode],
             'addressLines': [addressLines],
             'hours': [hours],
             'latitude': [latlong[0]],
             'longitude': [latlong[1]],
            })
    
        if store_n == 0 :
            stores_df = curr_store
        else:
            #skipping if this store has already been scraped
            if storeNumber not in list(stores_df['storeNumber']):
                #only add store if not alread in store_df
                stores_df = pd.concat([stores_df, curr_store], ignore_index = False)
                store_n += 1
    
    stores_df.reset_index(drop = True, inplace = True)
    
    return stores_df


#running lines
URL = 'https://www.starbucks.com/store-locator?map=38.90431,-77.0352,13z&place=Washington,%20DC,%20USA'
store_df = scrape_stores_URL(URL, [])