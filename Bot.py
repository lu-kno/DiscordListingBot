import discord
import json
import os
from Functions import *


with open('./botpriv.key','r') as k: key=k.readlines()[0]

#if not os.path.isfile('movie_list.json'):
#        with open('movie_list.json','w+') as j: json.dump([],j)
#        movie_list=[]
#if os.path.isfile('pinned_msg.json'):
#        with open('pinned_msg.json','r') as j: pinned_msg=json.load(j)
#else: pinned_msg=False

client = discord.Client()
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    global movie_list
    if message.author == client.user:
        return

    if message.content.lower().startswith('b!'):
        print(message.guild)
        print(message.channel)
        print(message.author)
        print(message.id)
        if ' ' in message.content:
            command = message.content[2:message.content.find(' ')].lower()
            input = message.content[message.content.find(' ')+1:].split(',')
        else: 
            command = message.content[2:]   
            input=[]
        for i in range(len(input)):input[i]=input[i].strip()

        response= 'blank'

        #with open('movie_list.json','r') as j: movie_list=json.load(j)

        if command==('add'): response = await add2list(message, input)

        elif command==('addlink'): response = await addlink(message, input)

        elif command==('remove'): response = await remove(message,input)

        elif command==('sort'): response = await sort(message)

        elif command==('searchNFLX'): response = await searchNFLX(message)

        elif command==('embed'): response = await test_embed(message)

        elif command==('show'): response = await show(message)

        elif command==('pin'): response = await pin_list(message)

        elif command==('random'): response = await get_random(message)

        elif command==('help'): response = 'the available commands are "b!add", "b!remove" and "b!show". \nWhen adding or removing entries, include the names after the command. \nTo enter multiple names, separate them with a comma (,) .\n Print this message again with the use of "b!help".'

        else: response='I didnt understand "%s"' % command


        msg = await message.channel.send(response)


        #with open('movie_list.json','w+') as j: json.dump(movie_list,j)

        #if command == 'pin' and not pinned_msg:
        #    await msg.pin()
        #    with open('pinned_msg.json','w+') as j: json.dump(msg,j)


        #if pinned_msg:
        #    new_edit='```'
        #    for i in sorted(movie_list): new_edit=new_edit+'\n'+i
        #    new_edit=new_edit+'```' 
        #    pinned_msg.edit(new_edit)

client.run(key)