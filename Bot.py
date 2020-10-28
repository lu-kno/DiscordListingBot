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

@bot.command(name='reload',alias='update')
@commands.check(bf.sf.is_owner)
async def _reload(ctx):
    try:
        if not WIP: os.system('git pull')
        importlib.reload(bf)
        importlib.reload(config)
        print(config.reload_test)
        await ctx.send('Modules were reloaded')
    except Exception as e:
        print(e)
        await ctx.send('Something went wrong')
    return

while running:
    try: bot.run(key)
    except Exception as e: print(e)
