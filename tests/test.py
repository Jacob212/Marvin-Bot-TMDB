import asyncio
import os
import sys
import threading
from discord.ext import commands

def thread_function(command):
    os.system(command)

if __name__ == "__main__":
    tested_bot_thread = threading.Thread(target=thread_function, args=("cd .. & run marvin.py",))
    tested_bot_thread.start()

#creates instance of the bot
client = commands.Bot(command_prefix="!", description="Testing Bot")

BASIC_EMBED_TESTS = (
    ("?search", ("You have to enter something to search for.", "eg ?search the flash")),
    ("?search the flash", ("Search results for:", "the flash")),
    ("?search the flash -movies", ("Search results for:", "the flash")),
    ("?search the flash -shows", ("Search results for:", "the flash")),
    ("?search this isnt in here", ("Search results for:", "this isnt in here"))
    )

async def basic_tests(test):
    await client.get_channel(603641157120950282).send(test[0])
    try:
        response = await client.wait_for("message", check=lambda m: m.author.id == 530876853104410624, timeout=20)
    except asyncio.futures.TimeoutError:
        print(f'{test[0]} timeout')
        return "failed"
    if len(response.embeds) > 1 or response.embeds[0].title != test[1][0] or response.embeds[0].description != test[1][1]:
        print(f'{test[0]} failed')
        return "failed"
    print(f'{test[0]} passed')
    return "passed"

async def reactions_test():
    await client.get_channel(603641157120950282).send("?search the flash")
    try:
        response = await client.wait_for("message", check=lambda m: m.author.id == 530876853104410624, timeout=20)
    except asyncio.futures.TimeoutError:
        print(f'reactions test timeout')
        return "failed"
    await asyncio.sleep(1)
    await response.channel.send("1")
    await asyncio.sleep(1)
    message = await response.channel.fetch_message(response.id)
    if response.embeds[0].title != "The Flash":
        print("failed at getting details")
        return "failed"
    await asyncio.sleep(1)
    await response.add_reaction("◀")
    await asyncio.sleep(1)
    message2 = await response.channel.fetch_message(response.id)
    if message.embeds[0] == message2.embeds[0]:
        print("failed when going back")
        return "failed"
    await asyncio.sleep(1)
    await response.add_reaction("▶")
    await asyncio.sleep(1)
    message = await response.channel.fetch_message(response.id)
    if response.embeds[0] == message.embeds[0]:
        print("failed to get to page 2")
        return "failed"
    print("reactions test passed")
    return "passed"

async def run_tests():
    for test in BASIC_EMBED_TESTS:
        result = await basic_tests(test)
        if result == "failed":
            await asyncio.sleep(2)
            await client.get_channel(603641157120950282).send("?shutdown")
            await client.close()
            sys.exit(1)
        await asyncio.sleep(2)
    else:
        result = await reactions_test()
        if result == "failed":
            await asyncio.sleep(2)
            await client.get_channel(603641157120950282).send("?shutdown")
            await client.close()
            sys.exit(1)
        print("passed all tests")
        await asyncio.sleep(2)
        await client.get_channel(603641157120950282).send("?shutdown")
        await client.close()
        sys.exit(0)

@client.event
async def on_ready():#Prints that bot has logged in when ready.
    print('------')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await asyncio.sleep(4)
    if str(client.get_guild(538718965904703508).get_member(530876853104410624).status) == "online":
        await run_tests()
    else:
        await client.close()
        sys.exit(1)

client.run(os.environ.get("DISCORD_TESTING_BOT_TOKEN"))
