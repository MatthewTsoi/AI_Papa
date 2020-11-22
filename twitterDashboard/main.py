import twitter_api
import dash_app
import time 
import threading 
import matplotlib
matplotlib.use('Agg')


class myThread (threading.Thread):
   def __init__(self, threadID, name, app=''):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      #self.counter = counter
      self.app = app 
   def run(self):
       dash_app.run(app=self.app)
      
      



if __name__ == "__main__":
#    twitter_api.start_api(duration=10) 
    

    collector=twitter_api.twitter_collector()
    collector.start(keywords=['biden','trump'],duration=0)

    ##wait for flush inital  data
    time.sleep(2)
    collector.refresh_summary()
    #app= dash_app.start_app(collector=collector)
    #print('started!')
    

    timer=600
    refresh_time=2

    app = dash_app.start_app(collector=collector)
    try:
        print('Starting')
        thread1 = myThread(2,'Dash App thread',app )
        thread1.start()
    except:
        print('Error starting dash app')
        pass

    
    while (timer >= 0):
        time.sleep(refresh_time/2)
        collector.refresh_summary()
        timer-=refresh_time
        time.sleep(refresh_time/2)
     #   dash_app.run(app=app)
        

    collector.stop() 

    
