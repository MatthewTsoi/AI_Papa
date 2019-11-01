#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the module to provide functions to extract and prepare data set from 
Hong Kong Goveronment's Open data (data.gov.hk)

@author: matthew.tsoi@gmail.com
"""
import json
import requests
#import pandas 





##Main routine
if __name__ == "__main__":
    uri= 'http%3A%2F%2Fwww.ha.org.hk%2Fopendata%2Faed%2Faedwtdata-en.json'
    
    url="https://api.data.gov.hk/v1/historical-archive/list-file-versions?url="+uri+"&start=20191001&end=20191030"
    r=requests.get(url)
    data=r.json()
    print(str(data)) 
    
    
    
    