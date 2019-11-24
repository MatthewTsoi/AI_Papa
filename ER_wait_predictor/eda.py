# %% 
import pandas as pd 
import matplotlib
from datetime import datetime

def loadData(source_path='',nrows=0):

    if nrows==0:
        source_df=pd.read_csv(source_path,parse_dates=False)
    else:
        source_df=pd.read_csv(source_path,parse_dates=False,nrows=nrows)
    #print(source_df.info())

    source_df['topWait']=source_df['topWait'].astype('category')
    source_df['hospName']=source_df['hospName'].astype('category')
    #3/4/2019 6:45am (3rd Apr 2019)
    #source_df['updateTime']=pd.to_datetime(source_df['updateTime'],dayfirst=True, format='%d/%m/%Y %H:%M%p',infer_datetime_format=True) 
    #source_df['updateTime_org']=source_df['updateTime']

    source_df['updateTime']=source_df['updateTime'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M%p'))
    return source_df 


# %%Verify data 
source_df = loadData('/Users/Matthew/Documents/AI_Papa/ER_wait_predictor/data.csv')
source_df2= loadData('/Users/Matthew/Documents/AI_Papa/ER_wait_predictor/data2.csv')


source_df3=source_df2[~source_df2['updateTime'].isin(source_df['updateTime'].unique())]

#print(len(source_df3.updateTime))
#print(len(source_df2.updateTime))

source_df=source_df.append(source_df3)

print(source_df.info())
print('Max wait record:'+str(source_df.updateTime.max()) )
print('Min wait record:'+str(source_df.updateTime.min()) )
print('Record count:'+str(len(source_df) ))





# %%Manual mapping of waiting category  
wait_mapping = [['Around 1 hour', 1], ['Over 1 hour', 2], ['Over 2 hours', 3], ['Over 3 hours', 4], ['Over 4 hours', 5],['Over 5 hours', 6], ['Over 6 hours', 7], ['Over 7 hours', 8], ['Over 8 hours', 9]] 
wait_mapping_df = pd.DataFrame(wait_mapping, columns = ['Wait Time', 'Wait Time order'],index=None) 

source_df=pd.merge(source_df,wait_mapping_df,left_on=['topWait'],right_on=['Wait Time'])
source_df=source_df.drop(columns=['Wait Time'])


# %% Data Profiling 
%time
print('Num of data points:  '+str(len(source_df.sort_values(by=['updateTime']).updateTime.unique())  ) ) 
print('Num of ER/hospital: '+str(len(source_df.hospName.unique()))) 
print('Record count:'+str(len(source_df) ))
print('Last date point:'+str(source_df.updateTime.max()) )
print('Earliest date point:'+str(source_df.updateTime.min()) )


#print(source_df.updateTime.tail(10)) 
#print(source_df.sort_values(by=['updateTime']).updateTime.tail(10)) 
#source_df.info()
#print(source_df.head(5))

# %%

%time 
plot_df=source_df[source_df['hospName']=='Queen Mary Hospital']
#plot_df.plot(x='updateTime',y='Wait Time order')
plot_df.plot(x='updateTime',y='Wait Time order')


# %%data exploration
#source_df.info()
#print('Hospital count:' +str(len(source_df.hospName.unique()))) 

source_df['updateTime_dow']= source_df.updateTime.dt.day_name()


#source_df.head(10)
#print(source_df.updateTime.max()) 
#print(source_df.updateTime.min()) 
#print(source_df.tail(10).updateTime)
pd.set_option('display.max_rows', 2000)
source_df.info()

#df2=source_df.groupby(by=['updateTime_dow','topWait']).count()[['hospName']].reset_index()
#df2.head(500)

source_df.head(10)
df3=source_df[source_df['hospName']=='Ruttonjee Hospital'].pivot_table(index=['topWait'],values=['hospName'],columns=['updateTime_dow'],aggfunc='count',fill_value=0)
df3.head(10)
#wait_dow_df=source_df.groupby(by=['updateTime_dow'])['updateTime_dow'].value_counts()
#wait_dow_df=source_df.groupby(by=['updateTime_dow'])['topWait'].value_counts(sort=True)
#print(wait_dow_df.sort_values(['Wait Time order']).head(10))
# %% vislualize data 

import seaborn as sns
import matplotlib.pyplot as plt # for data visualization


#fig, ax = plt.subplots(figsize=(6,6)) 

for hospname in source_df.hospName.unique():
    #print(hospname)
    fig, ax = plt.subplots(figsize=(6,6)) 
    ax.set_title("Wait catagory distribution for "+hospname,fontsize=20,pad=10)
    df3=source_df[source_df['hospName']==hospname].pivot_table(index=['topWait'],values=['hospName'],columns=['updateTime_dow'],aggfunc='count',fill_value=0).reset_index().rename_axis(None,1)
    sns.heatmap(df3,fmt='d',cmap="YlGnBu")
    plt.show()
#plot_df=df2[df2['updateTime_dow']=='Monday'][['updateTime_dow','hospName']]
#sns.distplot(source_df[['topWait']].head(2000),kde=False)

# %%

df3.head(10)