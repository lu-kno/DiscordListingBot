import discord
import json
import os
from '../keys/DiscordBotKey' import key

if not os.path.isfile('movie_list.json'):
        with open('movie_list.json','w+') as j: json.dump([],j)
        movie_list=[]
client = discord.Client()
if os.path.isfile('pinned_msg.json'):
        with open('pinned_msg.json','r') as j: pinned_msg=json.load(j)
else: pinned_msg=False

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global movie_list
    if message.author == client.user:
        return

    if message.content.lower().startswith('b!'):
        if ' ' in message.content:
            command = message.content[2:message.content.find(' ')].lower()
            input = message.content[message.content.find(' ')+1:].split(',')
        else: 
            command = message.content[2:]
            input=[]
        for i in range(len(input)):input[i]=input[i].strip()

        with open('movie_list.json','r') as j: movie_list=json.load(j)

        if command==('add'):
                for i in input:
                     if i not in movie_list: movie_list.append(i)
                response='I added the following entries: %s' % input

        elif command==('remove'):
                removed=[]
                for i in input:
                        if i in movie_list:
                                movie_list.remove(i)
                                removed.append(i)
                response='I removed the following entries: %s' % removed

        elif command==('show') or command==('pin'):
                response="```"
                for i in sorted(movie_list): response=response+'\n'+i
                response=response+"```"

        elif command==('help'):
            response='the available commands are "b!add", "b!remove" and "b!show". \nWhen adding or removing entries, include the names after the command. \nTo enter multiple names, separate them with a comma (,) .\n Print this message again with the use of "b!help".'

        else: response='I didnt understand "%s"' % command

        with open('movie_list.json','w+') as j: json.dump(movie_list,j)
        msg = await message.channel.send(response)

        if command == 'pin' and not pinned_msg:
            await msg.pin()
            with open('pinned_msg.json','w+') as j: json.dump(msg,j)

	
        if pinned_msg:
            new_edit='```'
            for i in sorted(movie_list): new_edit=new_edit+'\n'+i
            new_edit=new_edit+'```' 
            pinned_msg.edit(new_edit)
client.run(key)
