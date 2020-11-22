import redis   # import redis module 
import pyarrow as pa
import pandas as pd
import time
import json 

def init_connt(host='localhost',port=6379):
    return 

class twitter_cache():
    def __init__(self,host='localhost',port=6379):
        self.r = redis.Redis(host=host, port=port, decode_responses=False)

    def add_cache(self,ns='twitter_cache:',key='', value=''):
        self.r.set(ns+key,value)
        return 

    def add_df_cache(self,ns='twitter_cache:',key='',df=''):
        context = pa.default_serialization_context()
        self.r.set(ns+key, context.serialize(df).to_buffer().to_pybytes())
    
    def get_cache(self,ns='twitter_cache:',key=''):
        return self.r.get(ns+key)
    
    def get_df_cache(self,ns='twitter_cache:df:',key=''):
        context = pa.default_serialization_context()
        if type(key) is bytes:
            get_key=key
        else:
            get_key=ns+key 
        if self.r.get(get_key):
            return context.deserialize(self.r.get(get_key))
        else:
            return pd.DataFrame()

    def get_rawcache(self,ns='twitter_cache:raw:',return_df=False):
        keys= self.r.keys(pattern=ns+"*")
        if not return_df:
            return self.r.mget(keys)
        else:
            #construct a dataframe as return 
            rawdata=self.r.mget(keys)
            rawdata=[x[1:-1].decode("utf-8")  for x in rawdata]
            rawdata='['+','.join(map(str, rawdata))+']' 
            return pd.read_json(rawdata,orient='records',dtype=True)
    def clear_rawcache(self,ns='twitter_cache:raw:'):
        keys= self.r.keys(pattern=ns+"*")
        try:
            self.r.delete(*keys)
        except Exception as e:
            print('Error in clearing raw data in cache with namespace {1}. Error Msg: {0}'.format(e,ns))


    def get_allcache(self, df_only=False):
        keys = self.r.keys('*')
        out_dict = '['
        #out_df = pd.DataFrame() 

        tmp_dict = '['
        i= 0
        
        for key in keys:
            #decode bytes to Utf-8 from redis cache 
#            str_key=key.decode("utf-8") 
            tik = time.time()
            str_type = self.r.type(key).decode("utf-8") 
            print('decode time: '+str(round(time.time()-tik,2)*1000000)+'us')

            if str_type == "string":
                if b"twitter_cache:df:" in key:
                    #val_tmp=self.get_df_cache(key=key)
                    #out_dict[key]=val_tmp
                    try:
#                        out_df = pd.concat([out_df,self.get_df_cache(key=key)],ignore_index=True)
                        ##tmp_dict[i]=self.get_df_cache(key=key).to_dict('list')
                        #tmp_dict.append(self.get_df_cache(key=key).to_dict('index'))
                        tmp_dict=tmp_dict+self.get_df_cache(key=key).to_json(orient='records')[1:-1]+','
                        #print(pd.DataFrame.from_records(tmp_dict[i]))
                        i+=1
                    except Exception as e:
                        print('****ERROR****')
                        print('Error merge DataFrame from cache. {}'.format(e))
                        pass 
                else:
                    if not df_only:
                        #out_dict[key]=self.r.get(key)
                        #out_dict.append(self.r.get(key).decode("utf-8") )
                        tik=time.time()
                        out_dict=out_dict+self.r.get(key).decode("utf-8")[1:-1]+','
                        print('decode time: '+str(round(time.time()-tik,8)*1000)+'ms')
                        #out_dict+=str(self.r.get(key).decode("utf-8"))
                        #rint(pd.read_json(self.r.get(key).decode("utf-8")))

            #if str_type == "hash":
            #    val = self.r.hgetall(key)
            #if str_type == "zset":
            #    val = self.r.zrange(key, 0, -1)
            #if str_type == "list":
            #    val = self.r.lrange(key, 0, -1)
            #if str_type == "set":
            #    val = self.r.smembers(key)
        
        #out_df=pd.DataFrame.from_dict(tmp_dict,'columns')
        #print(tmp_dict)
        #out_df=pd.DataFrame.from_records(tmp_dict)
        out_dict = out_dict[:-1]+']'

        if tmp_dict != '[': 
            tmp_dict=tmp_dict[:-1]+']'
            return out_dict, pd.read_json(tmp_dict)
        else:
            return out_dict, None 


    def clean_allcache(self,ns='twitter_cache:',CHUNK_SIZE=5000):
        cursor = '0'
        ns_keys = ns + '*'
        while cursor != 0:
            cursor, keys = self.r.scan(cursor=cursor, match=ns_keys, count=CHUNK_SIZE)
            if keys:
                self.r.delete(*keys)
        return True

if __name__ == "__main__":
    t_cache = twitter_cache()

    
    df=pd.DataFrame({'A':[1,2,3]})
    df2=pd.DataFrame({'A':[4,5,6]})
    t_cache.add_df_cache(key='test_df',df=df)
    t_cache.add_df_cache(key='test_df2',df=df2)
    t_cache.add_cache(key='test-1',value='testing')
    print(t_cache.get_allcache(df_only=True))
    print(t_cache.get_allcache(df_only=False))
    t_cache.clean_allcache()
    
    
