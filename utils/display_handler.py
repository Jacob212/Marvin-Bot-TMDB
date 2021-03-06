import datetime
import asyncio
import discord
from utils.sql import get_account_details, get_show, add_show, add_sub, get_sub, remove_sub
from utils.file_handler import find_exact
from fulltmdb import search, movies, tv, discover
from fulltmdb.v4 import lists

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

def _embed_format(detail, media, color):
    try:
        detail[globals()[media][0][2]]
        url = f'https://www.imdb.com/{globals()[media][0][0]}/{detail[globals()[media][0][2]]}'
    except TypeError:
        url = None
    embed = discord.Embed(title=detail[globals()[media][0][0]],
        description=f'{detail [globals()[media][0][1]]}',
        url=url,
        color=color)
    for attr, name, inline, fmt in globals()[media][1:]:
        try:
            value = detail[attr]
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
            value = detail["backdrop_path"]
        except AttributeError:
            pass
        else:
            embed.set_image(url=f'https://image.tmdb.org/t/p/original{value}')
    return embed

class _base():
    def __init__(self, client, context, options, page):
        self.client = client
        self.context = context
        self.options = options
        self.results = None
        self.bots_message = None
        self.run = True
        self.page = page

    async def main(self):
        while self.run:
            embed = self._api_call()
            embed = self._finish_embed(embed, self.options["media"])
            await self._send_message(embed)
            response = await self._get_response(["◀", "▶"])
            if self.run:
                await self._handle_response(response)

    async def _get_response(self, reactions):
        try:
            return await self.client.wait_for("reaction_add", timeout=6, check=lambda r, u: r.emoji in reactions and u.id == self.context.message.author.id and r.message.id == self.bots_message.id)
        except asyncio.TimeoutError:
            self.run = False
            return None

    async def _add_reactions(self, reactions, message):
        for reaction in reactions:
            await message.add_reaction(reaction)

    async def _remove_reactions(self, reactions, message, author):
        for reaction in reactions:
            await message.remove_reaction(reaction, author)

    def _finish_embed(self, embed, media_type):
        if self.result['results'] == []:
            message = self.empty_message
        else:
            message = self._create_list(media_type)
        embed.add_field(name=f'Page: {self.result["page"]}/{self.result["total_pages"]}   Total results: {self.result["total_results"]}', value=message)
        return embed

    def _create_list(self, media_type):
        message = ""
        for result in self.result['results']:
            if media_type is None:
                message += f'**{self.result["results"].index(result)+1} - {result["media_type"].title()}**: {result[globals()[result["media_type"]][0][0]]}\n'
            else:
                message += f'**{self.result["results"].index(result)+1} - {media_type.title()}**: {result[globals()[media_type][0][0]]}\n'
        return message

    async def _send_message(self, embed):
        if self.bots_message is None:
            self.bots_message = await self.context.send(embed=embed)
        else:
            await self.bots_message.edit(embed=embed)
        await self._add_reactions(["◀", "▶"], self.bots_message)

    async def _handle_response(self, response):
        reaction = response[0]
        if reaction.emoji == "▶" and len(self.result['results']) == 20:
            self.page += 1
        elif reaction.emoji == "◀" and self.page != 1:
            self.page -= 1
        await self._remove_reactions(["◀", "▶"], self.bots_message, self.context.message.author)

