import discord
import asyncio
import datetime
from utils import api_handler

SEARCH = api_handler.Search()
LISTS = api_handler.Lists()
DETAILS = api_handler.Details()

movie = (
    ("title", "overview", "imdb_id"), 
    ("original_title", "Original Title", False, None),
    ("release_date", None, True, lambda v: datetime.datetime.strptime(v, '%Y-%m-%d').strftime('%d/%m/%Y')),
    ("runtime", "Run Time", True, '{0} minutes'.format),
    ("spoken_languages", "Languages", True, lambda v: ", ".join(language['name'] for language in v)),
    ("genres", None, False, lambda v: ", ".join(genre['name'] for genre in v)),
    ("vote_average", "User score", True, lambda v: '{0}%'.format(int(v*10))),
    ("vote_count", "Votes", True, None)     
    )

tv = (
    ("name", "overview", None), 
    ("original_name", "Original Title", False, None),
    ("number_of_seasons", "Seasons", True, None),
    ("number_of_episodes", "Episodes", True, None),
    ("episode_run_time", None, True, lambda v: '{0} minutes'.format(", ".join(str(time) for time in v))),
    ("languages", "Languages", True, lambda v: ", ".join(language.upper() for language in v)),
    ("first_air_date", None, True, lambda v: datetime.datetime.strptime(v, '%Y-%m-%d').strftime('%d/%m/%Y')),
    ("next_episode_to_air", None, True, lambda v: '{0} on {1}'.format(v["name"], datetime.datetime.strptime(v["air_date"], '%Y-%m-%d').strftime('%d/%m/%Y'))),
    ("genres", None, False, lambda v: ", ".join(genre['name'] for genre in v)),
    ("vote_average", "User score", True, lambda v: '{0}%'.format(int(v*10))),
    ("vote_count", "Votes", True, None)      
    )

person = (
    ("name", "biography", "imdb_id"),
    ("name")
    )

def embed_format(detail, media, color):
    try:
        getattr(detail, globals()[media][0][2])
        url = f'https://www.imdb.com/{globals()[media][0][0]}/{getattr(detail, globals()[media][0][2])}'
    except TypeError:
        url = None  
    embed = discord.Embed(title=getattr(detail, globals()[media][0][0]),
        description=f'{getattr(detail, globals()[media][0][1])}',
        url=url,
        color=color)
    for attr, name, inline, fmt in globals()[media][1:]:
        try:
            value = getattr(detail, attr)
            if value is None or value == "":
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
    return embed

