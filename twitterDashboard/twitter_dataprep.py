import pandas as pd 
import json
import re


def process_raw(tweet=''):
    
    tweets=[]
    tweet_obj = json.loads(tweet)
    
    # Store the user screen name in 'user-screen_name'
    tweet_obj['user-screen_name'] = tweet_obj['user']['screen_name']
    
    # Check if this is a 140+ character tweet
    if 'extended_tweet' in tweet_obj:
            # Store the extended tweet text in 'extended_tweet-full_text'
        tweet_obj['extended_tweet-full_text'] = tweet_obj['extended_tweet']['full_text']

    if 'retweeted_status' in tweet_obj:
        # Store the retweet user screen name in 'retweeted_status-user-screen_name'
        tweet_obj['retweeted_status-user-screen_name'] = tweet_obj['retweeted_status']['user']['screen_name']

        # Store the retweet text in 'retweeted_status-text'
        tweet_obj['retweeted_status-text'] = tweet_obj['retweeted_status']['text']

    if 'quoted_status' in tweet_obj:
        # Store the retweet user screen name in 'retweeted_status-user-screen_name'
        tweet_obj['quoted_status-user-screen_name'] = tweet_obj['quoted_status']['user']['screen_name']

        # Store the retweet text in 'retweeted_status-text'
        tweet_obj['quoted_status-text'] = tweet_obj['quoted_status']['text']
    
    tweets.append(tweet_obj)


    return tweets

def repack_tweets(df=''):
    '''
    Repackage tweets dataframe for (1) better data types (2) remove no used columns (3) add datetime index
    '''
    
    drop_col = ['id_str','in_reply_to_status_id_str','in_reply_to_user_id_str','quoted_status_id_str']

    try:
        df['created_at']=pd.to_datetime(df['created_at'])
        df.drop(columns=drop_col,inplace=True)
        df.set_index(pd.DatetimeIndex(df['created_at']),inplace=True)

        if 'extended_tweet-full_text' in df.columns:
            df['extended_tweet-full_text']=df['extended_tweet-full_text'].apply(process_tweettext)
        df['text']=df['text'].apply(process_tweettext)

    except Exception as e:
        print('Error in convert tweets dataframe, Error {}'.format(e))
    return df

def process_tweettext(tweet_txt=''):
    tweet_txt = str(tweet_txt).lower() # convert text to lower-case
    tweet_txt = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet_txt) # remove URLs
    tweet_txt = re.sub('@[^\s]+', 'AT_USER', tweet_txt) # remove usernames
    tweet_txt = re.sub(r'#([^\s]+)', r'\1', tweet_txt) # remove the # in #hashtag

    return tweet_txt


def check_word_in_tweet(word, data):
    """Checks if a word is in a Twitter dataset's text. 
    Checks text and extended tweet (140+ character tweets) for tweets,
    retweets and quoted tweets.
    Returns a logical pandas Series.
    """

    try:
        contains_column = data['text'].str.contains(word, case = False,na=False)
    except Exception as e:
        print(data.info())
    
    
    if 'extended_tweet-full_text' in data.columns:
        contains_column |= data['extended_tweet-full_text'].str.contains(word, case = False,na=False)
    if 'quoted_status-text' in data.columns:
        contains_column |= data['quoted_status-text'].str.contains(word, case = False,na=False) 
    if 'retweeted_status-text' in data.columns:
        contains_column |= data['retweeted_status-text'].str.contains(word, case = False,na=False) 
    return contains_column