class _details(_base):
    async def _handle_response(self, response):
        if isinstance(response, tuple):
            reaction = response[0]
            if reaction.emoji == "▶" and len(self.result['results']) == 20:
                self.page += 1
            elif reaction.emoji == "◀" and self.page != 1:
                self.page -= 1
            await self._remove_reactions(["◀", "▶"], self.bots_message, self.context.message.author)
        else:
            await response.delete()
            await self._details(int(response.content)-1)

    async def _get_response(self, reactions):
        try:
            done, pending = await asyncio.wait([
                self.client.wait_for("message", timeout=600, check=lambda m: m.channel == self.context.channel and m.content.isdigit() and m.author.id == self.context.message.author.id),
                self.client.wait_for("reaction_add", timeout=600, check=lambda r, u: r.emoji in reactions and u.id == self.context.message.author.id and r.message.id == self.bots_message.id)
                ], return_when=asyncio.FIRST_COMPLETED)
        except asyncio.TimeoutError:
            self.run = False
            return None
        else:
            for future in pending:
                future.cancel()
            return done.pop().result()

    async def _wait_for_reaction(self, reactions, message):
        try:
            return await self.client.wait_for("reaction_add", timeout=6, check=lambda r, u: r.emoji in reactions and u.id == self.context.message.author.id and r.message.id == message.id)
        except asyncio.TimeoutError:
            self.run = False
            return None, None

    async def _details(self, index):
        if index <= len(self.result['results']):
            try:
                media = self.result['results'][index]['media_type']
            except KeyError:
                media = self.options["media"]
            if media == "movie":
                detail = movies.details(self.result['results'][index]['id'])
                embed = _embed_format(detail, "movie", self.context.message.author.color.value)
                reactions = ["◀", "⏬", "❌"]
            elif media == "tv":
                detail = TV.details(self.result['results'][index]['id'])
                embed = _embed_format(detail, "tv", self.context.message.author.color.value)
                reactions = ["◀", "⏬", "❌", "🔔"]
        else:
            embed = discord.Embed(title="That is not an option", description="Please go back", color=discord.Colour.dark_red())
        await self.bots_message.edit(embed=embed)
        await self.bots_message.remove_reaction("▶", self.client.user)
        await self._add_reactions(reactions[1:], self.bots_message)
        while self.run:
            reaction, _ = await self._wait_for_reaction(reactions, self.bots_message)
            if not self.run:
                break
            if reaction.emoji == "◀":
                await self._remove_reactions(["⏬", "❌", "🔔"], self.bots_message, self.client.user)
                await self.bots_message.remove_reaction("◀", self.context.message.author)
                break
            elif reaction.emoji == "⏬":
                await self.bots_message.remove_reaction("⏬", self.context.message.author)
                await self._add_watchlist(index, media)
            elif reaction.emoji == "❌":
                await self.bots_message.remove_reaction("❌", self.context.message.author)
                await self._remove_watchlist(index, media)
            elif reaction.emoji == "🔔" and media == "tv":
                await self.bots_message.remove_reaction("🔔", self.context.message.author)
                await self._sub(index)

    async def _add_watchlist(self, index, media):
        if index <= len(self.result['results']):
            if media == "movie":
                season = ""
                episode = ""
                embed = discord.Embed(title=f'Are you sure you want to add {self.result["results"][index]["title"]} to your watched list?')
                temp_message = await self.context.send(embed=embed)
            elif media == "tv":
                embed = discord.Embed(title=f'What season of {self.result["results"][index]["name"]} have you watched up too?')
                temp_message = await self.context.send(embed=embed)
                response = await self.client.wait_for('message', check=lambda m: m.channel == self.context.channel and m.content.isdigit())
                season = response.content
                await response.delete()
                embed = discord.Embed(title=f'What episode of {self.result["results"][index]["name"]} season {season} have you watched up too?')
                await temp_message.edit(embed=embed)
                response = await self.client.wait_for('message', check=lambda m: m.channel == self.context.channel and m.content.isdigit())
                episode = response.content
                await response.delete()
                embed = discord.Embed(title=f'Are you sure you want to add {self.result["results"][index]["name"]} - {season} - {episode} to your watched list')
                await temp_message.edit(embed=embed)
            await self._add_reactions(["✅", "❌"], temp_message)
            while self.run:
                reaction, _ = await self._wait_for_reaction(["✅", "❌"], temp_message)
                if not self.run:
                    break
                if reaction.emoji == "✅":
                    account_details = get_account_details(self.context.author.id)
                    payload = "{\"items\":[{\"media_type\":\""+media+"\",\"media_id\":"+str(self.result['results'][index]['id'])+",\"comment\": \"S:"+season+" E:"+episode+"\"}]}"
                    Lists.add_items(account_details[2], account_details[0], payload)
                    if media == "tv":
                        Lists.update_items(account_details[2], account_details[0], payload)
                await temp_message.delete()
                break

    async def _remove_watchlist(self, index, media):
        if index <= len(self.results):
            if media == "movie":
                embed = discord.Embed(title=f'Are you sure you want to remove {self.result["results"][index]["title"]} from your watched list?')
                temp_message = await self.context.send(embed=embed)
            elif media == "tv":
                embed = discord.Embed(title=f'Are you sure you want to remove {self.result["results"][index]["name"]} from your watched list?')
                temp_message = await self.context.send(embed=embed)
            await self._add_reactions(["✅", "❌"], temp_message)
            while self.run:
                reaction, _ = await self._wait_for_reaction(["✅", "❌"], temp_message)
                if not self.run:
                    break
                if reaction.emoji == "✅":
                    account_details = get_account_details(self.context.author.id)
                    payload = "{\"items\":[{\"media_type\":\""+media+"\",\"media_id\":"+str(self.results[index].id)+"}]}"
                    lists.remove_items(account_details[0], account_details[2], payload)
                await temp_message.delete()
                break

    async def _sub(self, index):
        embed = discord.Embed(title=f'Are you sure you want to turn on notifications for {self.result["results"][index]["name"]}')
        temp_message = await self.context.send(embed=embed)
        await self._add_reactions(["✅", "❌"], temp_message)
        while self.run:
            reaction, _ = await self._wait_for_reaction(["✅", "❌"], temp_message)
            if not self.run:
                break
            show = get_show(self.result["results"][index]['id'])
            sub = get_sub(self.context.author.id, self.result["results"][index]['id'])
            if reaction.emoji == "✅":
                if show is None:
                    add_show(self.results[index].name, self.result["results"][index]['id'])
                if sub is None:
                    add_sub(self.context.author.id, self.result["results"][index]['id'])
            elif reaction.emoji == "❌":
                if sub is not None:
                    remove_sub(self.context.author.id, self.result["results"][index]['id'])
            await temp_message.delete()
            break

