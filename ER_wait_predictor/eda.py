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
    
    #source_df['updateTime']=source_df['updateTime'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %I:%M%p'))
    source_df['updateTime']=source_df['updateTime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    return source_df 


# %%Verify data 
source_path='./ER_wait_predictor/'


source_df=loadData(source_path+'source_data.csv')
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
#%time
print('============DATA PROFILE========================')
print('Num of timestamps:  '+str(len(source_df.sort_values(by=['updateTime']).updateTime.unique())  ) ) 
print('Num of ER/hospital: '+str(len(source_df.hospName.unique()))) 
print('Record count:'+str(len(source_df) ))
print('Last date point:'+str(source_df.updateTime.max()) )
print('Earliest date point:'+str(source_df.updateTime.min()) )
print('=================================================')
print('************Statistics for numeric columns********')
print(source_df.describe())

print('**************************************************')

print('##############Missing values######################')
for col in source_df.columns:
    print("Null value count for ["+col+"]: "+str(source_df[col].isna().sum()))

print('##################################################')


# %% Simple plot to validate the wait time outline 

#%time 
plot_df=source_df[source_df['hospName']=='Queen Mary Hospital']
#plot_df.plot(x='updateTime',y='Wait Time order')
plot_df.plot(x='updateTime',y='Wait Time order')


# %%data exploration and expend time dimenion 

def expandTimeDim(df = ''):
    df['updateTime_dow']= df.updateTime.dt.dayofweek
    df['updateTime_dayname']= df.updateTime.dt.day_name()
    df['updateTime_day']= df.updateTime.dt.day
    df['updateTime_month']= df.updateTime.dt.month
    df['updateTime_hour']= df.updateTime.dt.hour
    return df

source_df=expandTimeDim(source_df)


pd.set_option('display.max_rows', 2000)
source_df.info()

df3=source_df[source_df['hospName']=='Ruttonjee Hospital'].pivot_table(index=['topWait'],values=['hospName'],columns=['updateTime_dow'],aggfunc='count',fill_value=0)
df3.head(10)

# %% vislualize data in different dimension

import seaborn as sns
import matplotlib.pyplot as plt # for data visualization

##Change to True for analysis per hospital 
analyzePerHospial=False

df4=pd.DataFrame()
dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
time_dims=['dayname','day','month','hour']

for time_dim in time_dims:
    time_prespective = 'updateTime_'+time_dim

    ## Plot per day of week 
    fig, ax = plt.subplots(figsize=(6,6)) 
    ax.set_title("Overall wait dist. per "+time_dim,fontsize=20,pad=10)
    df3=source_df.pivot_table(index=['topWait'],values=['hospName'],columns=[time_prespective],aggfunc='count',fill_value=0)
    df3.columns = df3.columns.get_level_values(1)
    if time_dim == 'dayname':
        df3= df3.reindex(dow_order , axis=1)
    sns.heatmap(df3,fmt='d',cmap="YlGnBu")
    plt.show()
    #print(df3.head(10))

if analyzePerHospial:

    for time_dim in time_dims:
        time_prespective = 'updateTime_'+time_dim
        for hospname in source_df.hospName.unique():

            fig, ax = plt.subplots(figsize=(3,3)) 
            ax.set_title("Wait catagory dist. for "+hospname+' per '+time_dim,fontsize=9,pad=5)
            df3=source_df[source_df['hospName']==hospname].pivot_table(index=['topWait'],values=['hospName'],columns=[time_prespective],aggfunc='count',fill_value=0)
            df3.columns = df3.columns.get_level_values(1)
            if time_dim == 'dow':
                df3= df3.reindex(dow_order , axis=1)
            sns.heatmap(df3,fmt='d',cmap="YlGnBu")
            plt.show()


#
# %%Feature engineering 
source_df.info()


# %%Prepare the training set and test set 

# Import train_test_split function
from sklearn.model_selection import train_test_split



X=source_df[['hospName',  'updateTime_dow', 'updateTime_day','updateTime_month','updateTime_hour']]  # Features
y=source_df['topWait']  # Labels

X = pd.get_dummies(X,prefix=['hospName'], columns = ['hospName'], drop_first=True)

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

print("Training data set:"+str(X_train.shape))
print("Test data set:"+str(X_test.shape))
# %% Create a RandomForest model 

import time 

#Import Random Forest Model
from sklearn.ensemble import RandomForestClassifier

#Create a Gaussian Classifier
clf=RandomForestClassifier(n_estimators=100, n_jobs=6)

tic = time.time() 
#Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(X_train,y_train)

toc = time.time() 

print('Training time:'+str(round(toc-tic,2))+"s")
y_pred=clf.predict(X_test)


# %%

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics
# Model Accuracy, how often is the classifier correct?
print("Accuracy:"+str(round(clf.score( X=X_test,y=y_test),4)*100)+"%")




# %% Save the random forest model to file for re-use 

import pickle as pk

with open('./ER_wait_predictor/ER_predictor.dump', 'wb') as f:
    pk.dump(clf, f)




# %% [optional] load the random forest model and perform prediction

clf_load = pk.load(open('./ER_wait_predictor/ER_predictor.dump', 'rb'))
print("Accuracy:"+str(round(clf_load.score( X=X_test,y=y_test),4)*100)+"%")

clf_load=''
clf=''
# %%