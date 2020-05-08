import discord
import pandas as pd
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

def save_df(df, message):
    try:
        with open('./data//'+str(message.guild)+'.csv', 'w+') as csv: df.to_csv(csv, index=0)
        print('df saved')
        return
    except Exception as e:
        print(e)
        print('There was a problem saving the Data to the csv file')
        return 'Error'

def load_df(message):
    try: 
        with open('./data//'+str(message.guild)+'.csv') as csv: df=pd.read_csv(csv)
        print('df loaded')
    except: 
        df=pd.DataFrame(data={'Title':[],'AddedBy':[]})
        print('new df created')
    return df


async def add2list(message, input):
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
        await edit_msg(df2msg(df), message)
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

async def remove(message, input):
    try: 
        global df
        df=load_df(message)
        removed=[]
        not_found=[]
        for i in input:
            if is_number(i):
                if int(i) in df.index: 
                    print('if works')
                    removed.append(str(df.loc[int(i),'Title']))
                    print('1 works')
                    df=df.drop(int(i))
                    print('2 works')
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
        await edit_msg(df2msg(df), message)
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
        msg = df2msg(df)
        if bot: 
            print('Message will be pinned')
            the_msg = await message.channel.send(msg)   #
            await the_msg.pin()                         #
            pin_info={'Message_Id': the_msg.id,         #
                      'Channel_Id': str(the_msg.channel),    #
                      'Server_Id': str(the_msg.guild)}       #
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
        return 'Error 1'

async def edit_msg(new_content, message):
    # Maybe convert it to an 'update_pin(message)' function, opening the csv file again?
    '''replace the content of the pinned message of a server with the updated information'''
    try:
        with open('./data//'+str(message.guild)+'_pin.json', 'r') as j: ref=json.load(j)
        print('ref')
        print(ref)
        client=discord.Client()
        msg = await message.channel.fetch_message(ref['Message_Id'])
        await msg.edit(content=new_content)
        #await msg
        print('New content: \n%s' % new_content)
        
        print('Message edited')
        return 
    except Exception as e:
        print(e)
        print('The Pinned Message could not be edited. Maybe the message hasn\'t been pinned or the pin info file is corrupt/missing.')
        return 'Error 2'


def df2msg(df):
    '''This function creates a string using the data from a dataframe formatted for a message'''
    try:
        msg='``` \n'
        for i in range(df.index.size): msg=msg + str(i) + '. ' + str(df.loc[i,'Title']) + '  (by ' + str(df.loc[i,'AddedBy']) + ')\n'
        msg=msg+' ```'
        return msg
    except Exception as e:
        print(e)
        print('The Dataframe could not be converted into a message string. Make sure the Dataframe is formatted correctly')
        return '```Error creating message```'

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

#df=pd.DataFrame(data={'Title':['sun','moon'],'AddedBy':['Chris','Christi']})
#save_df(df,test)
#pin_list(test)
#add2list(test, ['a', 'b'])

