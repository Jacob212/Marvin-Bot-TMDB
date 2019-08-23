"""Main python file for bot.
Settings for the bot can be changed here. Like command prefix and status message.
This is also where the bot loads all the cogs from /cogs"""
import asyncio
from itertools import cycle
import os
import discord
from discord.ext import commands
from utils.api_handler import purge_cache
from utils.file_handler import download, make_genre_ids_file

def get_prefix(client, message):#
    prefixes = ['?']#allowed prefixes
    if not message.guild:#if in dms then only ? is allowed
        return '?'
    return commands.when_mentioned_or(*prefixes)(client, message)
    #allows user to use prefixes or mentioning the bot

async def change_status():#changes the status of the bot every 10 seconds from the list status.
    await client.wait_until_ready()
    status = ["?help", f'Servers: {len(client.guilds)}']
    msgs = cycle(status)
    while not client.is_closed():
        await client.change_presence(activity=discord.Activity(name=next(msgs), type=3))
        await asyncio.sleep(10)

async def auto_purge():#Clears the requests cache of expired responses every hour
    await client.wait_until_ready()
    while not client.is_closed():
        purge_cache()
        await asyncio.sleep(3600)

#list of all cogs that should be loaded on startup
INITIAL_EXTENSIONS = ['cogs.owner', 'cogs.general', 'cogs.management', 'cogs.error_handling']#

#creates instance of the bot
client = commands.Bot(command_prefix=get_prefix, description='My Bot')

#loads all extensions listed in initial_extensions
if __name__ == '__main__':
    for extension in INITIAL_EXTENSIONS:
        client.load_extension(extension)

#allows my testing bot in the tests directory to control this bot when running in travis ci
if os.environ.get("RESPOND_TO_BOTS") == "True":
    @client.event
    async def on_message(message):
        ctx = await client.get_context(message)
        await client.invoke(ctx)

@client.event
async def on_ready():#Prints that bot has logged in when ready.
    print('------')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    try:
        download("data")
        make_genre_ids_file("data")
    except:
        print("Failed to download latest files")

client.loop.create_task(auto_purge())
client.loop.create_task(change_status())
client.run(os.environ.get("DISCORD_BOT_TOKEN"))
