import asyncio
import os
import sys
import threading
import discord
from discord.ext import commands

def thread_function(name, command):
    os.system(command)

if __name__ == "__main__":
    y = threading.Thread(target=thread_function, args=("main_bot","cd .. & python marvin.py"))
    y.start()
    # x.join()

#creates instance of the bot
client = commands.Bot(command_prefix="!", description="Testing Bot")

@client.command()
async def stop(context):
    await client.close()

@client.event
async def on_ready():#Prints that bot has logged in when ready.
    print('------')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await asyncio.sleep(10)
    if str(client.get_guild(538718965904703508).get_member(530876853104410624).status) == "online":
        await client.get_channel(603641157120950282).send("?shutdown")
        await client.close()
        sys.exit(0)
    else:
        await client.close()
        sys.exit(1)

client.run(os.environ.get("DISCORD_TESTING_BOT_TOKEN"))
