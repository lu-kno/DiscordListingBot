import discord
import pandas as pd
import numpy as np
import json
import os
import re
import sys
import typing
from discord.ext import commands

from SideFunctions import *
from random import randrange
nflx_scraper=0
if nflx_scraper: from UNOGS_bot import *
from config import *

if re.search('WIP',str(sys.argv), re.IGNORECASE) or os.path.isfile(os.path.join(script_path,'WIP.txt')):
    bot = commands.Bot(command_prefix='!')
else: 
    bot = commands.Bot(command_prefix='b!')


class Message:
    def __init__(self, content):
        self.guild = 'CoronaCheck'
        self.channel = 'general'
        self.author = 'anauthor'
        self.content = content

test=Message('acontent')

@bot.command()
async def add(ctx, *, arg):
    '''Add elements separated by commas.
    You can add a link after the name and before any separating comma to include it on the list'''
    try:
        global df
        df=load_df(ctx)
        input=arg2input(arg)
        added=[]
        ignored=[]
        for i in input:
                links=[]
                for m in re.finditer('https?://[^\s\n]*', i): links.append(i[m.start():m.end()])
                if links: i=i[:i.find('http')-1].strip()
                if i.upper() not in [n.upper() for n in df['Title'].to_list()]: 
                    netflix_path=''
                    if nflx_scraper: netflix_path=bot.search(i)
                    df.loc[df.index.size]= [i.capitalize()] + [ctx.author] + [' '.join(links)] + [netflix_path]
                    added.append(i)
                else:
                    ignored.append(i)
        print('added')
        save_df(df, ctx)
        await edit_msg(df, ctx)
        response=''
        if added: response=response+'I added the following entries: %s\n' % added
        if ignored: response=response+'I ignored the double entries: %s\n' % ignored
        if not response:  'Sorry, I cant come up with a response to that'
        print(response)
        await ctx.send(response)
        return
    except Exception as e:
        print(e)
        print('An error ocurred adding entries to the list')
        await ctx.send('Error Adding to entry to the list')
        return 

@bot.command(name='random',aliases=['r', 'get_random','getr'])
async def get_random(ctx, reroll: typing.Optional[int]=0):
    '''Return a random element from the list.
    By clicking on the reaction you can reroll the random result.'''
    try:
        global df
        df=load_df(ctx)
        r=randrange(len(df))
        embed = line2embed(df,r)
        if not reroll:
            msg = await ctx.channel.send(embed=embed,nonce=11)
            await msg.add_reaction(chr(128257))
        else:
            await ctx.edit(embed=embed,nonce=11)
        #output=str(df.loc[r,'Title']) + '  (by ' + str(df.loc[r,'AddedBy']) + ')'
        #response='Random result:\n```%s```' % output
        response='** **'
        print(response)
        return
    except Exception as e:
        print(e)
        print('An error ocurred getting a random entry from the list')
        return 'Error  getting a random entry from the list'

@bot.command(aliases=['getvote','vote'])
async def getv(ctx, *, arg):
    '''Same as the 'get' command, but includes a reaction for each element to allow voting.'''
    input=arg2input(arg)
    await get_elements(ctx,input,vote=1)
    return 

@bot.command()
async def get(ctx, *, arg):
    '''This returns the elements specified and separated by a comma.
    If only using the index of the elements, only a separating blankspace is needed'''
    input=arg2input(arg)
    await get_elements(ctx,input,vote=0)
    return

@bot.command(aliases=['addlinks'])
async def addlink(ctx, *, arg):
    '''Adds a link to an existing element from the list.
    Usage: addlink <index|name> <links>'''
    try: 
        global df
        input=arg2input(arg)

        df=load_df(ctx)
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
        save_df(df, ctx)
        await edit_msg(df, ctx)
        print('edited')
        response=''
        if added_link: response=response+'I added the link(s) for the following entries: %s\n' % added_link
        if not_found: response=response+'I could not find the following entries: %s\n' % not_found
        if not response: 'Sorry, I cant come up with a response to that'
        print(response)
        await ctx.send(response)
        return

    except Exception as e:
        print(e)
        print('An error ocurred adding the link to the entry')
        await ctx.send('Error adding link to entry')
        return

