import discord
import pandas as pd
import numpy as np
import json
import os
import re
from random import randrange
bot=1

class Message:
    def __init__(self, content):
        self.guild = 'CoronaCheck'
        self.channel = 'general'
        self.author = 'anauthor'
        self.content = content

test=Message('acontent')


def save_df(df, message, csv=1):
    try:
        #df.to_pickle('./data//'+str(message.guild)+'.pck',compression=None)
        if csv: 
            with open('./data//'+str(message.guild)+'.csv', 'w+') as csv: df.to_csv(csv, index=0)
        else:
            df.to_json('./data//'+str(message.guild)+'.json', orient='index')
        print('df saved')
        return
    except Exception as e:
        print(e)
        print('There was a problem saving the Data to the pickle file')
        return 'Error'

def load_df(message):
    try: 
        if os.path.isfile('./data//'+str(message.guild)+'.json'):
            df=pd.read_pickle('./data//'+str(message.guild)+'.json', orient='index')
        elif os.path.isfile('./data//'+str(message.guild)+'.pck'):
            df=pd.read_pickle('./data//'+str(message.guild)+'.pck',compression=None)
        else:
            with open('./data//'+str(message.guild)+'.csv') as csv: df=pd.read_csv(csv)

        print('df loaded')
    except Exception as e: 
        print(e)
        df=pd.DataFrame(data={'Title':[],'AddedBy':[],'Link':[]})
        print('new df created')
    if 'Link' not in df.columns:
        l=['' for i in range(df.index.size)]
        df['Link']=l
    df = df.replace(np.nan, '', regex=True)
    df = capitalize(df)
    return df


async def add2list_unlinked(message, input):
    try:
        global df
        df=load_df(message)
        added=[]
        ignored=[]
        for i in input:
                if i.upper() not in [n.upper() for n in df['Title'].to_list()]: 
                    df.loc[df.index.size]= [i] + [message.author]
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
    except:
        print('An error ocurred adding entries to the list')
        return 'Error Adding to entry to the list'

async def add2list(message, input):
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
                    df.loc[df.index.size]= [i.capitalize()] + [message.author] + [' '.join(links)]
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
    except:
        print('An error ocurred adding entries to the list')
        return 'Error Adding to entry to the list'

async def get_random(message):
    try:
        global df
        df=load_df(message)
        r=randrange(len(df))
        output=str(df.loc[r,'Title']) + '  (by ' + str(df.loc[r,'AddedBy']) + ')'
        response='Random result:\n```%s```' % output
        print(response)
        return response
    except:
        print('An error ocurred getting a random entry from the list')
        return 'Error  getting a random entry from the list'

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

async def sort(message):
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

async def pin_list(message):
    '''This Function sends a message with the servers list and pins it. 
    Aditionally, the reference id for the message, channel and server (guild) are saved 
    to edit the message with every change made'''
    df=load_df(message)

    try:
        embed_list = df2embed(df)
        print('embed list length %s' % len(embed_list))
        
        # Unpin old messages before pinning the new ones
        with open('./data//'+str(message.guild)+'_pin.json', 'r') as j: pin_info=json.load(j)
        for ref_number in pin_info['Message_Id']:
                msg = await message.channel.fetch_message(ref_number)
                await msg.unpin()

        if bot: 
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
        else: 
            pin_info={'Message_Id': 'the_msg.id',
                        'Channel_Id': 'the_msg.channel',
                        'Server_Id': 'the_msg.guild'}

        with open('./data//'+str(message.guild)+'_pin.json', 'w+') as j: json.dump(pin_info,j)
        print('pin_info')
        print(pin_info)
        return 'The message has been Pinned'
        
    except Exception as e:
        print(e)
        print('Something went wrong. Message could not be Pinned')
        return 'Message could not be pinned'

async def edit_msg(df, message):
    # Maybe convert it to an 'update_pin(message)' function, opening the csv file again?
    '''replace the content of the pinned message of a server with the updated information'''
    try:
        embed_list=df2embed(df)
        with open('./data//'+str(message.guild)+'_pin.json', 'r') as j: ref=json.load(j)
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


def df2embed_string(df):
    '''This function creates a string using the data from a dataframe formatted for a message'''
    try:
        msg='```\n'
        for i in range(df.index.size): 
            #linkstring=''
            #for link in df.loc[i,'Link']: linkstring=linkstring+str(link)+' '
            msg=msg + str(i) + '. ' + str(df.loc[i,'Title']) 
            msg=msg + '  (by ' + str(df.loc[i,'AddedBy']) + ')  ' 
            msg=msg + str(df.loc[i,'Link']) + '\n'
        msg=msg+'```'
        return msg
    except Exception as e:
        print(e)
        print('The Dataframe could not be converted into a message string. Make sure the Dataframe is formatted correctly')
        return '```Error creating message```'

def df2embed(df):
    '''This function returns a list of discord embeds containing the data from a dataframe separated every 10 elements'''
    try:
        description=''
        description_list=[]

        for i in range(df.index.size): 
            if i!=1 and (i-1)%10==0:
                description_list.append(description)
                description=''
            links=str(df.loc[i,'Link']).strip().split(' ')
            if links[0]: link_string='[DL](' + ')  [DL]('.join(links) + ')'
            else: link_string=''
            title_string=str(df.loc[i,'Title'])
            addedby_string=str(df.loc[i,'AddedBy'])
            description=description + '`' + str(i) + '.` ' + title_string + ' '
            description=description + '`(by ' + addedby_string[:addedby_string.find('#')] + ')` '
            description=description + link_string + '\n'
        description_list.append(description)
        embed_list=[]
        for description in description_list:
            embed = discord.Embed(title="Watchlist", colour=discord.Colour(0xCD01BD), description=description,)
            embed_list.append(embed)
        print(description_list)

        return embed_list
    except Exception as e:
        print(e)
        print('The Dataframe could not be converted into a message string. Make sure the Dataframe is formatted correctly')
        return '```Error creating message```'

async def show(message):
    try:
        embed_list=df2embed(load_df(message))
        for embed in embed_list:
            await message.channel.send(embed=embed)
        return '** **'
    except Exception as e:
        print(e)
        print('The message could not be send')
        return '```The message could not be sent. List can not be shown```'

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def add_space(s):
    s=s+' '
    while len(s[s.rfind('\n')+1:])%4: s=s+' '
    return s

#df=pd.DataFrame(data={'Title':['sun','moon'],'AddedBy':['Chris','Christi']})
#save_df(df,test)
#pin_list(test)
#add2list(test, ['a', 'b'])

async def test_embed(message):
    embed_list=df2embed(load_df(test))
    for embed in embed_list: await message.channel.send(embed=embed)

def capitalize(df):
    df['Title']=df['Title'].apply(cap)
    return df

def cap(s):
    return s.capitalize()

