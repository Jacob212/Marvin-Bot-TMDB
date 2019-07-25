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

async def test_search_blank():
    await client.get_channel(603641157120950282).send("?search")
    print("Testing ?search")
    try:
        response = await client.wait_for("message", check=lambda m: m.author.id == 530876853104410624, timeout=10)
    except asyncio.TimeoutError:
        print("failed")
        return "failed" 
    else:
        if len(response.embeds) > 1 or response.embeds[0].title != "Search results for:" or response.embeds[0].description != "":
            print("failed")
            return "failed"
        print("passed")
        return "passed"

async def test_search():
    await client.get_channel(603641157120950282).send("?search the flash")
    print("Testing ?search the flash")
    response = await client.wait_for("message", check=lambda m: m.author.id == 530876853104410624, timeout=10)
    if len(response.embeds) > 1 or response.embeds[0].title != "Search results for:" or response.embeds[0].description != "the flash":
        print("failed")
        return "failed"
    print("passed")
    return "passed"

async def test_search_movies():
    await client.get_channel(603641157120950282).send("?search the flash -movies")
    print("Testing ?search the flash -movies")
    response = await client.wait_for("message", check=lambda m: m.author.id == 530876853104410624, timeout=10)
    if len(response.embeds) > 1 or response.embeds[0].title != "Search results for:" or response.embeds[0].description != "the flash":
        print("failed")
        return "failed"
    print("passed")
    return "passed"

async def test_search_shows():
    await client.get_channel(603641157120950282).send("?search the flash -shows")
    print("Testing ?search the flash -shows")
    response = await client.wait_for("message", check=lambda m: m.author.id == 530876853104410624, timeout=10)
    if len(response.embeds) > 1 or response.embeds[0].title != "Search results for:" or response.embeds[0].description != "the flash":
        print("failed")
        return "failed"
    print("passed")
    return "passed"

tests_to_run = [test_search_blank,test_search,test_search_movies,test_search_shows]

async def run_tests(tests):
    try:
        for test in tests:
            result = await test()
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
        await run_tests(tests_to_run)
    else:
        await client.close()
        sys.exit(1)

client.run(os.environ.get("DISCORD_TESTING_BOT_TOKEN"))
