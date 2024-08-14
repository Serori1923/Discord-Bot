# -*- coding: UTF-8 -*- 

import discord
from discord.ext import commands
import os
import time
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)

gw_logger = logging.getLogger('discord.gateway')
gw_logger.setLevel(logging.ERROR)

vc_logger = logging.getLogger('discord.voice_client')
vc_logger.setLevel(logging.ERROR)

vcs_logger = logging.getLogger('discord.voice_state')
vcs_logger.setLevel(logging.ERROR)

vcp_logger = logging.getLogger('discord.player')
vcp_logger.setLevel(logging.ERROR)

client_logger = logging.getLogger('discord.client')
client_logger.setLevel(logging.ERROR)

class GatewayEventFilter(logging.Filter):
    def __init__(self) -> None:
        super().__init__('discord.client')

    def filter(self, record: logging.LogRecord) -> bool:
        if record.exc_info is not None and isinstance(record.exc_info[1], discord.ConnectionClosed):
            return False
        return True
    
logging.getLogger('discord.client').addFilter(GatewayEventFilter())

#設定檔
intents = discord.Intents().all()
client = commands.Bot(command_prefix = "/", intents = intents)
players = {}

def journal(user,event):
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S |', time.localtime())
    print(f'{nowtime} Requester: {user} | {event}')

@client.event
async def on_ready():
    for filename in os.listdir("./Cog"):
        if filename.endswith(".py"):
            await client.load_extension(f"Cog.{filename[:-3]}")
            print(f'Loaded {filename[:-3]}')
    print('All File Loaded.\n')

    uptime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(f'\n{uptime} bot start working\n')
    print('└|`д´|┐   ※Bot is online※   └|๑´ㅁ`|┐ \n -----------------------------------')

    await client.tree.sync()
    game = discord.CustomActivity("正在玩 貓咪大戰爭")
    await client.change_presence(status=discord.Status.online, activity=game)


@client.command()
async def load(interaction, ext):
    await client.load_extension(f'Cog.{ext}')
    await interaction.send(f'{ext} loaded successfully.')
    await client.tree.sync()

@client.command()
async def unload(interaction, ext):
    await client.unload_extension(f'Cog.{ext}')
    await interaction.send(f'{ext} unloaded successfully.')
    await client.tree.sync()

@client.command()
async def reload(interaction, ext):
    await client.reload_extension(f'Cog.{ext}')
    await interaction.send(f'{ext} reloaded successfully.')
    await client.tree.sync()

@client.event
async def on_command_error(interaction,error):
    print(error)

client.run("Your Token Here")