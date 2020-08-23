import discord
import pandas as pd
import numpy as np
import json
import os
import re
from SideFunctions import *
from random import randrange
nflx_scraper=0
if nflx_scraper: from UNOGS_bot import *
from config import *



class Message:
    def __init__(self, content):
        self.guild = 'CoronaCheck'
        self.channel = 'general'
        self.author = 'anauthor'
        self.content = content

test=Message('acontent')

async def help(message,input):
    return 'the available commands are "b!add", "b!remove" and "b!show". \nWhen adding or removing entries, include the names after the command. \nTo enter multiple names, separate them with a comma (,) .\n Print this message again with the use of "b!help".'


async def add(message, input):
    try:
        global df
        df=load_df(message)
        added=[]
        ignored=[]
        for i in input:
                links=[]
                for m in re.finditer('https?://[^\s\n]*', i): links.append(i[m.start():m.end()])
                if links: i=i[:i.find('http')-1].strip()
                if i.upper() not in [n.upper() for n in df['Title'].to_list()]: 
                    netflix_path=''
                    if nflx_scraper: netflix_path=bot.search(i)
                    df.loc[df.index.size]= [i.capitalize()] + [message.author] + [' '.join(links)] + [netflix_path]
                    added.append(i)
                else:
                    ignored.append(i)
        print('added')
        save_df(df, message)
        await edit_msg(df, message)
        response=''
        if added: response=response+'I added the following entries: %s\n' % added
        if ignored: response=response+'I ignored the double entries: %s\n' % ignored
        if not response:  'Sorry, I cant come up with a response to that'
        print(response)
        return response
    except Exception as e:
        print(e)
        print('An error ocurred adding entries to the list')
        return 'Error Adding to entry to the list'

async def get_random(message, input, reroll=0):
    try:
        global df
        df=load_df(message)
        r=randrange(len(df))
        embed = line2embed(df,r)
        if not reroll:
            msg = await message.channel.send(embed=embed,nonce=11)
            await msg.add_reaction(chr(128257))
        else:
            await message.edit(embed=embed,nonce=11)
        #output=str(df.loc[r,'Title']) + '  (by ' + str(df.loc[r,'AddedBy']) + ')'
        #response='Random result:\n```%s```' % output
        response='** **'
        print(response)
        return response
    except Exception as e:
        print(e)
        print('An error ocurred getting a random entry from the list')
        return 'Error  getting a random entry from the list'

async def getv(message,input):
    response = await get(message,input,vote=1)
    return response

async def get(message, input, vote=0):
    try:
        global df
        df=load_df(message)

        tmp_df=pd.DataFrame(data={'Title':[],'AddedBy':[],'Link':[],'Netflix':[]})
        not_found=[]
        for i in input:
            line=[]
            n=None
            if is_number(i):
                if int(i) in df.index: 
                    n=int(i)
                    line=df.loc[n]
                else:
                    not_found.append(i)
            elif i.upper() in [n.upper() for n in df['Title'].to_list()]: 
                bool_arr=df.loc[:,'Title'].str.match(i, case=False)
                n=bool_arr[bool_arr==True].index[0]
                line=df.loc[n]
            else: not_found.append(i)
            if n is not None: tmp_df.loc[n]=df.loc[n]

        if vote: embed_list,emoji_list=df2embed(tmp_df,vote=vote)
        else: embed_list=df2embed(tmp_df,vote=vote)
        for i in range(len(embed_list)):
            msg= await message.channel.send(embed=embed_list[i])
            if vote:
                for emoji in emoji_list[i]:
                    await msg.add_reaction(emoji)
        if not_found: response='I could not find the following entries: %s\n' % not_found
        else: response='** **'

        print(response)
        return response
        
    except Exception as e:
        print(e)
        print('An error ocurred getting the entry from the list')
        return 'An error ocurred getting the entry from the list'

async def addlink(message, input):
    try: 
        global df
        df=load_df(message)
        added_link=[]
        not_found=[]
        for i in input:
            links=[]
            for m in re.finditer('https?://[^\s\n]*', i): links.append(i[m.start():m.end()])
            if links: i=i[:i.find('http')-1].strip()
            if is_number(i):
                if int(i) in df.index: 
                    added_link.append(str(df.loc[int(i),'Title']))
                    df.loc[int(i),'Link']=str(df.loc[int(i),'Link']) + ' ' + ' '.join(links)
                else:
                    not_found.append(i)
            elif i.upper() in [n.upper() for n in df['Title'].to_list()]: 
                bool_arr=df.loc[:,'Title'].str.match(i, case=False)
                index=bool_arr[bool_arr==True].index
                df.loc[int(index[0]),'Link']=str(df.loc[int(index[0]),'Link']) + ' ' + ' '.join(links)
                added_link.append(i)
            else: not_found.append(i)

        

        print('links added')
        save_df(df, message)
        await edit_msg(df, message)
        print('edited')
        response=''
        if added_link: response=response+'I added the link(s) for the following entries: %s\n' % added_link
        if not_found: response=response+'I could not find the following entries: %s\n' % not_found
        if not response: 'Sorry, I cant come up with a response to that'
        print(response)
        return response

    except Exception as e:
        print(e)
        print('An error ocurred adding the link to the entry')
        return 'Error adding link to entry'

