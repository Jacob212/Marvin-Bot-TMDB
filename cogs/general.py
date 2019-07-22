import asyncio
import sqlite3
import re
import discord
from discord.ext import commands
import api_handler

CONN = sqlite3.connect("discord.db")
C = CONN.cursor()
C.execute("CREATE TABLE IF NOT EXISTS accounts (userName TEXT NOT NULL,discordID INTEGER NOT NULL PRIMARY KEY UNIQUE,accessToken  TEXT UNIQUE,accountID TEXT UNIQUE,listID INTEGER UNIQUE);")
CONN.commit()

SEARCH = api_handler.Search()
AUTH = api_handler.Auth()
LISTS = api_handler.Lists()
DETAILS = api_handler.Details()

EMBED_CFG = (
    ("original_name", "Original Title", False, None),
    ("original_title", "Original Title", False, None),
    ("release_date", None, True, None),
    ("number_of_seasons", "Seasons", True, None),
    ("number_of_episodes", "Episodes", True, None),
    ("runtime", "Run Time", True, '{0} minutes'.format),
    ("episode_run_time", "Episode run time", True, lambda v: '{0} minutes'.format(", ".join(str(time) for time in v))),
    ("languages", "Languages", True, lambda v: ", ".join(language.upper() for language in v)),
    ("spoken_languages", "Languages", True, lambda v: ", ".join(language['name'] for language in v)),
    ("genres", None, False, lambda v: ", ".join(genre['name'] for genre in v)),
    ("vote_average", "User score", True, lambda v: '{0}%'.format(int(v*10))),
    ("vote_count", "Votes", True, None)
)

def embed_format(embed, detail):
    for attr, name, inline, fmt in EMBED_CFG:
        try:
            value = getattr(detail, attr)
        except AttributeError:
            continue
        if name is None:
            name = attr.replace('_', ' ').title()
        if fmt is not None:
            value = fmt(value)
        embed.add_field(name=name, value=value, inline=inline)
    try:
        value = getattr(detail, "backdrop_path")
    except AttributeError:
        pass
    else:
        embed.set_image(url=f'https://image.tmdb.org/t/p/original{value}')

class GeneralCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def arrow_pages(self, context, options, page, bots_message=None):
        while True:
            message = ""
            if "movies" not in options and "shows" not in options:
                if str(context.command) == "search":
                    embed = discord.Embed(title="Search results for:", description=options["query"])
                    results, extra = SEARCH.multi(options["query"], page)
                elif str(context.command) == "watched":
                    embed = discord.Embed(title="Watched list of:", description=options["mention"])
                    results, extra = LISTS.get(options["listID"], options["latest"], page)
                for res in results:
                    if res.media_type == "movie":
                        message += f'{results.index(res)+1} - Movie: {res.title}\n'
                    elif res.media_type == "tv":
                        message += f'{results.index(res)+1} - TV: {res.name} {extra.comments["tv:"+str(res.id)] if str(context.command) == "watched" else ""}\n'
                    elif res.media_type == "person":
                        message += f'{results.index(res)+1} - Person: {res.name}\n'
            elif "movies" in options and str(context.command) == "search":
                embed = discord.Embed(title="Search results for:", description=options["query"])
                results, extra = SEARCH.movie(options["query"], page)
                for res in results:
                    message += f'{results.index(res)+1} - Movie: {res.title}\n'
            elif "shows" in options and str(context.command) == "search":
                embed = discord.Embed(title="Search results for:", description=options["query"])
                results, extra = SEARCH.tv(options["query"], page)
                for res in results:
                    message += f'{results.index(res)+1} - TV: {res.name}\n'
            embed.add_field(name=f'Page: {extra.page}/{extra.total_pages}   Total results: {extra.total_results}', value=message)
            if bots_message is None:
                bots_message = await context.send(embed=embed)
            else:
                await bots_message.edit(embed=embed)
            await bots_message.add_reaction("◀")
            await bots_message.add_reaction("▶")
            done, pending = await asyncio.wait([
                self.client.wait_for("message", check=lambda m: m.channel == context.channel and m.content.isdigit()),
                self.client.wait_for("reaction_add", check=lambda r, u: (r.emoji == "▶" or r.emoji == "◀") and u.id == context.message.author.id and r.message.id == bots_message.id)
                ], return_when=asyncio.FIRST_COMPLETED)
            for future in pending:
                future.cancel()  # we don't need these anymore
            try:
                response = done.pop().result()
            except:
                pass
            finally:
                if isinstance(response, tuple):
                    reaction = response[0]
                    if reaction.emoji == "▶" and len(results) == 20:
                        page += 1
                    elif reaction.emoji == "◀" and page != 1:
                        page -= 1
                    await bots_message.remove_reaction("▶", context.message.author)
                    await bots_message.remove_reaction("◀", context.message.author)
                else:
                    await response.delete()
                    await self.details(context, options, results, bots_message, int(response.content)-1)

    async def details(self, context, options, results, bots_message, index):
        if index <= len(results):
            if results[index].media_type == "movie" or "movies" in options:
                detail = DETAILS.movie(results[index].id)
                embed = discord.Embed(title=detail.title, description=f'{detail.overview}', url=f'https://www.imdb.com/title/{detail.imdb_id}', color=context.message.author.color.value)
            elif results[index].media_type == "tv" or "tv" in options:
                detail = DETAILS.tv(results[index].id)
                embed = discord.Embed(title=detail.name, description=f'{detail.overview}', color=context.message.author.color.value)
            embed_format(embed, detail)
        else:
            embed = discord.Embed(title="That is not an option", description="Please go back", color=discord.Colour.dark_red())
        await bots_message.edit(embed=embed)
        await bots_message.remove_reaction("▶", self.client.user)
        await bots_message.add_reaction("⏬")
        while True:
            reaction, user = await self.client.wait_for("reaction_add", check=lambda r, u: (r.emoji == "⏬" or r.emoji == "◀") and u.id == context.message.author.id and r.message.id == bots_message.id)
            if reaction.emoji == "◀":
                await bots_message.remove_reaction("⏬", self.client.user)
                await bots_message.remove_reaction("◀", context.message.author)
                break
            elif reaction.emoji == "⏬":
                await bots_message.remove_reaction("⏬", context.message.author)
                await self.add_watchlist(context, results, index)

    async def add_watchlist(self, context, results, index):
        if index <= len(results):
            if results[index].media_type == "movie":
                season = ""
                episode = ""
                embed = discord.Embed(title=f'Are you sure you want to add {results[index].title} to your watched list')
                bots_message = await context.send(embed=embed)
            elif results[index].media_type == "tv":
                embed = discord.Embed(title=f'What season of {results[index].name} have you watched up too?')
                bots_message = await context.send(embed=embed)
                response = await self.client.wait_for('message', check=lambda m: m.channel == context.channel and m.content.isdigit())
                season = response.content
                await response.delete()
                embed = discord.Embed(title=f'What episode of {results[index].name} season {season} have you watched up too?')
                await bots_message.edit(embed=embed)
                response = await self.client.wait_for('message', check=lambda m: m.channel == context.channel and m.content.isdigit())
                episode = response.content
                await response.delete()
                embed = discord.Embed(title=f'Are you sure you want to add {results[index].name} - {season} - {episode} to your watched list')
                await bots_message.edit(embed=embed)
            await bots_message.add_reaction("✅")
            await bots_message.add_reaction("❌")
            while True:
                reaction, user = await self.client.wait_for("reaction_add", check=lambda r, u: (r.emoji == "✅" or r.emoji == "❌") and u.id == context.message.author.id and r.message.id == bots_message.id)
                if reaction.emoji == "✅":
                    C.execute("SELECT discordID, accessToken, accountID, listID FROM accounts WHERE discordID = ?;", (context.author.id,))
                    account_details = C.fetchone()
                    payload = "{\"items\":[{\"media_type\":\""+results[index].media_type+"\",\"media_id\":"+str(results[index].id)+",\"comment\": \"S:"+season+" E:"+episode+"\"}]}"
                    results, extra = LISTS.add_items(account_details[3], account_details[1], payload)
                    if results[index].media_type == "tv":
                        results, extra = LISTS.update_items(account_details[3], account_details[1], payload)
                await bots_message.delete()
                break

    @commands.command(description="", brief="", aliases=["Search"])
    async def search(self, context, *args):
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
        await self.arrow_pages(context, options, page)

    @commands.command(description="", brief="", aliases=["Watched"])
    async def watched(self, context, *args):
        options = {}
        options["mention"] = context.author.mention
        options["latest"] = "title.asc"
        search_user = context.author.id
        for part in args:
            if re.match("(<@!?)[0-9]*(>)", part):
                search_user = int(re.findall("\d+", part)[0])
                options["mention"] = part
            elif part == "-latest":
                options["latest"] = "original_order.desc"
        C.execute("SELECT listID FROM accounts WHERE discordID = ?;", (search_user, ))
        options["listID"] = C.fetchall()[0][0]
        page = 1
        await self.arrow_pages(context, options, page)

    #doesnt work now but i want to make it work later
    # @commands.command(description="", brief="", aliases=["Watch"])
    # async def watch(self, context, arg=None):
    #     await context.message.delete()
    #     if arg is None:
    #         await context.send("You have to enter an option to use this command")
    #     elif arg.isdigit() and context.message.author in globals():
    #         await globals()[context.message.author].add_watchlist(int(arg)-1)
    #     else:
    #         await context.send("That is not a valid option")

    # @commands.command()
    # async def discover_movie(self, context, *args):
    #     arg = " ".join(args)
    #     search, pages = discover.discover_movie(arg)
    #     message = ""
    #     for res in search:
    #         if res.media_type == "movie":
    #             message += f'{res.title}  {res.id}  {res.media_type}\n'
    #         else:
    #             message += f'{res.name}  {res.id}  {res.media_type}\n'
    #     embed = discord.Embed(title="Search results:", description="bob")
    #     embed.add_field(name=f'Page: {pages.page}/{pages.total_pages}   Total results:{pages.total_results}', value=message)
    #     await context.send(embed=embed)

    @commands.command(description="", brief="", aliases=["Setup"])
    async def setup(self, context):
        await context.message.delete()
        C.execute("SELECT discordID, accessToken, accountID FROM accounts WHERE discordID = ?;", (context.author.id,))
        if C.fetchall() == []:
            response = AUTH.request()
            embed = discord.Embed(title="Link", description="To use all the features of this bot you will need an account with the movie database and approve the bot to have access ", url=f'https://www.themoviedb.org/auth/access?request_token={response.request_token}', color=context.message.author.color.value)
            await context.author.send(embed=embed)
            await self.client.wait_for('message', check=lambda m: isinstance(m.channel, discord.DMChannel) and m.content == "approved")
            response2 = AUTH.access(response.request_token)
            print(response2)
            response3 = LISTS.create(response2.access_token)
            C.execute("INSERT INTO accounts VALUES(?,?,?,?,?)", (context.author.name, context.author.id, response2.access_token, response2.account_id, response3.id))
            CONN.commit()
        else:
            await context.send("You are already setup", delete_after=10)

    # @commands.command(name="filter",description="filter a list of movies by genre....etc")
    # async def filter_movies(self,context,*args):
    #     await context.message.delete()
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
    #             await context.send("One or more of your options are wrong")
    #             break
    #     else:
    #         globals()[context.message.author.id] = arrow_pages(self.client,context,params=params,tv=tv)
    #         await globals()[context.message.author.id].display()

    # @commands.command()
    # async def fitler_movies(self,context,*args):
    #     await context.message.delete()
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
    client.add_cog(GeneralCommands(client))
