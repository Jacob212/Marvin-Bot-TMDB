import asyncio
import os
import sys
import threading
import discord
from discord.ext import commands

def thread_function(command):
    os.system(command)

if __name__ == "__main__":
    y = threading.Thread(target=thread_function, args=("cd .. & coverage run marvin.py",))
    y.start()

#creates instance of the bot
client = commands.Bot(command_prefix="!", description="Testing Bot")

basic_tests_list = (
    ("?search", ("You have to enter something to search for.", "eg ?search the flash")),
    ("?search the flash", ("Search results for:", "the flash")),
    ("?search the flash -movies", ("Search results for:", "the flash")),
    ("?search the flash -shows", ("Search results for:", "the flash"))
    )

async def basic_tests(test):
    await client.get_channel(603641157120950282).send(test[0])
    print("Testing ?search")
    try:
        response = await client.wait_for("message", check=lambda m: m.author.id == 530876853104410624, timeout=10)
    except asyncio.futures.TimeoutError:
        print("failed")
        return "failed" 
    else:
        if len(response.embeds) > 1 or response.embeds[0].title != test[1][0] or response.embeds[0].description != test[1][1]:
            print("failed")
            return "failed"
        print("passed")
        return "passed"

async def run_tests(tests):
    try:
        for test in tests:
            result = await basic_tests(test)
            if result == "failed":
                await client.get_channel(603641157120950282).send("?shutdown")
                await client.close()
                sys.exit(1)
            await asyncio.sleep(2)
    except Exception as e:
        raise e
        await asyncio.sleep(2)
        await client.get_channel(603641157120950282).send("?shutdown")
        await client.close()
        sys.exit(1)
    else:
        print("passed all tests")
        await asyncio.sleep(2)
        await client.get_channel(603641157120950282).send("?shutdown")
        await client.close()
        sys.exit(0)

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
    await asyncio.sleep(4)
    if str(client.get_guild(538718965904703508).get_member(530876853104410624).status) == "online":
        await run_tests(basic_tests_list)
    else:
        await client.close()
        sys.exit(1)

client.run(os.environ.get("DISCORD_TESTING_BOT_TOKEN"))
