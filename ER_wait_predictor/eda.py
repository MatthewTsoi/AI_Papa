# %% 
import pandas as pd 
import matplotlib

def loadData(source_path=''):

    source_df=pd.read_csv(source_path)
    print(source_df.info())

    source_df['topWait']=source_df['topWait'].astype('category')
    source_df['hospName']=source_df['hospName'].astype('category')
    source_df['updateTime']=pd.to_datetime(source_df['updateTime']) 

    print(source_df['updateTime'].max())
    print(source_df['updateTime'].min())

    return source_df 


# %%Verify data 
source_df = loadData('/Users/Matthew/Documents/AI_Papa/ER_wait_predictor/data.csv')
source_df2= loadData('/Users/Matthew/Documents/AI_Papa/ER_wait_predictor/data2.csv')

print(source_df.info())
print('Max wait record:'+str(source_df.updateTime.max()) )
print('Min wait record:'+str(source_df.updateTime.min()) )

source_df3=source_df2[~source_df2['updateTime'].isin(source_df['updateTime'].unique())]

print(len(source_df3.updateTime))
print(len(source_df2.updateTime))

source_df=source_df.append(source_df3)

print(len(source_df.updateTime))

# %%Manual mapping of waiting category  
wait_mapping = [['Around 1 hour', 1], ['Over 1 hour', 2], ['Over 2 hours', 3], ['Over 3 hours', 4], ['Over 4 hours', 5],['Over 5 hours', 6], ['Over 6 hours', 7], ['Over 7 hours', 8], ['Over 8 hours', 9]] 
wait_mapping_df = pd.DataFrame(wait_mapping, columns = ['Wait Time', 'Wait Time order'],index=None) 

source_df=pd.merge(source_df,wait_mapping_df,left_on=['topWait'],right_on=['Wait Time'])
source_df=source_df.drop(columns=['Wait Time'])
print(source_df.head(5))


#plot_df=source_df[source_df['hospName']=='Queen Mary Hospital']
#plot_df.plot(x='updateTime',y='Wait Time order')


# %%data exploration

#print(source_df.hospName.unique()) 
#print(source_df.updateTime.max()) 
#print(source_df.updateTime.min()) 
#print(source_df.tail(10).updateTime)
source_df['updateDate']=source_df.updateTime.dt.date
source_df.updateDate


# %%
source_df.sort_values(by=['updateTime']).tail(50)