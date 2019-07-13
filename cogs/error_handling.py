from discord.ext import commands
import discord

class errorHandlingCog(commands.Cog):
  def __init__(self,client):
    self.client = client

  @commands.Cog.listener()
  async def on_command_error(self,ctx,error):
    if isinstance(error, commands.NoPrivateMessage):
      await ctx.message.channel.send("**private messages.**" + ctx.message.author.mention,delete_after=10)
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.message.channel.send("**Missing an argument.**" + ctx.message.author.mention,delete_after=10)
    elif isinstance(error, commands.DisabledCommand):
      await ctx.message.channel.send("**Command is disabled.**" + ctx.message.author.mention,delete_after=10)
    elif isinstance(error, commands.CheckFailure):
      await ctx.message.channel.send("**No permission.**" + ctx.message.author.mention,delete_after=10)
    elif isinstance(error, commands.CommandNotFound):
      await ctx.message.channel.send("**Wrong command.**" + ctx.message.author.mention,delete_after=10)
    elif str(error) == "HTTPException: BAD REQUEST (status code: 400)":
      await ctx.message.channel.send("**Too many characters.**" + ctx.message.author.mention,delete_after=10)
    else:
      embed = discord.Embed(title=str(error),description=f'{ctx.message.author.mention}\n{ctx.message.content}')
      await self.client.get_channel(538719054479884300).send(embed=embed)
      await ctx.message.channel.send("You either dont have access to the command or you have entered something wrong."+ctx.message.author.mention,delete_after=10)



def setup(client):
  client.add_cog(errorHandlingCog(client))