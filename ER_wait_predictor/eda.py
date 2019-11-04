import pandas as pd 
import matplotlib

source_file = './data.csv'

## Load the source csv 
source_df=pd.read_csv(source_file)

print(source_df.info())

##Defines data type 
source_df['topWait']=source_df['topWait'].astype('category')
source_df['hospName']=source_df['hospName'].astype('category')
source_df['updateTime']=pd.to_datetime(source_df['updateTime']) 

#print(source_df.info())
#print(source_df.head(10))
#print(source_df['topWait'].unique())


##Manual mapping of waiting category  
wait_mapping = [['Around 1 hour', 1], ['Over 1 hour', 2], ['Over 2 hours', 3], ['Over 3 hours', 4], ['Over 4 hours', 5],['Over 5 hours', 6], ['Over 6 hours', 7], ['Over 7 hours', 8], ['Over 8 hours', 9]] 
wait_mapping_df = pd.DataFrame(wait_mapping, columns = ['Wait Time', 'Wait Time order'],index=None) 

source_df=pd.merge(source_df,wait_mapping_df,left_on=['topWait'],right_on=['Wait Time'])
source_df=source_df.drop(columns=['Wait Time'])
print(source_df.head(5))


plot_df=source_df[source_df['hospName']=='Queen Mary Hospital']
plot_df.plot(x='updateTime',y='Wait Time order')