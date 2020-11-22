import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
import pandas as pd
import twitter_api

from wordcloud import WordCloud
#import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt

import io
import base64
import numpy as np

def start_app(collector=''):

#    app = dash.Dash()
    
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 
    
    app.layout = html.Div([ 
                        html.Div([ 
                        html.H1(children='Twitter feeds dashboard'),
                        html.Div([
                            html.H4(children='''Sampled tweets'''),
                            dcc.Graph(id='tweets-freq-graph', animate=True),
                            dcc.Interval(id='graph-update1',interval=1*3000)], className = 'seven columns'),
                        html.Div([
                            html.H4(children='''Counters'''),
                            dcc.Graph(id='counter-table'),
                            dcc.Interval(id='graph-update',interval=1*3000)], className = 'four columns')],
                        className='row'),
                        html.Div([ 
                            html.Div([
                            html.H4(children='''Trump's WordCloud'''),
                            html.Img(id= 'trump_wc', className="img-responsive", style={'max-height': '500px', 'margin': '1 auto'})], className = 'six columns'),
                            html.Div([
                            html.H4(children='''Biden's WordCloud'''),
                            html.Img(id= 'biden_wc', className="img-responsive", style={'max-height': '500px', 'margin': '1 auto'})], className = 'six columns')],
                        className='row'),
                        html.Div([ 
                            html.Div([
                            html.H5(children='''Trump's top 10 word'''),
                            dcc.Graph(id='wc_table'),
                            dcc.Interval(id='graph-update2',interval=1*3000)], className = 'six columns'),
                            html.Div([
                            html.H5(children='''Biden's top 10 word'''),
                            dcc.Graph(id='wc_table2'),
                            dcc.Interval(id='graph-update3',interval=1*3000)], className = 'six columns')],
                        className='row')
                ])


    @app.callback([Output('counter-table', 'figure'),Output('tweets-freq-graph', 'figure'),Output('wc_table', 'figure'),Output('wc_table2','figure'),Output('trump_wc','src'),Output('biden_wc','src')],
    [Input('graph-update' , 'n_intervals')])
    def update_metric(n):
        def gen_wordcloudImage(df=''):

            
            try:
                wc_dict = dict(zip(df.index.tolist(),df['counts'].tolist()))
                wc=WordCloud(width=900, height=550, max_words=200,background_color="white", contour_color='white', colormap="magma").generate_from_frequencies(wc_dict)

                wc.to_file('temp.png')
                output=base64.b64encode(open('temp.png', 'rb').read()).decode('ascii')


            except Exception as e:
                print(str(e))
            return output 







        ##Obtain data and generate KPI 
        df_freq=collector.listen.cache.get_df_cache(ns='twitter_cache:summary:',key='tweets_freq')
        total_tweets=int(collector.listen.cache.get_cache(ns='twitter_cache:summary:',key='total_tweets'))
        trump_tweets=int(collector.listen.cache.get_cache(ns='twitter_cache:summary:',key='trump_tweets'))
        biden_tweets=int(collector.listen.cache.get_cache(ns='twitter_cache:summary:',key='biden_tweets'))
        trump_wc=collector.listen.cache.get_df_cache(ns='twitter_cache:summary:',key='trump_wc')
        biden_wc=collector.listen.cache.get_df_cache(ns='twitter_cache:summary:',key='biden_wc')

        ##Generate line graph
        data = plotly.graph_objs.Scatter(
            x=list(df_freq.index),
            y=list(df_freq.freq),
            name='Scatter',
            mode= 'lines+markers'
            )

        ##Generate wordcloud 
        trump_wc_fig=gen_wordcloudImage(trump_wc)
        biden_wc_fig=gen_wordcloudImage(biden_wc)

        
        freq_fig={'data': [data],'layout' : go.Layout(xaxis=dict(range=[df_freq.index.min(),df_freq.index.max()]),
                                                yaxis=dict(range=[0,df_freq.freq.max()*1.2]),)}

        count_tab =go.Figure(data=[go.Table(header=dict(values=['Total tweets Processed', 'Trump Cnt','Biden Cnt', 'Ratio']), \
            cells=dict(values=[total_tweets,trump_tweets,biden_tweets,'1:'+str(round(biden_tweets/trump_tweets,2))]))
                     ])
        wc_tab =go.Figure(data=[go.Table(header=dict(values=['keyword','counts']), \
            cells=dict(values=[trump_wc.index,trump_wc.counts]))
                     ])
                     
        wc_tab2 =go.Figure(data=[go.Table(header=dict(values=['keyword','counts']), \
            cells=dict(values=[biden_wc.index,biden_wc.counts]))
                     ])
        return count_tab,freq_fig,wc_tab, wc_tab2, "data:image/png;base64,{}".format(trump_wc_fig), "data:image/png;base64,{}".format(biden_wc_fig)


                     
    return app

def run(app=''):
    app.run_server()


