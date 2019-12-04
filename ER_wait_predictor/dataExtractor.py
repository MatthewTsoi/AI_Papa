#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the module to provide functions to extract and prepare data set from 
Hong Kong Goveronment's Open data (data.gov.hk)

@author: matthew.tsoi@gmail.com
"""
import json
import requests
import pandas as pd
from pandas.io.json import json_normalize





##Main routine
if __name__ == "__main__":
    uri= 'http%3A%2F%2Fwww.ha.org.hk%2Fopendata%2Faed%2Faedwtdata-en.json'
    
    url="https://api.data.gov.hk/v1/historical-archive/list-file-versions?url="+uri+"&start=20191030&end=20191130"
    r=requests.get(url)
    data=r.json()
    #print(str(data['timestamps'])) 


    index_df = pd.DataFrame.from_dict(data['timestamps'])
    #print(df.head(5))

    df=pd.DataFrame()

    for index, row in index_df.iterrows():
    
        url='https://api.data.gov.hk/v1/historical-archive/get-file?url='
        uri='http%3A%2F%2Fwww.ha.org.hk%2Fopendata%2Faed%2Faedwtdata-en.json'
        params='&time='+row[0]

        request_url=url+uri+params
        prev_rowcnt=len(df)
        df = df.append(pd.DataFrame.from_dict(json_normalize(data=requests.get(request_url).json(),record_path='waitTime',meta=['updateTime']) ))
        print(row[0]+":"+str(len(df)-prev_rowcnt)+":"+str(len(df)))

    #print(df.info())
    print(df.head(200))
    df.to_csv('data4.csv',index=False)

    
    
    