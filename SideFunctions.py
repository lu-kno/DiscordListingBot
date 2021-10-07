import discord
import pandas as pd
import numpy as np
import json
import os
import re
from random import randrange
import config
import datetime
import asyncio


testing_import='asdfasdfa'

def save_df(df, message, csv=1):
    try:
        #df.to_pickle(os.path.join(config.script_path,'data',str(message.guild)+'.pck'),compression=None)
        if csv: 
            with open(os.path.join(config.script_path,'data',str(message.guild)+'.csv'), 'w+') as csv: df.to_csv(csv, index=0)
        else:
            df.to_json(os.path.join(config.script_path,'data',str(message.guild)+'.json'), orient='index')
        print('df saved')
        return
    except Exception as e:
        print(e)
        print('There was a problem saving the Data to the pickle file')
        return 'Error'

def load_df(message):
    try: 
        if os.path.isfile(os.path.join(config.script_path,'data',str(message.guild)+'.json')):
            df=pd.read_pickle(os.path.join(config.script_path,'data',str(message.guild)+'.json'), orient='index')
        elif os.path.isfile(os.path.join(config.script_path,'data',str(message.guild)+'.pck')):
            df=pd.read_pickle(os.path.join(config.script_path,'data',str(message.guild)+'.pck'),compression=None)
        else:
            with open(os.path.join(config.script_path,'data',str(message.guild)+'.csv')) as csv: df=pd.read_csv(csv)

        #print('df loaded')
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

async def get_elements(ctx, input, vote=0, embed_title='Watchlist'):
    try:
        global df
        df=load_df(ctx)

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
        else: embed_list=df2embed(tmp_df,vote=vote, embed_title=embed_title)
        for i in range(len(embed_list)):
            msg= await ctx.channel.send(embed=embed_list[i])
            if vote:
                for emoji in emoji_list[i]:
                    await msg.add_reaction(emoji)
        if not_found: response='I could not find the following entries: %s\n' % not_found
        else: response=''
        print(response)
        if response: await ctx.send(response)
        return
        
    except Exception as e:
        print(e)
        print('An error ocurred getting the entry from the list')
        await ctx.send('An error ocurred getting the entry from the list')
        return

async def edit_msg(df, ctx):
    # Maybe convert it to an 'update_pin(ctx)' function, opening the csv file again?
    '''replace the content of the pinned message of a server with the updated information'''
    try:
        embed_list=df2embed(df)
        with open(os.path.join(config.script_path,'data',str(ctx.guild)+'_pin.json'), 'r') as j: pin_info=json.load(j)
        print('pin_info')
        print(pin_info)
        ref_list=pin_info['Message_Id']
        client=discord.Client()
        #if len(embed_list)!=len(ref_list):                                           # If the new content wont fit in all the old messages, a new pin will be created, removing old pinned messages
        #    #for ref_number in ref_list:
        #    #    msg = await ctx.channel.fetch_message(ref_number)
        #    #    await msg.unpin()
        #    #await pin_list(ctx)

        if len(embed_list)>=len(ref_list):
            for i in range(len(ref_list)):
                msg = await ctx.channel.fetch_message(ref_list[i])
                await msg.edit(embed=embed_list[i])

            for i in range(len(ref_list),len(embed_list)):
                msg = await ctx.channel.send(embed=embed_list[i])
                await msg.pin()
                pin_info['Message_Id'].append(msg.id)

        elif len(embed_list)<len(ref_list):
            for i in range(len(embed_list)):
                msg = await ctx.channel.fetch_message(ref_list[i])
                await msg.edit(embed=embed_list[i])

            for i in reversed(range(len(embed_list),len(ref_list))):
                msg = await ctx.channel.fetch_message(ref_list[i])
                await msg.edit(embed=empty_embed())
                await msg.unpin()
                pin_info['Message_Id'].pop(i)

        #else:
        #    for i in range(len(ref_list)):
        #        ref_number=ref_list[i]
        #        embed=embed_list[i]
        #        msg = await ctx.channel.fetch_message(ref_number)
        #        await msg.edit(embed=embed)

        with open(os.path.join(config.script_path,'data',str(ctx.guild)+'_pin.json'), 'w+') as j: json.dump(pin_info,j)
        #await msg.edit(content=new_content)
        #await msg
        #print('New content: \n%s' % new_content)
        
        print('Message edited')
        return 0
    except Exception as e:
        print(e)
        print('The Pinned Message could not be edited. Maybe the message hasn\'t been pinned or the pin info file is corrupt/missing.')
        return 'Message could not be edited'

