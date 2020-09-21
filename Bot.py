import json
import os
import sys
import discord
from discord.ext import commands

from config import *
from BotFunctions import *

# set prefix and key
if re.search('WIP',str(sys.argv), re.IGNORECASE) or os.path.isfile(os.path.join(script_path,'WIP.txt')):
    WIP=1
    print('Using WIP Version!')
    with open(os.path.join(script_path,'botprivWIP.key'),'r') as k: key=k.readlines()[0]
    #bot = commands.Bot(command_prefix='!')
else: 
    WIP=0
    with open(os.path.join(script_path,'botpriv.key'),'r') as k: key=k.readlines()[0]
    #bot = commands.Bot(command_prefix='b!')


#bot = discord.Client()



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
        await get_random(reaction.message, 1)
    return

@bot.event
async def on_reaction_remove(reaction,user):
    #global movie_list
    if user == bot.user:
        return
    if reaction.message.nonce==11:
        await get_random(reaction.message,1)
    return

bot.run(key)