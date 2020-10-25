import discord
import pandas as pd
import numpy as np
import json
import os
import re
import sys
import typing
import datetime
from dateutil.parser import parse
import asyncio

from random import randrange
from discord.ext import commands

from config import *
from SideFunctions import *

nflx_scraper=0
if nflx_scraper: from UNOGS_bot import *

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

class Reminders:
    def __init__(self):
        try: 
            with open(os.path.join(script_path,'data','reminders.csv')) as csv: self.df=pd.read_csv(csv)
            print('Reminders loaded')
        except Exception as e: 
            print(e)
            self.df=pd.DataFrame(data={'Guild':[],'Channel':[],'Author':[],'Members':[],'Content':[],'Set_date':[]})
            print('New reminders created')
        
        self.df=self.df.sort_values('Set_date').reset_index(drop=1)
        self.df = self.df.replace(np.nan, '', regex=True)
        return

    def add_msg(self, ctx, members,content, set_date):
        new=pd.DataFrame(data={\
            'Guild':[ctx.guild.id],\
            'Channel':[ctx.channel.mention],\
            'Author':[ctx.author.mention],\
            'Members':[' '.join([m.mention for m in members])],\
            'Content':[content],\
            'Set_date':[str(set_date)]})

        self.df=self.df.append(new)
        self.df=self.df.sort_values('Set_date').reset_index(drop=1)
        self.save()
        return

    async def check(self):
        set_date=parse(self.df.loc[0,'Set_date'])
        curr_date=datetime.datetime.now()
        if curr_date>set_date:
            await self.remind(0)
            self.save()
        return

        
    def save(self):
        with open(os.path.join(script_path,'data','reminders.csv'), 'w+') as csv: self.df.to_csv(csv, index=0)

    async def remind(self,index):
        d1=self.df.loc[index]
        response=' '.join(['Reminder from', d1['Author'], 'to', d1['Members'], ':', d1['Content']+'\n'+d1['Set_date']])
        guild = await bot.fetch_guild(d1['Guild'])
        channel =  await guild.fetch_channel(d1['Channel'])
        await channel.send(response)
        self.df=self.df.drop(index).reset_index()
        return

reminders=Reminders()

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
                if links: i=i[:i.find('http')-1].strip().capitalize()
                
                if i.upper() not in [n.upper() for n in df['Title'].to_list()]: 
                    netflix_path=''
                    if nflx_scraper: netflix_path=bot.search(i)
                    df.loc[df.index.size]= [i.capitalize()] + [ctx.author] + [' '.join(links)] + [netflix_path]
                    added.append(i)
                elif links:
                    curr_links=[link for link in df.loc[df['Title']==i,'Link'].to_string(index=0).split(sep=' ') if link]
                    
                    [curr_links.append(link) for link in links if link not in curr_links]

                    df.loc[df['Title']==i,'Link']=' '.join(curr_links)
                    added.append(i)
                else:
                    ignored.append(i)
        print('added')
        save_df(df, ctx)
        await edit_msg(df, ctx)
        response=''
        if added: 
            await get_elements(ctx, added, vote=0, embed_title='Added')
            #response=response+'I added the following entries: %s\n' % added
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
async def _pin_list(ctx):
    '''Sends list as embeds and pins them. This messages are kept up-to-date''' 
    try:
        await pin_list(ctx)
        
    except Exception as e:
        print(e)
        print('side Funciton error. pin failed')
        await ctx.send('Message could not be pinned')
        return

@bot.command()
async def show(ctx):
    '''Sends the list as embeds to the channel'''
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


#@bot.command(name='reminder', aliases=['remindme','remind'])
#async def set_reminder(ctx, members: commands.Greedy[discord.Member], *, text='I dont know what to remind you about'):
    
#    def check(m):
#        return m.author == ctx.author

#    response1='When should I remind you about this? (Respond with "!" to delete the reminder. Respond with "h" for help)'
#    await ctx.send(response1)
#    msg = await bot.wait_for('message', check=check)
    
#    if msg.content=='h':
#        await ctx.send('tell me the date in "year-month-day" format or how long to wait for in "--w --d --h --m --s" format (weeks, days, hours, minutes, seconds)')
#        msg = await bot.wait_for('message', check=check)

#    if msg.content.startswith('!'):
#        await ctx.send("I'll try to forget this ever happened")
#        print('Reminder canceled')
#        return

#    curr_date=datetime.datetime.now()
#    content=msg.content
#    delta = parse_timedelta(content)
#    if delta:
#        print(curr_date)
#        print(delta)
#        set_date=curr_date+delta

#    else:
#        try: set_date=parse(content)
#        except Exception as e:
#            print('Date not parsed:\n'+e)
#            await ctx.send('I could not understand that. I will ignore this reminder')
#            return

#    if set_date<curr_date:
#        print('set_date is in the past')
#        await ctx.send('This date is in the past. That is not how time works')
#        return


#    reminders.add_msg(ctx, members, text, set_date)


#    await ctx.send(';'.join([str(set_date),str(ctx.guild.id), ctx.channel.mention, ctx.author.mention,','.join([m.mention for m in members]),text])+'\n')
#    await ctx.send('I will remind you on {}'.format(str(set_date)))
#    return

    
    #set reminder text
    # reminder list should be a pending list and a done list (max 10 items)
    # ask to remind tomorrow (add 1 day and move it back to the pending list) or delete it (keeps it in the done list)


