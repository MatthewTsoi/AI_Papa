from tweepy import OAuthHandler
from tweepy import API
from tweepy import Stream

from tweepy.streaming import StreamListener
import json
import time
import sys
import pandas as pd
import numpy as np
import twitter_dataprep as dataprep

import twitter_cache as tc



class SListener(StreamListener):
    def __init__(self, api = None, fprefix = 'streamer'):
        self.api = api or API()
        self.counter = 0
        self.fprefix = fprefix
        self.output  = open('tweets.json', 'w')
        self.cache = tc.twitter_cache() 

        self.cache.clean_allcache()

        


    def on_data(self, data):
        if  'in_reply_to_status' in data:
            ##Debug
            #print('=================='+str(self.counter)+'=========')
            #print(data)
            self.on_status(data)
        elif 'delete' in data:
            delete = json.loads(data)['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False
        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False
        elif 'warning' in data:
            warning = json.loads(data)['warnings']
            print("WARNING: %s" % warning['message'])
            return


    def on_status(self, status):
        self.output.write(status)
        self.counter += 1
        #if self.counter >= 20000:
        if self.counter >= 1000:
            self.output.close()
            self.output  = open('%s_%s.json' % (self.fprefix, time.strftime('%Y%m%d-%H%M%S')), 'w')
            self.counter = 0
        #print(self.counter)

        df_tweets=pd.DataFrame(dataprep.process_raw(status))
        #self.cache.add_df_cache(key=str(df_tweets.id.max()),df=df_tweets)
        self.cache.add_cache(ns='twitter_cache:raw:',key=str(df_tweets.id.max()),value=str(df_tweets.to_json(orient='records')))
    
        return


    def on_delete(self, status_id, user_id):
        print("Delete notice")
        return


    #def on_limit(self, track):
        #print("WARNING: Limitation notice received, tweets missed: %d" % track)
    #    return


    def on_error(self, status_code):
        print('Encountered error with status code:', status_code)
        return 


    def on_timeout(self):
        print("Timeout, sleeping for 60 seconds...")
        time.sleep(60)
        return



class twitter_collector():
    def __init__(self,cache=''):
        
        ##Init  stream object  
        # Consumer key authentication(consumer_key,consumer_secret can be collected from our twitter developer profile)
        auth = OAuthHandler('o9nR34wWz2QYKWIX64VzRFgv6', 'bfmDRlKnhQsFTfiaq95GdNV4VJqUu20QA9BfYvQvVjlN8MTgOs')
        # Access key authentication(access_token,access_token_secret can be collected from our twitter developer profile)
        auth.set_access_token('1278060518096244737-yRVyRQFWvKh3tUXUWvk2tIsNyVTSjT', 'etOFJPVTnxfkplTjDvprO0FfIq98vSHSASPmuYFubliXe')
        # Set up the API with the authentication handler
        api = API(auth)

        # Instantiate the cache object for twitter stream 
        #self.cache = tc.twitter_cache() 

        # Instantiate the SListener object 
        self.listen = SListener(api=api)
        
        # Instantiate the Stream object
        self.stream = Stream(auth, self.listen)

        # Initiate collector counters 
        self.listen.cache.add_cache(ns='twitter_cache:summary:',key='total_tweets',value=0)
        self.listen.cache.add_cache(ns='twitter_cache:summary:',key='trump_tweets',value=0)
        self.listen.cache.add_cache(ns='twitter_cache:summary:',key='biden_tweets',value=0)

    def start(self,keywords=['biden','trump'],duration=0):
        
        # Begin collecting data
        self.stream.filter(track = keywords, is_async=True) 

        # if collector object started with duration specified, stop after X seconds
        if duration>0:
            time.sleep(duration)
            self.stream.disconnect() 
            
            print('streaming stopped after '+str(duration)+"s")
            self.summary()
            
        
    def stop(self):

        #Disconnect the streaming object
        self.stream.disconnect()

        time.sleep(1)
        print("Twitter collector stopped!")

        self.summary()

    def refresh_summary(self,clear_raw=True):
        '''
        Load raw tweets and process summary 
        Delete raw tweets from redis cache if [clear_raw=True]
        '''

        try:
            df_summary=dataprep.repack_tweets(self.listen.cache.get_rawcache(ns='twitter_cache:raw:',return_df=True))
        except Exception as e:
            print ('Error to load raw tweets and refresh summary! Error Msg: {0}'.format(e))
            return 

        if clear_raw:
            self.listen.cache.clear_rawcache(ns='twitter_cache:raw:')

        # Update counters 
        total_tweets=int(self.listen.cache.get_cache(ns='twitter_cache:summary:',key='total_tweets'))+len(df_summary.index)
        trump_tweets=int(self.listen.cache.get_cache(ns='twitter_cache:summary:',key='trump_tweets'))+np.sum(dataprep.check_word_in_tweet('trump',df_summary))
        biden_tweets=int(self.listen.cache.get_cache(ns='twitter_cache:summary:',key='biden_tweets'))+np.sum(dataprep.check_word_in_tweet('biden',df_summary))
        self.listen.cache.add_cache(ns='twitter_cache:summary:',key='total_tweets',value=str(total_tweets))
        self.listen.cache.add_cache(ns='twitter_cache:summary:',key='trump_tweets',value=str(trump_tweets))
        self.listen.cache.add_cache(ns='twitter_cache:summary:',key='biden_tweets',value=str(biden_tweets))

        ## Build the word count histogram 
        trump_wcloud = df_summary[dataprep.check_word_in_tweet('trump',df_summary)].text.str.split(expand=True).stack().value_counts().rename_axis('keyword').to_frame('counts')
        biden_wcloud = df_summary[dataprep.check_word_in_tweet('biden',df_summary)].text.str.split(expand=True).stack().value_counts().rename_axis('keyword').to_frame('counts')

        exclude_word = ['AT_USER','rt','URL','is','am','are','was','were','a','an','of','the','to','in','for','and','i','you','at','this','there','that','he','she','it','his','her','will','on','by','about','with','and','or']
        trump_wcloud=trump_wcloud[~trump_wcloud.index.isin(exclude_word)].nlargest(10,'counts')
        biden_wcloud=biden_wcloud[~biden_wcloud.index.isin(exclude_word)].nlargest(10,'counts')

        trump_wc = self.listen.cache.get_df_cache(ns='twitter_cache:summary:',key='trump_wc')
        biden_wc = self.listen.cache.get_df_cache(ns='twitter_cache:summary:',key='biden_wc')

        if not trump_wc.empty:
            trump_wc = pd.concat([trump_wc,trump_wcloud]).groupby(level=0).sum().nlargest(10,'counts')
        else:
            trump_wc=trump_wcloud
        self.listen.cache.add_df_cache(ns='twitter_cache:summary:',key='trump_wc',df=trump_wc)      

        if not biden_wc.empty:
            biden_wc = pd.concat([biden_wc,biden_wcloud]).groupby(level=0).sum().nlargest(10,'counts')
        else:
            biden_wc=biden_wcloud
        self.listen.cache.add_df_cache(ns='twitter_cache:summary:',key='biden_wc',df=biden_wc)        

        #print(trump_wc)
        #print(biden_wc)

        prev_freq=self.listen.cache.get_df_cache(ns='twitter_cache:summary:',key='tweets_freq')
        if  not prev_freq.empty:
            latest_freq = pd.concat([prev_freq,df_summary['id'].resample('1S').count().to_frame(name='freq')])
            #print(df_summary['id'].resample('1S').count().to_frame(name='freq'))
        else:
            latest_freq=df_summary['id'].resample('1S').count().to_frame(name='freq')
        
        latest_freq=latest_freq.groupby('created_at').sum()#.reset_index('created_at')
        self.listen.cache.add_df_cache(ns='twitter_cache:summary:',key='tweets_freq',df=latest_freq)

        return total_tweets,trump_tweets, biden_tweets, latest_freq


    def summary(self):
        print('----------SUMMARY-----------')
        print("Total tweets: {0}. Trump tweets count {1}. Biden tweets count {2}. \n\n Frequency timeline: \n {3}".format(*self.refresh_summary()[:4],))
        print('-----------------------------')



