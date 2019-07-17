import discord
import api_handler
from discord.ext import commands
import sqlite3
import re

conn = sqlite3.connect("discord.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS accounts (userName TEXT NOT NULL,discordID INTEGER NOT NULL PRIMARY KEY UNIQUE,accessToken  TEXT UNIQUE,accountID TEXT UNIQUE,listID INTEGER UNIQUE);")
conn.commit()

search = api_handler.search()
auth = api_handler.auth()
lists = api_handler.lists()
details = api_handler.details()

class display_handler():
    def __init__(self,client,context):
        self.client = client
        self.context = context

    async def arrowPages(self,args,page):
        while True:
            message = ""
            if str(self.context.command) == "search":
                if "movies" in args:
                    embed = discord.Embed(title="Search results for:",description=args["query"])
                    self.results,extra = search.movie(args["query"],page)
                    for res in self.results:
                        message += f'{self.results.index(res)+1} - Movie: {res.title}\n'
                elif "shows" in args:
                    embed = discord.Embed(title="Search results for:",description=args["query"])
                    self.results,extra = search.tv(args["query"],page)
                    for res in self.results:
                        message += f'{self.results.index(res)+1} - TV: {res.name}\n'
                else:
                    embed = discord.Embed(title="Search results for:",description=args["query"])
                    self.results,extra = search.multi(args["query"],page)
            elif str(self.context.command) == "watched":
                embed = discord.Embed(title="Watched list of:",description=args["mention"])
                self.results,extra = lists.get(args["listID"],page)
            if "movies" not in args and "shows" not in args:
                for res in self.results:
                    if res.media_type == "movie":
                        message += f'{self.results.index(res)+1} - Movie: {res.title}\n'
                    elif res.media_type == "tv":
                        message += f'{self.results.index(res)+1} - TV: {res.name}\n'
                    elif res.media_type == "person":
                        message += f'{self.results.index(res)+1} - Person: {res.name}\n'
            embed.add_field(name=f'Page: {extra.page}/{extra.total_pages}   Total results: {extra.total_results}',value=message)
            try:
                await self.msg.edit(embed=embed)
            except NameError:
                self.msg = await self.context.send(embed=embed)
            await self.msg.add_reaction("◀")
            await self.msg.add_reaction("▶")
            reaction, user = await self.client.wait_for("reaction_add", check=lambda r, u: (r.emoji == "▶" or r.emoji == "◀") and u.id == self.context.message.author.id and r.message.id == self.msg.id)
            if reaction.emoji == "▶" and len(self.results) == 20:
                page += 1
            elif reaction.emoji == "◀" and page != 1:
                page -= 1
            await self.msg.remove_reaction("▶",self.context.message.author)
            await self.msg.remove_reaction("◀",self.context.message.author)

    async def details(self,index):
        if index <= len(self.results):
            if self.results[index].media_type == "movie":
                detail = details.movie(self.results[index].id)
                embed = discord.Embed(title=detail.title,description=f'{detail.overview}',url=f'https://www.imdb.com/title/{detail.imdb_id}',color=self.context.message.author.color.value)
                embed.add_field(name="Original Title",value=detail.original_title)
                embed.add_field(name="Release Date",value=detail.release_date)
                embed.add_field(name="Run Time",value=detail.runtime)
            elif self.results[index].media_type == "tv":
                detail = details.tv(self.results[index].id)
                embed = discord.Embed(title=detail.name,description=f'{detail.overview}',color=self.context.message.author.color.value)
                embed.add_field(name="Original Title",value=detail.original_name)
                embed.add_field(name="Seasons",value=detail.number_of_seasons)
                embed.add_field(name="Episodes",value=detail.number_of_episodes)
            embed.add_field(name="Genres",value=", ".join([genre['name'] for genre in detail.genres]))
            embed.set_image(url=f'https://image.tmdb.org/t/p/original{detail.backdrop_path}')
        else:
            embed = discord.Embed(title="That is not an option",description="Please go back",color=discord.Colour.dark_red())
        await self.msg.edit(embed=embed)
        await self.msg.remove_reaction("▶",self.client.user)
        await self.msg.add_reaction("⏬")
        while True:
            reaction, user = await self.client.wait_for("reaction_add", check=lambda r, u: (r.emoji == "⏬" or r.emoji == "◀") and u.id == self.context.message.author.id and r.message.id == self.msg.id)
            if reaction.emoji == "◀":
                await self.msg.remove_reaction("⏬",self.client.user)
                break
            elif reaction.emoji == "⏬":
                await self.add_watchlist(index)
            await self.msg.remove_reaction("◀",self.context.message.author)
            await self.msg.remove_reaction("⏬",self.context.message.author)

    async def add_watchlist(self,index=None):
        if index <= len(self.results):
            if self.results[index].media_type == "movie":
                embed = discord.Embed(title=f'Are you sure you want to add {self.results[index].title} to your watched list')
            elif self.results[index].media_type == "tv":
                embed = discord.Embed(title=f'Are you sure you want to add {self.results[index].name} to your watched list')
            msg2 = await self.context.send(embed=embed)
            await msg2.add_reaction("✅")
            await msg2.add_reaction("❌")
            while True:
                reaction, user = await self.client.wait_for("reaction_add", check=lambda r, u: (r.emoji == "✅" or r.emoji == "❌") and u.id == self.context.message.author.id and r.message.id == msg2.id)
                if reaction.emoji == "✅":
                    c.execute("SELECT discordID, accessToken, accountID, listID FROM accounts WHERE discordID = ?;",(self.context.author.id,))
                    accountDetails = c.fetchone()
                    payload = "{\"items\":[{\"media_type\":\""+self.results[index].media_type+"\",\"media_id\":"+str(self.results[index].id)+"}]}"
                    results,extra = lists.add_items(accountDetails[3],accountDetails[1],payload)
                await msg2.delete()
                break

