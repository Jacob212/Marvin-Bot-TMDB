import asyncio
import re
import datetime
import discord
from discord.ext import commands
from utils import api_handler
from utils.sql import get_account_details

SEARCH = api_handler.Search()
LISTS = api_handler.Lists()
DETAILS = api_handler.Details()

EMBED_CFG = (
    ("original_name", "Original Title", False, None),
    ("original_title", "Original Title", False, None),
    ("release_date", None, True, lambda v: datetime.datetime.strptime(v, '%Y-%m-%d').strftime('%d/%m/%Y')),
    ("number_of_seasons", "Seasons", True, None),
    ("number_of_episodes", "Episodes", True, None),
    ("runtime", "Run Time", True, '{0} minutes'.format),
    ("episode_run_time", None, True, lambda v: '{0} minutes'.format(", ".join(str(time) for time in v))),
    ("languages", "Languages", True, lambda v: ", ".join(language.upper() for language in v)),
    ("spoken_languages", "Languages", True, lambda v: ", ".join(language['name'] for language in v)),
    ("first_air_date", None, True, lambda v: datetime.datetime.strptime(v, '%Y-%m-%d').strftime('%d/%m/%Y')),
    ("next_episode_to_air", None, True, lambda v: '{0} on {1}'.format(v["name"], datetime.datetime.strptime(v["air_date"], '%Y-%m-%d').strftime('%d/%m/%Y'))),
    ("genres", None, False, lambda v: ", ".join(genre['name'] for genre in v)),
    ("vote_average", "User score", True, lambda v: '{0}%'.format(int(v*10))),
    ("vote_count", "Votes", True, None)
    )

def embed_format(embed, detail):
    for attr, name, inline, fmt in EMBED_CFG:
        try:
            value = getattr(detail, attr)
            if value is None:
                continue
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


