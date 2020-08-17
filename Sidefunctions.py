import discord
import pandas as pd
import numpy as np
import json
import os
import re
from random import randrange
from config import *

def save_df(df, message, csv=1):
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

    

def load_df(message):
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


async def edit_msg(df, message):
    # Maybe convert it to an 'update_pin(message)' function, opening the csv file again?
    '''replace the content of the pinned message of a server with the updated information'''
    try:
        embed_list=df2embed(df)
        with open(os.path.join(script_path,'data',str(message.guild)+'_pin.json'), 'r') as j: ref=json.load(j)
        print('ref')
        print(ref)
        ref_list=ref['Message_Id']
        client=discord.Client()
        if len(embed_list)!=len(ref_list):                                           # If the new content wont fit in all the old messages, a new pin will be created, removing old pinned messages
            #for ref_number in ref_list:
            #    msg = await message.channel.fetch_message(ref_number)
            #    await msg.unpin()
            await pin_list(message)
        else:
            for i in range(len(ref_list)):
                ref_number=ref_list[i]
                embed=embed_list[i]
                msg = await message.channel.fetch_message(ref_number)
                await msg.edit(embed=embed)

        #await msg.edit(content=new_content)
        #await msg
        #print('New content: \n%s' % new_content)
        
        print('Message edited')
        return 0
    except Exception as e:
        print(e)
        print('The Pinned Message could not be edited. Maybe the message hasn\'t been pinned or the pin info file is corrupt/missing.')
        return 'Message could not be edited'

    
def line2embed(df,i):
    '''This function returns a discord embed containing the data from a dataframe in one single embed.'''
    try:
        description=''

        title_string=str(df.loc[i,'Title'])
        addedby_string=str(df.loc[i,'AddedBy'])
        netflix_path=df.loc[i,'Netflix']
        links=str(df.loc[i,'Link']).strip().split(' ')
        link_string=''

        if links[0]: link_string='[DL](' + ')  [DL]('.join(links) + ')'
        if netflix_path.startswith('/title/'):netflix_path='[NFLX](https://www.netflix.com'+netflix_path+')'

        description=description + '`' + str(i) + '.` ' + title_string + ' '
        description=description + '`(by ' + addedby_string[:addedby_string.find('#')] + ')` '
        description=description + netflix_path + ' ' + link_string + '\n'

        embed = discord.Embed(title="Random Element", colour=discord.Colour(0xCD01BD), description=description,)

        return embed
    except Exception as e:
        print(e)
        print('The element from Dataframe could not be converted into a message string. Make sure the Dataframe is formatted correctly')
        return '```Error creating message```'

def df2embed(df):
    '''This function returns a list of discord embeds containing the data from a dataframe separated every 10 elements'''
    try:
        description=''
        description_list=[]
        counter=-1
        max=10

        for i in df.index: 
            #if i!=1 and (i-1)%10==0:
            if counter==10:
                description_list.append(description)
                description=''
                counter=0
            title_string=str(df.loc[i,'Title'])
            addedby_string=str(df.loc[i,'AddedBy'])
            netflix_path=df.loc[i,'Netflix']
            links=str(df.loc[i,'Link']).strip().split(' ')
            link_string=''

            if links[0]: link_string='[DL](' + ')  [DL]('.join(links) + ')'
            if netflix_path.startswith('/title/'):netflix_path='[NFLX](https://www.netflix.com'+netflix_path+')'

            description=description + '`' + str(i) + '.` ' + title_string + ' '
            description=description + '`(by ' + addedby_string[:addedby_string.find('#')] + ')` '
            description=description + netflix_path + ' ' + link_string + '\n'
            counter=counter+1
        description_list.append(description)
        embed_list=[]
        for description in description_list:
            embed = discord.Embed(title="Watchlist", colour=discord.Colour(0xCD01BD), description=description,)
            embed_list.append(embed)
        #print(description_list)

        return embed_list
    except Exception as e:
        print(e)
        print('The Dataframe could not be converted into a message string. Make sure the Dataframe is formatted correctly')
        return '```Error creating message```'


async def test_embed(message):
    embed_list=df2embed(load_df(test))
    for embed in embed_list: await message.channel.send(embed=embed)

def capitalize(df):
    df['Title']=df['Title'].apply(cap)
    return df

def cap(s):
    return s.capitalize()


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False