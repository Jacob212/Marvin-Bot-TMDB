from discord.ext import commands
import discord

class errorHandlingCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, context, error):
        if isinstance(error,  commands.NoPrivateMessage):
            await context.message.channel.send("**private messages.**" + context.message.author.mention, delete_after=10)
        if isinstance(error,  commands.MissingRequiredArgument):
            await context.message.channel.send("**Missing an argument.**" + context.message.author.mention, delete_after=10)
        elif isinstance(error,  commands.DisabledCommand):
            await context.message.channel.send("**Command is disabled.**" + context.message.author.mention, delete_after=10)
        elif isinstance(error,  commands.CheckFailure):
            await context.message.channel.send("**No permission.**" + context.message.author.mention, delete_after=10)
        elif isinstance(error,  commands.CommandNotFound):
            await context.message.channel.send("**Wrong command.**" + context.message.author.mention, delete_after=10)
        elif str(error) == "HTTPException: BAD REQUEST (status code: 400)":
            await context.message.channel.send("**Too many characters.**" + context.message.author.mention, delete_after=10)
        else:
            embed = discord.Embed(title=str(error), description=f'{context.message.author.mention}\n{context.message.content}')
            await self.client.get_channel(538719054479884300).send(embed=embed)
            await context.message.channel.send("You either dont have access to the command or you have entered something wrong."+context.message.author.mention, delete_after=10)



def setup(client):
    client.add_cog(errorHandlingCog(client))