class DisplayHandler():
    def __init__(self, client, context, options):
        self.client = client
        self.context = context
        self.options = options
        self.results = None
        self.bots_message = None
        self.run = True

    async def arrow_pages(self, page):
        while self.run:
            message = ""
            if "movies" not in self.options and "shows" not in self.options:
                if str(self.context.command) == "search":
                    embed = discord.Embed(title="Search results for:", description=self.options["query"])
                    self.results, extra = SEARCH.multi(self.options["query"], page)
                elif str(self.context.command) == "watched":
                    embed = discord.Embed(title="Watched list of:", description=self.options["mention"])
                    self.results, extra = LISTS.get(self.options["listID"], self.options["latest"], page)
                for res in self.results:
                    if res.media_type == "movie":
                        message += f'{self.results.index(res)+1} - Movie: {res.title}\n'
                    elif res.media_type == "tv":
                        message += f'{self.results.index(res)+1} - TV: {res.name} {extra.comments["tv:"+str(res.id)] if str(self.context.command) == "watched" else ""}\n'
                    elif res.media_type == "person":
                        message += f'{self.results.index(res)+1} - Person: {res.name}\n'
            elif "movies" in self.options and str(self.context.command) == "search":
                embed = discord.Embed(title="Search results for:", description=self.options["query"])
                self.results, extra = SEARCH.movie(self.options["query"], page)
                for res in self.results:
                    message += f'{self.results.index(res)+1} - Movie: {res.title}\n'
            elif "shows" in self.options and str(self.context.command) == "search":
                embed = discord.Embed(title="Search results for:", description=self.options["query"])
                self.results, extra = SEARCH.tv(self.options["query"], page)
                for res in self.results:
                    message += f'{self.results.index(res)+1} - TV: {res.name}\n'
            embed.add_field(name=f'Page: {extra.page}/{extra.total_pages}   Total results: {extra.total_results}', value=message)
            if self.bots_message is None:
                self.bots_message = await self.context.send(embed=embed)
            else:
                await self.bots_message.edit(embed=embed)
            await self.bots_message.add_reaction("◀")
            await self.bots_message.add_reaction("▶")
            done, pending = await asyncio.wait([
                self.client.wait_for("message", timeout=600, check=lambda m: m.channel == self.context.channel and m.content.isdigit()),
                self.client.wait_for("reaction_add", timeout=600, check=lambda r, u: r.emoji in ["◀", "▶"] and u.id == self.context.message.author.id and r.message.id == self.bots_message.id)
                ], return_when=asyncio.FIRST_COMPLETED)
            for future in pending:
                future.cancel()  # we don't need these anymore
            try:
                response = done.pop().result()
            except asyncio.TimeoutError:
                break
            else:
                if not self.run:
                    break
                if isinstance(response, tuple):
                    reaction = response[0]
                    if reaction.emoji == "▶" and len(self.results) == 20:
                        page += 1
                    elif reaction.emoji == "◀" and page != 1:
                        page -= 1
                    await self.bots_message.remove_reaction("▶", self.context.message.author)
                    await self.bots_message.remove_reaction("◀", self.context.message.author)
                else:
                    await response.delete()
                    await self.details(int(response.content)-1)

    async def details(self, index):
        if index <= len(self.results):
            if "movies" in self.options or self.results[index].media_type == "movie":
                detail = DETAILS.movie(self.results[index].id)
                embed = discord.Embed(title=detail.title, description=f'{detail.overview}', url=f'https://www.imdb.com/title/{detail.imdb_id}', color=self.context.message.author.color.value)
            elif "tv" in self.options or self.results[index].media_type == "tv":
                detail = DETAILS.tv(self.results[index].id)
                embed = discord.Embed(title=detail.name, description=f'{detail.overview}', color=self.context.message.author.color.value)
            embed_format(embed, detail)
        else:
            embed = discord.Embed(title="That is not an option", description="Please go back", color=discord.Colour.dark_red())
        await self.bots_message.edit(embed=embed)
        await self.bots_message.remove_reaction("▶", self.client.user)
        await self.bots_message.add_reaction("⏬")
        await self.bots_message.add_reaction("❌")
        while self.run:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=600, check=lambda r, u: r.emoji in ["◀", "⏬", "❌"] and u.id == self.context.message.author.id and r.message.id == self.bots_message.id)
            except asyncio.TimeoutError:
                self.run = False
                break
            if reaction.emoji == "◀":
                await self.bots_message.remove_reaction("⏬", self.client.user)
                await self.bots_message.remove_reaction("❌", self.client.user)
                await self.bots_message.remove_reaction("◀", self.context.message.author)
                break
            elif reaction.emoji == "⏬":
                await self.bots_message.remove_reaction("⏬", self.context.message.author)
                await self.add_watchlist(index)
            elif reaction.emoji == "❌":
                await self.bots_message.remove_reaction("❌", self.context.message.author)
                await self.remove_watchlist(index)

    async def add_watchlist(self, index):
        if index <= len(self.results):
            if self.results[index].media_type == "movie":
                season = ""
                episode = ""
                embed = discord.Embed(title=f'Are you sure you want to add {self.results[index].title} to your watched list?')
                self.bots_message = await self.context.send(embed=embed)
            elif self.results[index].media_type == "tv":
                embed = discord.Embed(title=f'What season of {self.results[index].name} have you watched up too?')
                self.bots_message = await self.context.send(embed=embed)
                response = await self.client.wait_for('message', check=lambda m: m.channel == self.context.channel and m.content.isdigit())
                season = response.content
                await response.delete()
                embed = discord.Embed(title=f'What episode of {self.results[index].name} season {season} have you watched up too?')
                await self.bots_message.edit(embed=embed)
                response = await self.client.wait_for('message', check=lambda m: m.channel == self.context.channel and m.content.isdigit())
                episode = response.content
                await response.delete()
                embed = discord.Embed(title=f'Are you sure you want to add {self.results[index].name} - {season} - {episode} to your watched list')
                await self.bots_message.edit(embed=embed)
            await self.bots_message.add_reaction("✅")
            await self.bots_message.add_reaction("❌")
            while self.run:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=600, check=lambda r, u: r.emoji in ["✅", "❌"] and u.id == self.context.message.author.id and r.message.id == self.bots_message.id)
                except asyncio.TimeoutError:
                    self.run = False
                    break
                if reaction.emoji == "✅":
                    account_details = get_account_details(self.context.author.id)
                    payload = "{\"items\":[{\"media_type\":\""+self.results[index].media_type+"\",\"media_id\":"+str(self.results[index].id)+",\"comment\": \"S:"+season+" E:"+episode+"\"}]}"
                    LISTS.add_items(account_details[2], account_details[0], payload)
                    if self.results[index].media_type == "tv":
                        LISTS.update_items(account_details[2], account_details[0], payload)
                await self.bots_message.delete()
                break

    async def remove_watchlist(self, index):
        if index <= len(self.results):
            if self.results[index].media_type == "movie":
                embed = discord.Embed(title=f'Are you sure you want to remove {self.results[index].title} from your watched list?')
                self.bots_message = await self.context.send(embed=embed)
            elif self.results[index].media_type == "tv":
                embed = discord.Embed(title=f'Are you sure you want to remove {self.results[index].name} from your watched list?')
                self.bots_message = await self.context.send(embed=embed)
            await self.bots_message.add_reaction("✅")
            await self.bots_message.add_reaction("❌")
            while self.run:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=600, check=lambda r, u: r.emoji in ["✅", "❌"] and u.id == self.context.message.author.id and r.message.id == self.bots_message.id)
                except asyncio.TimeoutError:
                    self.run = False
                    break
                if reaction.emoji == "✅":
                    account_details = get_account_details(self.context.author.id)
                    payload = "{\"items\":[{\"media_type\":\""+self.results[index].media_type+"\",\"media_id\":"+str(self.results[index].id)+"}]}"
                    LISTS.remove_items(account_details[2], account_details[0], payload)
                await self.bots_message.delete()
                break

class GeneralCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(description="Use -movies or -shows to filter to only one. You can select an item by typing its number in chat.", brief="Used to search for movies and tv shows.", aliases=["Search"])
    async def search(self, context, *args):
        options = {}
        query = []
        for arg in args:
            if arg == "-shows":
                options["shows"] = True
            elif arg == "-movies":
                options["movies"] = True
            else:
                query.append(arg)
        if not query:
            embed = discord.Embed(title="You have to enter something to search for.",description="eg ?search the flash")
            await context.send(embed=embed)
        else:
            options["query"] = " ".join(query)
            page = 1
            if context.author.id in globals():
                globals()[context.author.id].run = False
            globals()[context.author.id] = DisplayHandler(self.client, context, options)
            await globals()[context.author.id].arrow_pages(page)

    @commands.command(description="You can also edit your list here by typing the number in chat that you want to change.", brief="Used to show yours or others watched list. (eg ?watched @Riot212)", aliases=["Watched"])
    async def watched(self, context, *args):
        options = {}
        options["mention"] = context.author.mention
        options["latest"] = "title.asc"
        search_user = context.author.id
        for arg in args:
            if re.match("(<@!?)[0-9]*(>)", arg):
                search_user = int(re.findall("\d+", arg)[0])
                options["mention"] = arg
            elif arg == "-latest":
                options["latest"] = "original_order.desc"
        options["listID"] = get_account_details(search_user)[2]
        page = 1
        if context.author.id in globals():
            globals()[context.author.id].run = False
        globals()[context.author.id] = DisplayHandler(self.client, context, options)
        await globals()[context.author.id].arrow_pages(page)

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
