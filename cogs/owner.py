import discord
from discord.ext import commands
from .utils.api_handler import purge_cache

#cog for owner only commands
class OwnerCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def cog_command_error(self, context, error):
        print(f'{context.command.qualified_name}: {error}')

    #command for loading cogs. format ?load cogs."cog_name"
    @commands.command(name='load', aliases=["Load"], hidden=True)
    @commands.is_owner()
    async def load_cog(self, context, *, cog: str):
        try:
            self.client.load_extension(cog)
        except Exception as e:
            await context.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await context.send('**`SUCCESS`**')

    #command for unloading cogs. format ?unload cogs."cog_name"
    @commands.command(name='unload', aliases=["Unload"], hidden=True)
    @commands.is_owner()
    async def unload_cog(self, context, *, cog: str):
        try:
            self.client.unload_extension(cog)
        except Exception as e:
            await context.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await context.send('**`SUCCESS`**')

    #command for reloading cogs. format ?reload cogs."cog_name"
    @commands.command(name='reload', aliases=["Reload"], hidden=True)
    @commands.is_owner()
    async def reload_cog(self, context, *, cog: str):
        try:
            self.client.unload_extension(cog)
            self.client.load_extension(cog)
        except Exception as e:
            await context.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await context.send('**`SUCCESS`**')

    @commands.command(aliases=["Clear"], hidden=True)
    @commands.is_owner()
    async def clear(self, context):
        purge_cache()

    #command for shutting down the bot.
    @commands.command(name='shutdown', aliases=["Shutdown"], hidden=True)
    @commands.is_owner()
    async def shutdown_client(self, context):
        await context.message.delete()
        await self.client.close()

    #List all servers that the bot is part of. Need to change it later when bot is in more servers
    @commands.command(name="servers", aliases=["Servers"], hidden=True)
    @commands.is_owner()
    async def list_servers(self, context):
        await context.message.delete()
        embed = discord.Embed(title="List of servers that the bot is in", description=".....", color=context.message.author.color.value)
        for guild in self.client.guilds:
            embed.add_field(name=f'{guild.name} - {guild.id}', value=f'Owner: {guild.owner.mention}  Members: {guild.member_count}  Large: {guild.large}  Features: {guild.features}  Splash: {guild.splash}  Region: {guild.region}')
        await context.send(embed=embed)

def setup(client):
    client.add_cog(OwnerCog(client))