async def pin_list(ctx):
    '''Sends list as embeds and pins them. This messages are kept up-to-date''' 

    df=load_df(ctx)

    try:
        embed_list = df2embed(df)
        print('embed list length %s' % len(embed_list))
        
        # Unpin old messages before pinning the new ones
        with open(os.path.join(config.script_path,'data',str(ctx.guild)+'_pin.json'), 'r') as j: pin_info=json.load(j)
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

        with open(os.path.join(config.script_path,'data',str(ctx.guild)+'_pin.json'), 'w+') as j: json.dump(pin_info,j)
        print('pin_info')
        print(pin_info)
        await ctx.send('The message has been Pinned')
        return
        
    except Exception as e:
        print(e)
        print('Something went wrong. Message could not be Pinned')
        await ctx.send('Message could not be pinned')
        return
    
def line2embed(df,i):
    '''This function returns a discord embed containing the data from a dataframe in one single embed.'''
    try:
        description=''

        title_string=str(df.loc[i,'Title'])
        addedby_string=str(df.loc[i,'AddedBy'])
        netflix_path=df.loc[i,'Netflix']
        links=str(df.loc[i,'Link']).strip().split(' ')
        link_string=''

        if links[0]: 
            for link in links:
                prefix='DL'
                if 'mega.nz' in link.lower(): prefix='MEGA'
                else:
                    torrent=['pirate','bay','torrent']
                    for t in torrent: 
                        if t in link.lower():
                            prefix='TORR'
                link_string=link_string+'[{}]({})  '.format(prefix, link)
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

def df2embed(df,vote=0, embed_title="Watchlist"):
    '''This function returns a list of discord embeds containing the data from a dataframe separated every 10 elements'''
    try:
        description=''
        description_list=[]
        emoji_list=[]
        emoji_stack=[]
        counter=-1
        c=0
        max=10

        for i in df.index: 
            #if i!=1 and (i-1)%10==0:
            if counter==max:
                description_list.append(description)
                emoji_list.append(emoji_stack)
                emoji_stack=[]
                description=''
                counter=0
                c=0
            title_string=str(df.loc[i,'Title'])
            addedby_string=str(df.loc[i,'AddedBy'])
            netflix_path=df.loc[i,'Netflix']
            links=str(df.loc[i,'Link']).strip().split(' ')
            link_string=''
            emoji=''

            if links[0]: 
                for link in links:
                    prefix='DL'
                    if 'mega.nz' in link.lower(): prefix='MEGA'
                    else:
                       torrent=['pirate','bay','torrent']
                       for t in torrent: 
                           if t in link.lower():
                               prefix='TORR'
                    link_string=link_string+'[{}]({})  '.format(prefix, link)
                    #link_string='[DL](' + ')  [DL]('.join(links) + ')'
            if netflix_path.startswith('/title/'):netflix_path='[NFLX](https://www.netflix.com'+netflix_path+')'
            if vote: emoji=chr(127462+c)

            description=description + '`' + str(i) + '.` '+emoji + title_string + ' '
            description=description + '`(by ' + addedby_string[:addedby_string.find('#')] + ')` '
            description=description + netflix_path + ' ' + link_string + '\n'
            counter=counter+1
            c=c+1
            emoji_stack.append(emoji)

        emoji_list.append(emoji_stack)
        description_list.append(description)
        embed_list=[]

        for description in description_list:
            embed = discord.Embed(title=embed_title, colour=discord.Colour(0xCD01BD), description=description,)
            embed_list.append(embed)
        #print(description_list)

        if vote: return embed_list, emoji_list
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

def is_number(*s):
    try:
        for i in s: int(i)
        return True
    except ValueError:
        return False

def arg2input(arg):
    if is_number(*arg.split(' ')): input=arg.split(' ')
    else: input=[i.strip() for i in arg.split(',')]
    return input

def empty_embed():
    return discord.Embed(title=" ", colour=discord.Colour(0xCD01BD), description='',)

def parse_timedelta(time_str):
    try:    
        regex = re.compile(r'((?P<weeks>\d+?)w)?\s?((?P<days>\d+?)d)?\s?((?P<hours>\d+?)hr?)?\s?((?P<minutes>\d+?)m)?\s?((?P<seconds>\d+?)s)?')
        parts = regex.match(time_str)
        if not parts:
            return
        parts = parts.groupdict()
        for i in parts: 
            if parts[i]==None: parts[i]=0
            parts[i]=int(parts[i])
        return datetime.timedelta(**parts)
    except Exception as e:
        print(e)
        print('timedelta could not be parsed')
        return None

async def check_reminders():
    running=1
    while running:
        print('checking reminders')
        await asyncio.sleep(2)

async def is_owner(ctx):
    return ctx.author.id == config.author