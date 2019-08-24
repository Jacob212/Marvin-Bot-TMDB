import discord
from discord.ext import commands
from utils.api_handler import Auth, Lists
from utils.sql import get_account_details, setup_account, update_access_token, update_list_id, update_account

class ManagementCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(description="An account has to be linked to use the watched list feature.", brief="Used to setup and link a TMDb account to this bot.", aliases=["Setup"])
    async def setup(self, context):
        await context.message.delete()
        account_details = get_account_details(context.author.id)
        if account_details is None or account_details[0] is None:
            await context.send("I have sent you more information to your DMs")
            response = Auth.request()
            embed = discord.Embed(title="Link", description='To use all the features of this bot you will need an account with The Movie Database and approve the bot to have access to your account. Respond with "approved" when you have finshed the links instructions', url=f'https://www.themoviedb.org/auth/access?request_token={response.request_token}')
            await context.author.send(embed=embed)
            await self.client.wait_for('message', check=lambda m: isinstance(m.channel, discord.DMChannel) and m.content in ["approved", "Approved"])
            approved = Auth.access(response.request_token)
            if account_details is None:
                created_list = Lists.create(approved.access_token)
                setup_account(context.author.name, context.author.id, approved.access_token, approved.account_id, created_list.id)
            elif account_details[2] is None:
                created_list = Lists.create(approved.access_token)
                update_account(context.author.id, approved.access_token, approved.account_id, created_list.id)
            else:
                update_access_token(context.author.id, approved.access_token)
        else:
            await context.send("You are already setup", delete_after=10)

    @commands.command(description="", brief="!!Not working on the api's end.!!", aliases=["Unlink"], enabled=False)
    async def unlink(self, context):
        await context.message.delete()
        bots_message = await context.send("Are you sure you want to unlink your TMDb account from this bot.")
        await bots_message.add_reaction("✅")
        await bots_message.add_reaction("❌")
        reaction, user = await self.client.wait_for("reaction_add", check=lambda r, u: r.emoji in ["✅", "❌"] and u.id == context.message.author.id and r.message.id == bots_message.id)
        if reaction.emoji == "✅":
            account_details = get_account_details(context.author.id)[0]
            Auth.delete(account_details)
            update_access_token(context.author.id, None)
        await bots_message.delete()

    @commands.command(description="", brief="Used to create new list if old one was deleted.", aliases=["List"], enabled=False)#hard to test this right now
    async def list(self, context):
        await context.message.delete()
        account_details = get_account_details(context.author.id)
        if account_details[2] is None:
            response = Lists.create(account_details[1])
            print(response.status_message)
            await context.send("A new list has been created.", delete_after=10)
        else:
            await context.send("There is already a list saved under your account.", delete_after=10)

    @commands.command(description="", brief="!!Not working on the api's end.!! Deletes your watched list. This cannot be undone.", aliases=["Delete"], enabled=False)
    async def delete(self, context):
        await context.message.delete()
        bots_message = await context.send("Are you sure you want to delete your watched list.")
        await bots_message.add_reaction("✅")
        await bots_message.add_reaction("❌")
        reaction, user = await self.client.wait_for("reaction_add", check=lambda r, u: r.emoji in ["✅", "❌"] and u.id == context.message.author.id and r.message.id == bots_message.id)
        if reaction.emoji == "✅":
            account_details = get_account_details(context.author.id)
            result = Lists.delete(account_details[2], account_details[0])
            update_list_id(context.author.id, None)
        await bots_message.delete()

def setup(client):
    client.add_cog(ManagementCommands(client))