@bot.command()
async def sort(ctx):
    '''Sorts all elements alphabetically'''
    try:
        global df
        df=load_df(ctx)
        df=df.sort_values('Title').reset_index(drop=True)
        save_df(df, ctx)
        await edit_msg(df,ctx)
        await show(ctx)
        await ctx.send('List has been sorted')
        return

    except Exception as e:
        print(e)
        print('An error ocurred sorting the entries on the list')
        await ctx.send('Error sorting list')
        return

@bot.command()
async def searchNFLX(ctx):
    '''Not Working! Search the corresponding NETFLIX link for the movie|serie titles'''
    try:
        if nflx_scraper:
            global df
            df=load_df(ctx)
            for i in df.index:
                df.loc[i,'Netflix']=bot.search(df.loc[i,'Title'])
            save_df(df, ctx)
            await edit_msg(df,ctx)
            return 'Netflix links have been added'
        else:
            return 'Netflix search is deactivated in the code'
    except Exception as e:
        print(e)
        print('An error ocurred adding netflix links')
        return 'Error adding Netflix links'

@bot.command(aliases=['rm'])
async def remove(ctx, *, arg):
    '''Removes one or more elements from the list. Titles separated by commas.
    When only using the index of the elements, only a blankspace is needed to separate elements.'''
    try: 
        global df
        input=arg2input(arg)
        df=load_df(ctx)
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
        save_df(df, ctx)
        await edit_msg(df, ctx)
        print('edited')
        response=''
        if removed: response=response+'I removed the following entries: %s\n' % removed
        if not_found: response=response+'I could not find the following entries: %s\n' % not_found
        if not response: 'Sorry, I cant come up with a response to that'
        print(response)
        await ctx.send(response)
        return

    except Exception as e:
        print(e)
        print('An error ocurred removing entries from the list')
        await ctx.send('Error removing entry from the list')
        return 

@bot.command(name='pin', aliases=['pin_list'])
async def pin_list(ctx):
    '''Sends list as embeds and pins them. This messages are kept up-to-date''' 

    df=load_df(ctx)

    try:
        embed_list = df2embed(df)
        print('embed list length %s' % len(embed_list))
        
        # Unpin old messages before pinning the new ones
        with open(os.path.join(script_path,'data',str(ctx.guild)+'_pin.json'), 'r') as j: pin_info=json.load(j)
        for ref_number in pin_info['Message_Id']:
                msg = await ctx.channel.fetch_message(ref_number)
                await msg.unpin()

        print('Message will be pinned')
        msg_list=[]
        for embed in embed_list:                                                        #loop added to separante embeds that are too long. embed_list is made for this
            the_msg = await ctx.channel.send(embed=embed)   #
            msg_list.append(the_msg)
            print('embed sent and pinned')
        for msg in reversed(msg_list):
            await msg.pin()                         #
        pin_info={'Message_Id': [msg.id for msg in msg_list],                           #the dict now contains a list of all related pinned messages
                    'Channel_Id': str(ctx.channel),    #
                    'Server_Id': str(ctx.guild)}       #

        with open(os.path.join(script_path,'data',str(ctx.guild)+'_pin.json'), 'w+') as j: json.dump(pin_info,j)
        print('pin_info')
        print(pin_info)
        await ctx.send('The message has been Pinned')
        return
        
    except Exception as e:
        print(e)
        print('Something went wrong. Message could not be Pinned')
        await ctx.send('Message could not be pinned')
        return


@bot.command()
async def show(ctx):
    '''Sends the lsit as embeds to the channel'''
    try:
        embed_list=df2embed(load_df(ctx))
        for embed in embed_list:
            await ctx.channel.send(embed=embed)
        return
    except Exception as e:
        print(e)
        print('The message could not be send')
        await ctx.send('The message could not be sent. List can not be shown')
        return


#def add_space(s):
#    s=s+' '
#    while len(s[s.rfind('\n')+1:])%4: s=s+' '
#    return s

#function_list={'add':add,
#               'addlink':addlink,
#               'get':get,
#               'getv':getv,
#               'random':get_random,
#               'sort':sort,
#               'searchNFLX':searchNFLX,
#               'remove':remove,
#               'pin':pin_list,
#               'show':show,
#               'embed':test_embed,
#               'help': help
#               }