class generalCommands(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.command(description="",brief="",aliases=["Search"])
    async def search(self,ctx,*args):
        options = {}
        query = []
        for part in args:
            if part == "--shows":
                options["shows"] = True
            elif part == "--movies":
                options["movies"] = True
            else:
                query.append(part)
        options["query"] = " ".join(query)
        page = 1
        globals()[ctx.message.author] = display_handler(self.client,ctx)
        await globals()[ctx.message.author].arrowPages(options,page)

    @commands.command(description="",brief="",aliases=["Select"])
    async def select(self,ctx, arg=None):
        await ctx.message.delete()
        if arg is None:
            await ctx.send("You have to enter an option to use this command")
        elif arg.isdigit() and ctx.message.author in globals():
            await globals()[ctx.message.author].details(int(arg)-1)
        else:
            await context.send("That is not a valid option")

    @commands.command(description="",brief="",aliases=["Watch"])
    async def watch(self,ctx,arg=None):
        await ctx.message.delete()
        if arg is None:
            await ctx.send("You have to enter an option to use this command")
        elif arg.isdigit() and ctx.message.author in globals():
            await globals()[ctx.message.author].add_watchlist(int(arg)-1)
        else:
            await context.send("That is not a valid option")

    @commands.command()
    async def discover_movie(self,ctx,*args):
        arg = " ".join(args)
        search,pages = discover.discover_movie(arg)
        message = ""
        for res in search:
            if res.media_type == "movie":
                message += f'{res.title}  {res.id}  {res.media_type}\n'
            else:
                message += f'{res.name}  {res.id}  {res.media_type}\n'
        embed = discord.Embed(title="Search results:",description="bob")
        embed.add_field(name=f'Page: {pages.page}/{pages.total_pages}   Total results:{pages.total_results}',value=message)
        await ctx.send(embed=embed)

    @commands.command(description="",brief="",aliases=["Setup"])
    async def setup(self,ctx):
        await ctx.message.delete()
        c.execute("SELECT discordID, accessToken, accountID FROM accounts WHERE discordID = ?;",(ctx.author.id,))
        if c.fetchall() == []:
            response = auth.request()
            embed = discord.Embed(title="Link",description="To use all the features of this bot you will need an account with the movie database and approve the bot to have access ",url=f'https://www.themoviedb.org/auth/access?request_token={response.request_token}',color=ctx.message.author.color.value)
            await ctx.author.send(embed = embed)
            msg = await self.client.wait_for('message', check=lambda m: isinstance(m.channel, discord.DMChannel) and m.content == "approved")
            response2 = auth.access(response.request_token)
            print(response2)
            response3 = lists.create(response2.access_token)
            c.execute("INSERT INTO accounts VALUES(?,?,?,?,?)", (ctx.author.name,ctx.author.id,response2.access_token,response2.account_id,response3.id))
            conn.commit()
        else:
            await ctx.send("You are already setup",delete_after=10)

    @commands.command()
    async def watched(self,ctx,*arg):
        options = {}
        options["mention"] = ctx.author.mention
        searchUser = ctx.author.id
        for x in arg:
            if re.match("(<@!?)[0-9]*(>)",x):
                searchUser = int(re.findall("\d+",x)[0])
                options["mention"] = x
        c.execute("SELECT listID FROM accounts WHERE discordID = ?;",(searchUser,))
        options["listID"] = c.fetchall()[0][0]
        page = 1
        globals()[ctx.message.author] = display_handler(self.client,ctx)
        await globals()[ctx.message.author].arrowPages(options,page)


    # @commands.command(name="filter",description="filter a list of movies by genre....etc")
    # async def filter_movies(self,ctx,*args):
    #     await ctx.message.delete()
    #     paramsList = ["year","genre","other"]
    #     params = {}
    #     key = "genre"
    #     tv = False
    #     for arg in args:
    #         if re.match("--tv",arg):
    #             tv = True
    #         elif re.match("--",arg):
    #             key = arg.strip("-")
    #         else:
    #         if key in params:
    #             params[key] += " "+arg
    #         else:
    #             params[key] = arg
    #     for key,val in params.items():
    #         if key not in paramsList:
    #             await ctx.send("One or more of your options are wrong")
    #             break
    #     else:
    #         globals()[ctx.message.author.id] = arrowPages(self.client,ctx,params=params,tv=tv)
    #         await globals()[ctx.message.author.id].display()

    # @commands.command()
    # async def fitler_movies(self,ctx,*args):
    #     await ctx.message.delete()
    #     paramsList = ["--year","--genre"]
    #     params = {}
    #     key = "--genre"
    #     tv = False
    #     for arg in args:
    #         if arg == "--tv":
    #             tv = True
    #         elif arg in paramsList:
    #             key = arg.strip("-")
    #         if key in params:
    #             params[key] += " "+arg
    #         else:
    #             params[key] = arg

def setup(client):
    client.add_cog(generalCommands(client))