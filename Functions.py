import discord
import pandas as pd
import json
import os
bot=0

#class Message:
#    def __init__(self, content):
#        self.guild = 'aguild'
#        self.channel = 'achannel'
#        self.author = 'anauthor'
#        self.content = content

#test=Message('acontent')

def save_df(df, message):
    df.to_csv('./data//'+message.guild+'.csv', index=0)
    print('df saved')

def load_df(message):
    try: 
        df=pd.read_csv('./data//'+message.guild+'.csv')
    except: 
        df=pd.DataFrame(data={'Title':[],'AddedBy':[]})
    print('df loaded')
    return df


def add2list(message, input):
    try:
        global df
        df=load_df(message)

        print('read')
        for i in input:
                if i not in df['Title'].to_list(): df.loc[df.index.size]= [i] + [message.author]
        print('added')
        save_df(df, message)
        edit_msg(df2msg(df), message)
        print('edited')
        response='I added the following entries: %s' % input
        print(response)
        return response
    except:
        print('An error ocurred adding entries to the list')
        return 'Error Adding to entry to the list'

def remove(message, input):
    try: 
        global df
        df=load_df(message)

        print('read')
        for i in input:
            if is_number(i):
               if int(i) in df.index: df=df.drop(i)
            elif i in df['Title'].to_list(): df=df.drop(df[df.loc[:,'Title']==i].index)
        df=df.reset_index(drop=1)

        print('removed')
        save_df(df, message)
        edit_msg(df2msg(df), message)
        print('edited')
        response='I removed the following entries: %s' % input
        print(response)
        return response

    except:
        print('An error ocurred removing entries from the list')
        return 'Error removing entry from the list'

async def pin_list(message):
    '''This Function sends a message with the servers list and pinns it. 
    Aditionally, the reference id for the message, channel and server (guild) are saved 
    to edit the message with every change made'''
    try:
        df=pd.read_csv('./data//'+message.guild+'.csv')
    except:
        print('CSV File could not be loaded. Maybe it doesn\'t exist.')

    try:
        msg = df2msg(df)
        if bot: 
            print('Message will be pinned')
            the_msg = await message.channel.send(msg)   #
            await the_msg.pin()                         #
            pin_info={'Message_Id': the_msg.id,         #
                      'Channel_Id': the_msg.channel,    #
                      'Server_Id': the_msg.guild}       #
        else: 
            pin_info={'Message_Id': 'the_msg.id',
                        'Channel_Id': 'the_msg.channel',
                        'Server_Id': 'the_msg.guild'}

        with open('./data//'+message.guild+'_pin.json', 'w+') as j: json.dump(pin_info,j)
        print('pin_info')
        print(pin_info)
        return 
        
    except:
        print('Something went wrong. Message could not be Pinned')
        return 1

async def edit_msg(new_content, message):
    # Maybe convert it to an 'update_pin(message)' function, opening the csv file again?
    '''replace the content of the pinned message of a server with the updated information'''
    try:
        with open('./data//'+message.guild+'_pin.json', 'r') as j: ref=json.load(j)
        print('ref')
        print(ref)
        if bot:                 #
            msg = await client.guilds.get(ref['Server_Id']).channels.get(ref['Channel_Id']).fetch_message(ref['Message_Id'])
            await msg.edit(content)
        print('New content: \n%s' % new_content)
        
        return 
    except:
        print('The Pinned Message could not be edited. Maybe the message hasn\'t been pinned or the pin info file is corrupt/missing.')
        return 2


def df2msg(df):
    '''This function creates a string using the data from a dataframe formatted for a message'''
    try:
        msg='```\n'
        for i in range(df.index.size): msg=msg + str(i) + '. ' + df.loc[i,'Title'] + '  (by ' + df.loc[i,'AddedBy'] + ')\n'
        msg=msg+'```'
        return msg
    except:
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

