import asyncio
import discord
from discord.ext import commands
from itertools import cycle

f = open("Token.txt","r")#Reads bot token from text file.
TOKEN = f.read()
f.close()

def get_prefix(client, message):
    prefixes = ['?']#allowed prefixes
    if not message.guild:#if in dms then only ? is allowed
        return '?'
    return commands.when_mentioned_or(*prefixes)(client, message)#allows user to use prefixes or mentioning the bot

#changes the status of the bot every 10 seconds from the list status.
async def change_status():
  await client.wait_until_ready()
  status = ["?help",f'Servers: {len(client.guilds)}']
  msgs = cycle(status)
  while not client.is_closed():
    await client.change_presence(activity=discord.Activity(name=next(msgs),type=3))
    await asyncio.sleep(10)

#list of all cogs that should be loaded on startup
initial_extensions = ['cogs.owner','cogs.general']

#creates instance of the bot
client = commands.Bot(command_prefix=get_prefix, description='My Bot')

#loads all extensions listed in initial_extensions
if __name__ == '__main__':
    for extension in initial_extensions:
        client.load_extension(extension)

#Prints that bot has logged in when ready.
@client.event
async def on_ready():
  print('------')
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')

client.loop.create_task(change_status())
client.run(TOKEN)