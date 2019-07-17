from discord.ext import commands
import discord
import subprocess

#cog for owner only commands
class OwnerCog(commands.Cog):
  def __init__(self, client):
    self.client = client

  async def cog_command_error(self,ctx,error):
    print(f'{ctx.command.qualified_name}: {error}')

  #command for loading cogs. format ?load cogs."cog_name"
  @commands.command(name='load',aliases=["Load"],hidden=True)
  @commands.is_owner()
  async def load_cog(self, ctx, *, cog: str):
    try:
      self.client.load_extension(cog)
    except Exception as e:
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      await ctx.send('**`SUCCESS`**')

  #command for unloading cogs. format ?unload cogs."cog_name"
  @commands.command(name='unload',aliases=["Unload"],hidden=True)
  @commands.is_owner()
  async def unload_cog(self, ctx, *, cog: str):
    try:
      self.client.unload_extension(cog)
    except Exception as e:
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      await ctx.send('**`SUCCESS`**')

  #command for reloading cogs. format ?reload cogs."cog_name"
  @commands.command(name='reload',aliases=["Reload"],hidden=True)
  @commands.is_owner()
  async def reload_cog(self, ctx, *, cog: str):
    try:
      self.client.unload_extension(cog)
      self.client.load_extension(cog)
    except Exception as e:
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      await ctx.send('**`SUCCESS`**')

  #command for shutting down the bot.
  @commands.command(name='shutdown',aliases=["Shutdown"],hidden=True)
  @commands.is_owner()
  async def shutdown_client(self,ctx):
    await ctx.message.delete()
    await self.client.close()

  #List all servers that the bot is part of. Need to change it later when bot is in more servers
  @commands.command(name="servers",aliases=["Servers"],hidden=True)
  @commands.is_owner()
  async def list_servers(self,ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="List of servers that the bot is in",description=".....",color=ctx.message.author.color.value)
    for guild in self.client.guilds:
      embed.add_field(name=f'{guild.name} - {guild.id}',value=f'Owner: {guild.owner.mention}  Members: {guild.member_count}  Large: {guild.large}  Features: {guild.features}  Splash: {guild.splash}  Region: {guild.region}')
    await ctx.send(embed=embed)

  #pulls the latest update from github.
  @commands.command(name="update",aliases=["Update"],hidden=True)
  @commands.is_owner()
  async def update_bot(self,ctx):
    await ctx.message.delete()
    try:
      returned_value = subprocess.check_output("git pull",shell=True)
      embed = discord.Embed(title="Github Update",description=f'{returned_value.decode("utf-8")}',color=discord.Colour.green())
    except Exception as e:
      embed = discord.Embed(title="Github Update Failed",description=f'Update failed with following error: {type(e).__name__} - {e}',color=discord.Colour.red())
    await discord.Object(id=538719054479884300).send(embed=embed)

def setup(client):
  client.add_cog(OwnerCog(client))