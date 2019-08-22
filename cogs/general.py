import asyncio
import re
import discord
from discord.ext import commands
from utils.sql import get_account_details
from utils.display_handler import SearchPages, WatchedPages, KeywordPages, DiscoverMoviesPages, DiscoverTVPages
from utils.file_handler import download, make_genre_ids_file

class GeneralCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        #download("data")
        make_genre_ids_file("data")

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

    @commands.command(description="You can filter movies by entering genres and keywords with + or - (include, exclude) before the genre or keyword. e.g ?movies +action -adventure.", brief="Used to filter movies based on genres. Do ?help movies for more info.", aliases=["Movies"])
    async def movies(self, context, *args):
        page = 1
        genre_matches = re.finditer(r"[\+-][a-zA-z &]+", " ".join(args), re.IGNORECASE)
        year_matches = re.search(r"-{2}\d{4}", " ".join(args))
        options = {
            "media": "movie",
            "matches": genre_matches,
            "year": year_matches
            }
        if context.author.id in globals():
            globals()[context.author.id].run = False
        globals()[context.author.id] = DiscoverMoviesPages(self.client, context, options, page)
        await globals()[context.author.id].before_main()

    @commands.command(description="You can filter tv shows by entering genres and keywords with + or - (include, exclude) before the genre or keyword. e.g ?shows +action -adventure.", brief="Used to filter tv shows based on genres. Do ?help shows for more info.", aliases=["Shows"])
    async def shows(self, context, *args):
        page = 1
        genre_matches = re.finditer(r"[\+-][a-zA-z &]+", " ".join(args), re.IGNORECASE)
        year_matches = re.search(r"-{2}\d{4}", " ".join(args))
        options = {
            "media": "tv",
            "matches": genre_matches,
            "year": year_matches
            }
        if context.author.id in globals():
            globals()[context.author.id].run = False
        globals()[context.author.id] = DiscoverTVPages(self.client, context, options, page)
        await globals()[context.author.id].before_main()

def setup(client):
    client.add_cog(GeneralCommands(client))