class SearchPages(_details):
    def __init__(self, client, context, options, page):
        super().__init__(client, context, options, page)
        self.empty_message = "Nothing could be found for this search."

    def _api_call(self):
        if self.options["media"] == "movie":
            embed = discord.Embed(title="Search results for:", description=self.options["query"])
            self.result = search.movie(query=self.options["query"], page=self.page)
        elif self.options["media"] == "tv":
            embed = discord.Embed(title="Search results for:", description=self.options["query"])
            self.result = search.tv(query=self.options["query"], page=self.page)
        else:
            embed = discord.Embed(title="Search results for:", description=self.options["query"])
            self.result = search.multi(query=self.options["query"], page=self.page)
        return embed

class WatchedPages(_details):
    def __init__(self, client, context, options, page):
        super().__init__(client, context, options, page)
        self.empty_message = "This user has not added anything to their watched list."

    def _api_call(self):
        embed = discord.Embed(title="Watched list of:", description=self.options["mention"])
        self.result = lists.get(self.options["listID"], sort_by=self.options["latest"], page=self.page)
        return embed

class _discover(_details):
    def __init__(self, client, context, options, page):
        super().__init__(client, context, options, page)
        self.empty_message = "Nothing could be found with these filters"
        self.query_string = {}
        self.description_string = {"include":[], "exclude":[]}

    async def before_main(self):
        self._sort_matches(self.options["matches"])
        self._year(self.options["year"])
        await self.main()

    def _year(self, year):
        if year is not None:
            self.query_string["primary_release_year"] = year.group().strip("-")
            self.description_string["year"] = [year.group().strip("-")]

    def _sort_matches(self, matches):
        for _, match in enumerate(matches, start=1):
            match_string = match.group().lower()
            result = find_exact("data", f'{self.options["media"]}_genre_ids', match_string.strip().strip("+-"))
            if result is not None:
                self._query_string_setup("genres", match_string, result)
            else:
                result = find_exact("data", "keyword_ids", match_string.strip().strip("+-"))
                if result is not None:
                    self._query_string_setup("keywords", match_string, result)

    def _query_string_setup(self, query_type, match_string, result):
        if "+" in match_string:
            if "with_"+query_type in self.query_string:
                self.query_string["with_"+query_type] = f'{self.query_string["with_"+query_type]},{result["id"]}'
            else:
                self.query_string["with_"+query_type] = result["id"]
            self.description_string["include"].append(result["name"])
        elif "-" in match_string:
            if "without_"+query_type in self.query_string:
                self.query_string["without_"+query_type] = f'{self.query_string["without_"+query_type]},{result["id"]}'
            else:
                self.query_string["without_"+query_type] = result["id"]
            self.description_string["exclude"].append(result["name"])

    def _description(self):
        string = ""
        for value, key in self.description_string.items():
            string += f'{value}: {", ".join(key).lower()}\n'
        return string

class DiscoverMoviesPages(_discover):
    def _api_call(self):
        embed = discord.Embed(title="Movies filtered by:", description=self._description())
        print(self.query_string)
        self.result = discover.movie(query=self.query_string, page=self.page)
        return embed

class DiscoverTVPages(_discover):
    def _api_call(self):
        embed = discord.Embed(title="TV shows filtered by:", description=self._description())
        self.result = discover.tv(query=self.query_string, page=self.page)
        return embed

class AiringTVPages(_details):
    def __init__(self, client, context, options, page):
        super().__init__(client, context, options, page)
        self.empty_message = "Nothing airing soon."

    def _api_call(self):
        embed = discord.Embed(title="TV shows airing todat:")
        self.result = tv.airing_today(page=self.page)
        return embed

class KeywordPages(_base):
    def __init__(self, client, context, options, page):
        super().__init__(client, context, options, page)
        self.empty_message = "The keyword you are looking for doesnt exist."
        self.options["media"] = None

    def _api_call(self):
        embed = discord.Embed(title="Keywords related to:", description=self.options["query"])
        self.result = search.keywords(query=self.options["query"], page=self.page)
        return embed

    def _create_list(self, media_type):
        message = ""
        for item in self.result['results']:
            message += f'**{self.result["results"].index(result)+1}**: - {item["name"]}\n'
        return message