class DisplayHandler():
    def __init__(self, client, context, options):
        self.client = client
        self.context = context
        self.options = options
        self.results = None
        self.bots_message = None
        self.run = True

    async def wait_for_message(self):
        return self.client.wait_for("message", timeout=600, check=lambda m: m.channel == self.context.channel and m.content.isdigit() and m.author.id == self.context.message.author.id)

    async def wait_for_reaction(self, reactions, message):
        try:
            return await self.client.wait_for("reaction_add", timeout=6, check=lambda r, u: r.emoji in reactions and u.id == self.context.message.author.id and r.message.id == message.id)
        except asyncio.TimeoutError:
            self.run = False
            return None, None

    async def wait_for_both(self, reactions):
        try:
            done, pending = await asyncio.wait([
                self.client.wait_for("message", timeout=600, check=lambda m: m.channel == self.context.channel and m.content.isdigit() and m.author.id == self.context.message.author.id),
                self.client.wait_for("reaction_add", timeout=600, check=lambda r, u: r.emoji in ["◀", "▶"] and u.id == self.context.message.author.id and r.message.id == self.bots_message.id)
                ], return_when=asyncio.FIRST_COMPLETED)
        except asyncio.TimeoutError:
            self.run = False
            return None
        else:
            for future in pending:
                future.cancel()
            return done.pop().result()

    async def add_reactions(self, reactions, message):
        for reaction in reactions:
            await message.add_reaction(reaction)

    async def remove_reactions(self, reactions, message, author):
        for reaction in reactions:
            await message.remove_reaction(reaction, author)

    def create_list(self, results, media_type):
        message = ""
        for result in results:
            if media_type == None:
                message += f'{results.index(result)+1} - {result.media_type.title()}: {getattr(result, globals()[result.media_type][0][0])}\n'
            else:
                message += f'{results.index(result)+1} - {media_type.title()}: {getattr(result, globals()[media_type][0][0])}\n'
        return message

    async def arrow_pages(self, page):
        while self.run:
            message = ""
            if self.options["media"] == None:
                if str(self.context.command) == "search":
                    embed = discord.Embed(title="Search results for:", description=self.options["query"])
                    self.results, extra = SEARCH.multi(self.options["query"], page)
                elif str(self.context.command) == "watched":
                    embed = discord.Embed(title="Watched list of:", description=self.options["mention"])
                    self.results, extra = LISTS.get(self.options["listID"], self.options["latest"], page)
            elif self.options["media"] == "movie" and str(self.context.command) == "search":
                embed = discord.Embed(title="Search results for:", description=self.options["query"])
                self.results, extra = SEARCH.movie(self.options["query"], page)
            elif self.options["media"] == "tv" and str(self.context.command) == "search":
                embed = discord.Embed(title="Search results for:", description=self.options["query"])
                self.results, extra = SEARCH.tv(self.options["query"], page)
            message = self.create_list(self.results, self.options["media"])
            if message == "":
                message = "Nothing could be found for this search."
            embed.add_field(name=f'Page: {extra.page}/{extra.total_pages}   Total results: {extra.total_results}', value=message)
            if self.bots_message is None:
                self.bots_message = await self.context.send(embed=embed)
            else:
                await self.bots_message.edit(embed=embed)
            await self.add_reactions(["◀", "▶"], self.bots_message)
            
            response = await self.wait_for_both(["◀", "▶"])

            if not self.run:
                break
            if isinstance(response, tuple):
                reaction = response[0]
                if reaction.emoji == "▶" and len(self.results) == 20:
                    page += 1
                elif reaction.emoji == "◀" and page != 1:
                    page -= 1
                await self.remove_reactions(["◀", "▶"], self.bots_message, self.context.message.author)
            else:
                await response.delete()
                await self.details(int(response.content)-1)

    async def details(self, index):
        if index <= len(self.results):
            if self.options["media"] == "movie" or self.results[index].media_type == "movie":
                detail = DETAILS.movie(self.results[index].id)
                embed = embed_format(detail, "movie", self.context.message.author.color.value)
            elif self.options["media"] == "tv" or self.results[index].media_type == "tv":
                detail = DETAILS.tv(self.results[index].id)
                embed = embed_format(detail, "tv", self.context.message.author.color.value)
        else:
            embed = discord.Embed(title="That is not an option", description="Please go back", color=discord.Colour.dark_red())
        await self.bots_message.edit(embed=embed)
        await self.bots_message.remove_reaction("▶", self.client.user)
        await self.add_reactions(["⏬", "❌"], self.bots_message)
        while self.run:
            reaction, user = await self.wait_for_reaction(["◀", "⏬", "❌"], self.bots_message)
            if not self.run:
                break
            if reaction.emoji == "◀":
                await self.remove_reactions(["⏬", "❌"], self.bots_message, self.client.user)
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
                temp_message = await self.context.send(embed=embed)
            elif self.results[index].media_type == "tv":
                embed = discord.Embed(title=f'What season of {self.results[index].name} have you watched up too?')
                temp_message = await self.context.send(embed=embed)
                response = await self.client.wait_for('message', check=lambda m: m.channel == self.context.channel and m.content.isdigit())
                season = response.content
                await response.delete()
                embed = discord.Embed(title=f'What episode of {self.results[index].name} season {season} have you watched up too?')
                await temp_message.edit(embed=embed)
                response = await self.client.wait_for('message', check=lambda m: m.channel == self.context.channel and m.content.isdigit())
                episode = response.content
                await response.delete()
                embed = discord.Embed(title=f'Are you sure you want to add {self.results[index].name} - {season} - {episode} to your watched list')
                await temp_message.edit(embed=embed)
            await self.add_reactions(["✅", "❌"], temp_message)
            while self.run:
                reaction, user = await self.wait_for_reaction(["✅", "❌"], temp_message)
                if not self.run:
                    break
                if reaction.emoji == "✅":
                    account_details = get_account_details(self.context.author.id)
                    payload = "{\"items\":[{\"media_type\":\""+self.results[index].media_type+"\",\"media_id\":"+str(self.results[index].id)+",\"comment\": \"S:"+season+" E:"+episode+"\"}]}"
                    LISTS.add_items(account_details[2], account_details[0], payload)
                    if self.results[index].media_type == "tv":
                        LISTS.update_items(account_details[2], account_details[0], payload)
                await temp_message.delete()
                break

    async def remove_watchlist(self, index):
        if index <= len(self.results):
            if self.results[index].media_type == "movie":
                embed = discord.Embed(title=f'Are you sure you want to remove {self.results[index].title} from your watched list?')
                temp_message = await self.context.send(embed=embed)
            elif self.results[index].media_type == "tv":
                embed = discord.Embed(title=f'Are you sure you want to remove {self.results[index].name} from your watched list?')
                temp_message = await self.context.send(embed=embed)
            await self.add_reactions(["✅", "❌"], temp_message)
            while self.run:
                reaction, user = await self.wait_for_reaction(["✅", "❌"], temp_message)
                if not self.run:
                    break
                if reaction.emoji == "✅":
                    account_details = get_account_details(self.context.author.id)
                    payload = "{\"items\":[{\"media_type\":\""+self.results[index].media_type+"\",\"media_id\":"+str(self.results[index].id)+"}]}"
                    LISTS.remove_items(account_details[2], account_details[0], payload)
                await temp_message.delete()
                break
