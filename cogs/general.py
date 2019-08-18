import asyncio
import re
import discord
from discord.ext import commands
from utils.sql import get_account_details
from utils.display_handler import SearchPages, WatchedPages, KeywordPages, DiscoverMoviesPages, DiscoverTVPages
from utils.file_handler import download, find_exact

class GeneralCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        download("data")

    @commands.command(description="Use -movies or -shows to filter to only one. You can select an item by typing its number in chat.", brief="Used to search for movies and tv shows.", aliases=["Search"])
    async def search(self, context, *args):
        options = {"media": None}
        query = []
        for arg in args:
            if arg == "-shows":
                options["media"] = "tv"
            elif arg == "-movies":
                options["media"] = "movie"
            else:
                query.append(arg)
        if not query:
            embed = discord.Embed(title="You have to enter something to search for.", description="eg ?search the flash")
            await context.send(embed=embed)
        else:
            options["query"] = " ".join(query)
            page = 1
            if context.author.id in globals():
                globals()[context.author.id].run = False
            globals()[context.author.id] = SearchPages(self.client, context, options, page)
            await globals()[context.author.id].main()

    @commands.command(description="You can also edit your list here by typing the number in chat that you want to change.", brief="Used to show yours or others watched list. (eg ?watched @Riot212)", aliases=["Watched"])
    async def watched(self, context, *args):
        options = {"media": None}
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
        globals()[context.author.id] = WatchedPages(self.client, context, options, page)
        await globals()[context.author.id].main()

    @commands.command(description="", brief="", aliases=["Keywords"])
    async def keywords(self, context, *keyword):
        options = {"query": " ".join(keyword)}
        page = 1
        if context.author.id in globals():
            globals()[context.author.id].run = False
        globals()[context.author.id] = KeywordPages(self.client, context, options, page)
        await globals()[context.author.id].main()

    @commands.command(description="", brief="", aliases=[])
    async def discover(self, context, *args):
        stuff = {}
        page = 1
        matches = re.finditer(r"[\+-][a-zA-z ]+(\+|-){0}", " ".join(args), re.IGNORECASE)
        for matchNum, match in enumerate(matches, start=1):
            matchString = match.group()
            result = find_exact("data", "keyword_ids", matchString.strip().strip("+-"))
            if result is None:
                continue
            if "+" in matchString:
                if "with_genres" in stuff:
                    stuff["with_genres"] = f'{stuff["with_genres"]},{result["id"]}'
                else:
                    stuff["with_genres"] = result["id"]
            elif "-" in matchString:
                if "without_genres" in stuff:
                    stuff["without_genres"] = f'{stuff["without_genres"]},{result["id"]}'
                else:
                    stuff["without_genres"] = result["id"]
        if stuff != {}:
            options = {
                "media":"movie",
                "query":stuff
                }
            if context.author.id in globals():
                globals()[context.author.id].run = False
            globals()[context.author.id] = DiscoverMoviesPages(self.client, context, options, page)
            await globals()[context.author.id].main()

    #doesnt work now but i want to make it work later
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
