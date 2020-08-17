import discord
import pandas as pd
import numpy as np
import json
import os
import re
from SideFunctions import *
from random import randrange

class BotFunction():
    """description of class"""
    def __init__(self):
        return

    def save_df(self, df, message, csv=1):
        try:
            #df.to_pickle(os.path.join(script_path,'data',str(message.guild)+'.pck'),compression=None)
            if csv: 
                with open(os.path.join(script_path,'data',str(message.guild)+'.csv'), 'w+') as csv: df.to_csv(csv, index=0)
            else:
                df.to_json(os.path.join(script_path,'data',str(message.guild)+'.json'), orient='index')
            print('df saved')
            return
        except Exception as e:
            print(e)
            print('There was a problem saving the Data to the pickle file')
            return 'Error'

    def load_df(self,message):
        try: 
            if os.path.isfile(os.path.join(script_path,'data',str(message.guild)+'.json')):
                df=pd.read_pickle(os.path.join(script_path,'data',str(message.guild)+'.json'), orient='index')
            elif os.path.isfile(os.path.join(script_path,'data',str(message.guild)+'.pck')):
                df=pd.read_pickle(os.path.join(script_path,'data',str(message.guild)+'.pck'),compression=None)
            else:
                with open(os.path.join(script_path,'data',str(message.guild)+'.csv')) as csv: df=pd.read_csv(csv)

            print('df loaded')
        except Exception as e: 
            print(e)
            df=pd.DataFrame(data={'Title':[],'AddedBy':[],'Link':[],'Netflix':[]})
            print('new df created')
        if 'Link' not in df.columns:
            l=['' for i in range(df.index.size)]
            df['Link']=l
        if 'Netflix' not in df.columns:
            l=['' for i in range(df.index.size)]
            df['Netflix']=l
        df = df.replace(np.nan, '', regex=True)
        df = capitalize(df)
        return df


    def run(self):
        return