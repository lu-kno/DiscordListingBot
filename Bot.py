import discord
import json
import os
from BotFunctions import *
#import FunctionList
import sys
from config import *


if re.search('WIP',str(sys.argv), re.IGNORECASE) or os.path.isfile(os.path.join(script_path,'WIP.txt')):
    WIP=1
    print('Using WIP Version!')
else: WIP=0


if WIP:
    with open(os.path.join(script_path,'botprivWIP.key'),'r') as k: key=k.readlines()[0]
else:
    with open(os.path.join(script_path,'botpriv.key'),'r') as k: key=k.readlines()[0]


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
async def on_reaction_add(reaction,user):
    #global movie_list
    if user == client.user:
        return
    if reaction.message.nonce==11:
        await get_random(reaction.message,[],reroll=1)
    return

@client.event
async def on_reaction_remove(reaction,user):
    #global movie_list
    if user == client.user:
        return
    if reaction.message.nonce==11:
        await get_random(reaction.message,[],reroll=1)
    return

@client.event
async def on_message(message):
    #global movie_list
    if message.author == client.user:
        return

    if message.content.lower().startswith('b!') or (WIP and message.content.lower().startswith('!')):
        print(message.guild)
        print(message.channel)
        print(message.author)
        print(message.id)
        if ' ' in message.content:
            command = message.content[message.content.find('!')+1:message.content.find(' ')].lower()
            input = message.content[message.content.find(' ')+1:].split(',')
        else: 
            command = message.content[message.content.find('!')+1:]   
            input=[]
        for i in range(len(input)):input[i]=input[i].strip()

        response= 'blank'

        if command in function_list.keys(): response = await function_list[command](message,input)
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
    return
client.run(key)