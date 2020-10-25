import json
import os
import sys
import discord
from discord.ext import commands
import importlib
import re

import config
import BotFunctions as bf
running=1

# set prefix and key
if re.search('WIP',str(sys.argv), re.IGNORECASE) or os.path.isfile(os.path.join(config.script_path,'WIP.txt')):
    WIP=1
    print('Using WIP Version!')
    with open(os.path.join(config.script_path,'botprivWIP.key'),'r') as k: key=k.readlines()[0]
    #bot = commands.Bot(command_prefix='!')
else: 
    WIP=0
    with open(os.path.join(config.script_path,'botpriv.key'),'r') as k: key=k.readlines()[0]
    #bot = commands.Bot(command_prefix='b!')

bot=bf.bot
#bot = discord.Client()


#@bot.event
#async def on_message(message):
#    await reminders.check()
#    return



@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Python!'))
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_reaction_add(reaction,user):
    #global movie_list
    if user == bot.user:
        return
    if reaction.message.nonce==11:
        await bf.get_random(reaction.message, 1)
    
    if reaction.message.nonce==1 and user.id==config.author:
        if not WIP: os.system('git pull')
        importlib.reload(bf)
        importlib.reload(config)
        print(config.reload_test)

    return

@bot.event
async def on_reaction_remove(reaction,user):
    #global movie_list
    if reaction.message.nonce==11 and user != bot.user:
        await bf.get_random(reaction.message,1)
    return



while running:
    try:
        bot.run(key)
    except Exception as e:
        print(e)