async def sort(message, input):
    try:
        global df
        df=load_df(message)
        df=df.sort_values('Title').reset_index(drop=True)
        save_df(df, message)
        await edit_msg(df,message)
        await show(message)
        return 'List has been sorted'
    except Exception as e:
        print(e)
        print('An error ocurred sorting the entries on the list')
        return 'Error sorting list'

async def searchNFLX(message, input):
    try:
        if nflx_scraper:
            global df
            df=load_df(message)
            for i in df.index:
                df.loc[i,'Netflix']=bot.search(df.loc[i,'Title'])
            save_df(df, message)
            await edit_msg(df,message)
            return 'Netflix links have been added'
        else:
            return 'Netflix search is deactivated in the code'
    except Exception as e:
        print(e)
        print('An error ocurred adding netflix links')
        return 'Error adding Netflix links'

async def remove(message, input):
    try: 
        global df
        df=load_df(message)
        removed=[]
        not_found=[]
        for i in input:
            if is_number(i):
                if int(i) in df.index: 
                    removed.append(str(df.loc[int(i),'Title']))
                    df=df.drop(int(i))
                else:
                    not_found.append(i)
            elif i.upper() in [n.upper() for n in df['Title'].to_list()]: 
                bool_arr=df.loc[:,'Title'].str.match(i, case=False)
                df=df.drop(bool_arr[bool_arr==True].index)
                removed.append(i)
            else: not_found.append(i)

        df=df.reset_index(drop=1)

        print('removed')
        save_df(df, message)
        await edit_msg(df, message)
        print('edited')
        response=''
        if removed: response=response+'I removed the following entries: %s\n' % removed
        if not_found: response=response+'I could not find the following entries: %s\n' % not_found
        if not response: 'Sorry, I cant come up with a response to that'
        print(response)
        return response

    except Exception as e:
        print(e)
        print('An error ocurred removing entries from the list')
        return 'Error removing entry from the list'

async def pin_list(message, input):
    '''This Function sends a message with the servers list and pins it. 
    Aditionally, the reference id for the message, channel and server (guild) are saved 
    to edit the message with every change made'''
    df=load_df(message)

    try:
        embed_list = df2embed(df)
        print('embed list length %s' % len(embed_list))
        
        # Unpin old messages before pinning the new ones
        with open(os.path.join(script_path,'data',str(message.guild)+'_pin.json'), 'r') as j: pin_info=json.load(j)
        for ref_number in pin_info['Message_Id']:
                msg = await message.channel.fetch_message(ref_number)
                await msg.unpin()

        print('Message will be pinned')
        msg_list=[]
        for embed in embed_list:                                                        #loop added to separante embeds that are too long. embed_list is made for this
            the_msg = await message.channel.send(embed=embed)   #
            msg_list.append(the_msg)
            print('embed sent and pinned')
        for msg in reversed(msg_list):
            await msg.pin()                         #
        pin_info={'Message_Id': [msg.id for msg in msg_list],                           #the dict now contains a list of all related pinned messages
                    'Channel_Id': str(message.channel),    #
                    'Server_Id': str(message.guild)}       #

        with open(os.path.join(script_path,'data',str(message.guild)+'_pin.json'), 'w+') as j: json.dump(pin_info,j)
        print('pin_info')
        print(pin_info)
        return 'The message has been Pinned'
        
    except Exception as e:
        print(e)
        print('Something went wrong. Message could not be Pinned')
        return 'Message could not be pinned'



async def show(message, input):
    try:
        embed_list=df2embed(load_df(message))
        for embed in embed_list:
            await message.channel.send(embed=embed)
        return '** **'
    except Exception as e:
        print(e)
        print('The message could not be send')
        return '```The message could not be sent. List can not be shown```'


#def add_space(s):
#    s=s+' '
#    while len(s[s.rfind('\n')+1:])%4: s=s+' '
#    return s

function_list={'add':add,
               'addlink':addlink,
               'get':get,
               'getv':getv,
               'random':get_random,
               'sort':sort,
               'searchNFLX':searchNFLX,
               'remove':remove,
               'pin':pin_list,
               'show':show,
               'embed':test_embed,
               'help': help
               }