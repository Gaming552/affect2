# This Bot Is Owned By Andrei Lord#0001 #
# All credits receive to sent, vlaz #
# Use Luma https://discord.gg/luma #

import discord, button_paginator as pg, json, aiohttp, userhandler, lastfmhandler
from discord.ext import commands  
from cogs.events import blacklist, sendmsg
from utility import Emotes, Colours

def Sort_Tuple(tup):
    return(reversed(sorted(tup, key = lambda x: x[1])))

class lastfm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
      try:  
       if not message.guild: return 
       if message.author.bot: return 
       async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM lastfmcc WHERE user_id = {}".format(message.author.id))
        check = await cursor.fetchone()
        if check is not None:
          if check[1] == message.content:
            member = message.author 
            async with message.channel.typing():
              await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
              res = await cursor.fetchone()
              if res is not None:   
                 user = str(res[1]).replace("('", "").replace("',)", "")
                 if user != "error":   
                    a = await lastfmhandler.get_tracks_recent(user, 1)
                    artist = a['recenttracks']['track'][0]['artist']['#text'].replace(" ", "+")
                    album = a['recenttracks']['track'][0]['album']['#text'] or "N/A"
                    embed = discord.Embed(colour=Colours.standard)
                    embed.add_field(name="**Track:**", value = f"""[{"" + a['recenttracks']['track'][0]['name']}]({"" + a['recenttracks']['track'][0]['url']})""", inline = False)
                    embed.add_field(name="**Artist:**", value = f"""[{a['recenttracks']['track'][0]['artist']['#text']}](https://last.fm/music/{artist})""", inline = False)
                    embed.set_author(name = user, icon_url = member.display_avatar, url = f"https://last.fm/user/{user}")                               
                    embed.set_thumbnail(url=(a['recenttracks']['track'][0])['image'][3]['#text'])
                    embed.set_footer(text = f"Track Playcount: {await lastfmhandler.get_track_playcount(user, a['recenttracks']['track'][0])} ・Album: {album}", icon_url = (a['recenttracks']['track'][0])['image'][3]['#text'])
                    await sendmsg(self, message, None, embed, None, None, None, None)
              elif check is None: 
                embed = discord.Embed(description=f"> {Emotes.lastfm} {message.author.mention}: **{member}** doesn't have a **Last.fm account** linked. Use `;lastfm set <username>` to link your **account**.", color=Colours.standard)
                await sendmsg(self, message, None, embed, None, None, None, None)  
      except Exception as e:
          embed = discord.Embed(description=f"> {Emotes.warning} {message.author.mention}: unable to get **{member.name}'s** recent track - {e}", color=Colours.standard)
          await sendmsg(self, message, None, embed, None, None, None, None)  

    @commands.group(aliases = ['lf'])
    @blacklist()
    async def lastfm(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = f"**How do I set my Last.fm username?**\n1. Go on **[Last.fm](https://last.fm)** & create an account if you don't already have one\n2. Run the command `;lastfm set <usernmae>`",color = Colours.standard)
            embed.add_field(name="category", value="config")
            embed.add_field(name="Arguments", value="<subcommand> [string]")
            embed.add_field(name="Command Usage",value="```Syntax: ;lastfm set\nSyntax: ;lastfm remove\nSyntax: ;lastfm customcommand\nSyntax: ;topartists\nSyntax: ;toptracks\nSyntax: ;topalbums\nSyntax: ;whoknows [artist]\nSyntax: ;globalwhoknows [artist]\nSyntax: ;nowplaying```", inline=False)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            return

    @lastfm.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def set(self, ctx, ref=None):
            if ref is None: 
                e = discord.Embed(title="Command: lastfm set", description="register your lastfm account",color=Colours.standard, timestamp=ctx.message.created_at)
                e.add_field(name="category", value="config")
                e.add_field(name="Arguments", value="[name]")
                e.add_field(name="Command Usage",value="```Syntax: ;lastfm set andreilord```", inline=False)
                await sendmsg(self, ctx, None, e, None, None, None, None)
                return

            ref = ref.replace("https://www.last.fm/user/", "")
            if not await userhandler.lastfm_user_exists(ref):
                embed = discord.Embed(description=f'> {Emotes.warning} {ctx.author.mention}: **Invalid** Last.fm username',
                                    color=Colours.standard)
                return await sendmsg(self, ctx, None, embed, None, None, None, None)
            else:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(ctx.author.id))
                    check = await cursor.fetchone()
                    if check is None:
                        await cursor.execute("INSERT INTO lastfm VALUES (?, ?)", (ctx.author.id, ref))
                    elif check is not None:
                        await cursor.execute("UPDATE lastfm SET username = ? WHERE user_id = ?", (ref, ctx.author.id))
                    embed = discord.Embed(description=f'> {Emotes.warning} {ctx.message.author.mention}: Your **Last.fm** username has been set to **{ref}**', color=Colours.standard)
                    await sendmsg(self, ctx, None, embed, None, None, None, None)
                await self.bot.db.commit()  

    @lastfm.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def remove(self, ctx): 
     async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(ctx.author.id))
        check = await cursor.fetchone()
        if check is None: return await sendmsg(self, ctx, None, discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: You don't have a **Last.fm account** linked. Use `;lastfm set <username>` to link your **account**.", color=Colours.standard), None, None, None, None)             
        await cursor.execute("DELETE FROM lastfm WHERE user_id = {}".format(ctx.author.id))
        await self.bot.db.commit()
        await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: your last fm account has been removed"), None, None, None, None)

    @lastfm.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def customcommand(self, ctx, *, cmd=None):
        if cmd is None:
            e = discord.Embed(title="Command: lastfm customcommand", description="set a custom command for nowplaying",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="[command]")
            e.add_field(name="Command Usage",value="```Syntax: ;lastfm customcommand play123```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        if cmd == "none":   
             async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM lastfmcc WHERE user_id = {}".format(ctx.author.id))
                    check = await cursor.fetchone()
                    if check is None:
                        return await sendmsg(self, ctx, "you don't have a lastfm command", None, None, None, None, None)
                    elif check is not None:
                        await cursor.execute(f"DELETE FROM lastfmcc WHERE user_id = {ctx.author.id}")
                    embed = discord.Embed(description=f'> {Emotes.approve} {ctx.author.mention}: Your **Last.fm** custom command got deleted', color=Colours.standard)
                    await sendmsg(self, ctx, None, embed, None, None, None, None)   
                    await self.bot.db.commit()  
                    return          
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM lastfmcc WHERE user_id = {}".format(ctx.author.id))
                    check = await cursor.fetchone()
                    if check is None:
                        await cursor.execute("INSERT INTO lastfmcc VALUES (?, ?)", (ctx.author.id, cmd))
                    elif check is not None:
                        await cursor.execute("UPDATE lastfmcc SET command = ? WHERE user_id = ?", (cmd, ctx.author.id))
                    embed = discord.Embed(description=f'> {Emotes.lastfm} {ctx.message.author.mention}: Your **Last.fm** custom command is {cmd}', color=Colours.standard)
                    await sendmsg(self, ctx, None, embed, None, None, None, None)   
                    await self.bot.db.commit()  

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def topartists(self, ctx, member: discord.Member = None):
        try:
           if member == None:
                member = ctx.author
           async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT user FROM nodata WHERE user = ?", (member.id,))
            data = await cursor.fetchone()
            embed = discord.Embed(description=f'> {Emotes.warning} {ctx.message.author.mention}: This member opted out of their data being tracked', color=Colours.standard)
            if data: return await sendmsg(self, None, embed, None, None, None, None, None)
            await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
            check = await cursor.fetchone()
            if check is not None:   
                user = str(check[1]).replace("('", "").replace("',)", "")
                if user != "error": 
                 async with aiohttp.ClientSession() as session:
                    params= {"api_key" : "f3042dd6ed60412788835b2ac5334503",
                    "user" : user,
                    "period" : "overall",
                    "limit" : 10,
                    "method":"user.getTopArtists",
                    "format":"json"}
                    async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
                        resp = await response.read()
                        jsonData = json.loads(resp)
                        topartist1 = jsonData["topartists"]["artist"][0]["name"]
                        topartist2 = jsonData["topartists"]["artist"][1]["name"]
                        topartist3 = jsonData["topartists"]["artist"][2]["name"]
                        topartist4 = jsonData["topartists"]["artist"][3]["name"]
                        topartist5 = jsonData["topartists"]["artist"][4]["name"]
                        topartist6 = jsonData["topartists"]["artist"][5]["name"]
                        topartist7 = jsonData["topartists"]["artist"][6]["name"]
                        topartist8 = jsonData["topartists"]["artist"][7]["name"]
                        topartist9 = jsonData["topartists"]["artist"][8]["name"]
                        topartist10 = jsonData["topartists"]["artist"][9]["name"]
                        topartist1url = jsonData["topartists"]["artist"][0]["url"]
                        topartist2url = jsonData["topartists"]["artist"][1]["url"]
                        topartist3url = jsonData["topartists"]["artist"][2]["url"]
                        topartist4url = jsonData["topartists"]["artist"][3]["url"]
                        topartist5url = jsonData["topartists"]["artist"][4]["url"]
                        topartist6url = jsonData["topartists"]["artist"][5]["url"]
                        topartist7url = jsonData["topartists"]["artist"][6]["url"]
                        topartist8url = jsonData["topartists"]["artist"][7]["url"]
                        topartist9url = jsonData["topartists"]["artist"][8]["url"]
                        topartist10url = jsonData["topartists"]["artist"][9]["url"]
                        topartist1plays = jsonData["topartists"]["artist"][0]["playcount"]
                        topartist2plays = jsonData["topartists"]["artist"][1]["playcount"]
                        topartist3plays = jsonData["topartists"]["artist"][2]["playcount"]
                        topartist4plays = jsonData["topartists"]["artist"][3]["playcount"]
                        topartist5plays = jsonData["topartists"]["artist"][4]["playcount"]
                        topartist6plays = jsonData["topartists"]["artist"][5]["playcount"]
                        topartist7plays = jsonData["topartists"]["artist"][6]["playcount"]
                        topartist8plays = jsonData["topartists"]["artist"][7]["playcount"]
                        topartist9plays = jsonData["topartists"]["artist"][8]["playcount"]
                        topartist10plays = jsonData["topartists"]["artist"][9]["playcount"]
                        embed = discord.Embed(description = f"""`1` **[{topartist1}]({topartist1url})** {topartist1plays} plays
`2` **[{topartist2}]({topartist2url})** {topartist2plays} plays
`3` **[{topartist3}]({topartist3url})** {topartist3plays} plays
`4` **[{topartist4}]({topartist4url})** {topartist4plays} plays
`5` **[{topartist5}]({topartist5url})** {topartist5plays} plays
`6` **[{topartist6}]({topartist6url})** {topartist6plays} plays
`7` **[{topartist7}]({topartist7url})** {topartist7plays} plays
`8`	**[{topartist8}]({topartist8url})** {topartist8plays} plays
`9` **[{topartist9}]({topartist9url})** {topartist9plays} plays
`10` **[{topartist10}]({topartist10url})** {topartist10plays} plays""",color = Colours.standard)
                        embed.set_thumbnail(url = member.display_avatar)
                        embed.set_author(name = f"{user}'s overall top artists", icon_url = member.display_avatar)
                        await sendmsg(self, ctx, None, embed, None, None, None, None)   
            else:
                embed = discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: You don't have a **Last.fm account** linked. Use `;lastfm set <username>` to link your **account**.",color=Colours.standard)
                await sendmsg(self, ctx, None, embed, None, None, None, None)   
        except Exception as e:
            print(e)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def toptracks(self, ctx, *, member: discord.Member=None):
        if member == None:
            member=ctx.author
        try:
           async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT user FROM nodata WHERE user = ?", (member.id,))
            data = await cursor.fetchone()
            embed = discord.Embed(description=f'> {Emotes.warning} {ctx.message.author.mention}: This member opted out of their data being tracked', color=Colours.standard)
            if data: return await sendmsg(self, None, embed, None, None, None, None, None)
            await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
            check = await cursor.fetchone()
            if check is not None:   
                user = str(check[1]).replace("('", "").replace("',)", "")
                if user != "error": 
                 async with aiohttp.ClientSession() as session:
                    params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7",
                    "user" : user,
                    "period" : "overall",
                    "limit" : 10,
                    "method":"user.getTopTracks",
                    "format":"json"}
                    async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
                        resp = await response.read()
                        jsonData = json.loads(resp)
                        toptrack1 = jsonData["toptracks"]["track"][0]["name"]
                        toptrack2 = jsonData["toptracks"]["track"][1]["name"]
                        toptrack3 = jsonData["toptracks"]["track"][2]["name"]
                        toptrack4 = jsonData["toptracks"]["track"][3]["name"]
                        toptrack5 = jsonData["toptracks"]["track"][4]["name"]
                        toptrack6 = jsonData["toptracks"]["track"][5]["name"]
                        toptrack7 = jsonData["toptracks"]["track"][6]["name"]
                        toptrack8 = jsonData["toptracks"]["track"][7]["name"]
                        toptrack9 = jsonData["toptracks"]["track"][8]["name"]
                        toptrack10 = jsonData["toptracks"]["track"][9]["name"]
                        toptrack1url = jsonData["toptracks"]["track"][0]["url"]
                        toptrack2url = jsonData["toptracks"]["track"][1]["url"]
                        toptrack3url = jsonData["toptracks"]["track"][2]["url"]
                        toptrack4url = jsonData["toptracks"]["track"][3]["url"]
                        toptrack5url = jsonData["toptracks"]["track"][4]["url"]
                        toptrack6url = jsonData["toptracks"]["track"][5]["url"]
                        toptrack7url = jsonData["toptracks"]["track"][6]["url"]
                        toptrack8url = jsonData["toptracks"]["track"][7]["url"]
                        toptrack9url = jsonData["toptracks"]["track"][8]["url"]
                        toptrack10url = jsonData["toptracks"]["track"][9]["url"]
                        toptrack1plays = jsonData["toptracks"]["track"][0]["playcount"]
                        toptrack2plays = jsonData["toptracks"]["track"][1]["playcount"]
                        toptrack3plays = jsonData["toptracks"]["track"][2]["playcount"]
                        toptrack4plays = jsonData["toptracks"]["track"][3]["playcount"]
                        toptrack5plays = jsonData["toptracks"]["track"][4]["playcount"]
                        toptrack6plays = jsonData["toptracks"]["track"][5]["playcount"]
                        toptrack7plays = jsonData["toptracks"]["track"][6]["playcount"]
                        toptrack8plays = jsonData["toptracks"]["track"][7]["playcount"]
                        toptrack9plays = jsonData["toptracks"]["track"][8]["playcount"]
                        toptrack10plays = jsonData["toptracks"]["track"][9]["playcount"]
                        embed = discord.Embed(description = f"""`1` **[{toptrack1}]({toptrack1url})** {toptrack1plays} plays
`2` **[{toptrack2}]({toptrack2url})** {toptrack2plays} plays
`3` **[{toptrack3}]({toptrack3url})** {toptrack3plays} plays
`4` **[{toptrack4}]({toptrack4url})** {toptrack4plays} plays
`5` **[{toptrack5}]({toptrack5url})** {toptrack5plays} plays
`6` **[{toptrack6}]({toptrack6url})** {toptrack6plays} plays
`7` **[{toptrack7}]({toptrack7url})** {toptrack7plays} plays
`8`	**[{toptrack8}]({toptrack8url})** {toptrack8plays} plays
`9` **[{toptrack9}]({toptrack9url})** {toptrack9plays} plays
`10` **[{toptrack10}]({toptrack10url})** {toptrack10plays} plays""",color = Colours.standard)
                        embed.set_thumbnail(url = ctx.message.author.avatar)
                        embed.set_author(name = f"{user}'s overall top tracks", icon_url = ctx.message.author.avatar)
                        await sendmsg(self, ctx, None, embed, None, None, None, None)   
            else:
                embed = discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: You don't have a **Last.fm account** linked. Use `;lastfm set <username>` to link your **account**.",color=Colours.standard)
                await sendmsg(self, ctx, None, embed, None, None, None, None)   
        except Exception as e:
            print(e)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def topalbums(self,ctx, *, member: discord.Member=None):
        if member == None: member=ctx.author
        try:
           async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT user FROM nodata WHERE user = ?", (member.id,))
            data = await cursor.fetchone()
            embed = discord.Embed(description=f'> {Emotes.warning} {ctx.message.author.mention}: This member opted out of their data being tracked', color=Colours.standard)
            if data: return await sendmsg(self, None, embed, None, None, None, None, None)
            await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
            check = await cursor.fetchone()
            if check is not None:   
                user = str(check[1]).replace("('", "").replace("',)", "")
                if user != "error": 
                 async with aiohttp.ClientSession() as session:
                    params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7",
                    "user" : user,
                    "period" : "overall",
                    "limit" : 10,
                    "method":"user.getTopAlbums",
                    "format":"json"}
                    async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
                        resp = await response.read()
                        jsonData = json.loads(resp)
                        topalbum1 = jsonData["topalbums"]["album"][0]["name"]
                        topalbum2 = jsonData["topalbums"]["album"][1]["name"]
                        topalbum3 = jsonData["topalbums"]["album"][2]["name"]
                        topalbum4 = jsonData["topalbums"]["album"][3]["name"]
                        topalbum5 = jsonData["topalbums"]["album"][4]["name"]
                        topalbum6 = jsonData["topalbums"]["album"][5]["name"]
                        topalbum7 = jsonData["topalbums"]["album"][6]["name"]
                        topalbum8 = jsonData["topalbums"]["album"][7]["name"]
                        topalbum9 = jsonData["topalbums"]["album"][8]["name"]
                        topalbum10 = jsonData["topalbums"]["album"][9]["name"]
                        topalbum1url = jsonData["topalbums"]["album"][0]["url"]
                        topalbum2url = jsonData["topalbums"]["album"][1]["url"]
                        topalbum3url = jsonData["topalbums"]["album"][2]["url"]
                        topalbum4url = jsonData["topalbums"]["album"][3]["url"]
                        topalbum5url = jsonData["topalbums"]["album"][4]["url"]
                        topalbum6url = jsonData["topalbums"]["album"][5]["url"]
                        topalbum7url = jsonData["topalbums"]["album"][6]["url"]
                        topalbum8url = jsonData["topalbums"]["album"][7]["url"]
                        topalbum9url = jsonData["topalbums"]["album"][8]["url"]
                        topalbum10url = jsonData["topalbums"]["album"][9]["url"]
                        topalbum1plays = jsonData["topalbums"]["album"][0]["playcount"]
                        topalbum2plays = jsonData["topalbums"]["album"][1]["playcount"]
                        topalbum3plays = jsonData["topalbums"]["album"][2]["playcount"]
                        topalbum4plays = jsonData["topalbums"]["album"][3]["playcount"]
                        topalbum5plays = jsonData["topalbums"]["album"][4]["playcount"]
                        topalbum6plays = jsonData["topalbums"]["album"][5]["playcount"]
                        topalbum7plays = jsonData["topalbums"]["album"][6]["playcount"]
                        topalbum8plays = jsonData["topalbums"]["album"][7]["playcount"]
                        topalbum9plays = jsonData["topalbums"]["album"][8]["playcount"]
                        topalbum10plays = jsonData["topalbums"]["album"][9]["playcount"]
                        embed = discord.Embed(description = f"""`1` **[{topalbum1}]({topalbum1url})** {topalbum1plays} plays
`2` **[{topalbum2}]({topalbum2url})** {topalbum2plays} plays
`3` **[{topalbum3}]({topalbum3url})** {topalbum3plays} plays
`4` **[{topalbum4}]({topalbum4url})** {topalbum4plays} plays
`5` **[{topalbum5}]({topalbum5url})** {topalbum5plays} plays
`6` **[{topalbum6}]({topalbum6url})** {topalbum6plays} plays
`7` **[{topalbum7}]({topalbum7url})** {topalbum7plays} plays
`8`	**[{topalbum8}]({topalbum8url})** {topalbum8plays} plays
`9` **[{topalbum9}]({topalbum9url})** {topalbum9plays} plays
`10` **[{topalbum10}]({topalbum10url})** {topalbum10plays} plays""",color = Colours.standard)
                        embed.set_thumbnail(url = ctx.message.author.avatar)
                        embed.set_author(name = f"{user}'s overall top albums", icon_url = ctx.message.author.avatar)
                        await sendmsg(self, ctx, None, embed, None, None, None, None)   
            else:
                embed = discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: You don't have a **Last.fm account** linked. Use `;lastfm set <username>` to link your **account**.",color=Colours.standard)
                await sendmsg(self, ctx, None, embed, None, None, None, None)    
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_command(self, ctx): 
        destination = ("Private Message" if not ctx.guild else f"#{ctx.channel} ({ctx.guild})"),
        channel = self.bot.get_channel(956675897132478474)
        await channel.send(f"{ctx.author} in {destination}: **{ctx.message.content}**")

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def whoknows(self, ctx: commands.Context, * ,artist):
     try:   
      lis = []  
      async with ctx.typing():
       async with self.bot.db.cursor() as cursor:
        for user in ctx.guild.members: 
         await cursor.execute("SELECT user FROM nodata WHERE user = ?", (user.id,))
         data = await cursor.fetchone()
         if data: continue   
         await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(user.id))
         check = await cursor.fetchone()
         if check is not None: 
          use = await self.bot.fetch_user(user.id)   
          username = str(check[1]).replace("('", "").replace("',)", "")
          if username != "error": 
           async with aiohttp.ClientSession() as session:
            params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7", "user": username, "artist" : artist, "method": "artist.getInfo", "autocorrect": "true", "format":"json"}
            async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
             jsonData = await response.json()
             try:
              userplays = jsonData['artist']['stats']['userplaycount']
              if len(jsonData['artist']['stats']['userplaycount']) > 1: 
               lis.append(tuple((f"{use.name}#{use.discriminator}", int(userplays), username)))
              else:
               continue
             except KeyError: 
                continue           
         elif check is not None:
            continue 

       if lis == []:
         embed = discord.Embed(description=f"> {Emotes.lastfm} {ctx.author.mention}: Nobody (not even you) has listened to {artist}",color=Colours.standard)
         await sendmsg(self, ctx, None, embed, None, None, None, None) 
         return      
       list = Sort_Tuple(lis)
       listeners = ""
       listenerscount = 0
       num = 0
       number = []
       messages =[]
       i = 0
       for l in list:
        num += 1  
        listenerscount += 1
        if num == 1:
            listeners += f"{Emotes.crown} **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n"
        else:    
         listeners += f"`{num}` **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n" 
        if listenerscount == 10:
         messages.append(listeners)
         number.append(discord.Embed(color=Colours.standard, description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{len(lis   )} listeners for this artist"))
         i+=1
         listeners = ""
         listenerscount = 0 
       if num == 0:
         embed = discord.Embed(description=f"> {Emotes.lastfm} {ctx.author.mention}: Nobody (not even you) has listened to {artist}",color=Colours.standard)
         await sendmsg(self, ctx, None, embed, None, None, None, None) 
         return 
       messages.append(listeners)
       embe = discord.Embed(color=Colours.standard, description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{len(lis)} listeners for this artist")
       number.append(embe)
       if len(number) > 1:
        paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
        paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
        paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
        paginator.add_button('next', emoji="<:right:1018156484170883154>")
        await paginator.start()
       else: 
        await sendmsg(self, ctx, None, embe, None, None, None, None)    
     except Exception as e:
        embed = discord.Embed(description = f"> {Emotes.warning} {ctx.author.mention}: `{artist}` is not a **valid** artist", color = Colours.standard)
        await sendmsg(self, ctx, None, embed, None, None, None, None)   
        print(e) 
    
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def globalwhoknows(self, ctx: commands.Context, * ,artist):
     try:   
      lis = []  
      async with ctx.typing():
       async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM lastfm")
        results = await cursor.fetchall()
        for check in results:
         use = await self.bot.fetch_user(check[0])      
         await cursor.execute("SELECT user FROM nodata WHERE user = ?", (use.id,))
         data = await cursor.fetchone()
         if data: continue
         username = str(check[1]).replace("('", "").replace("',)", "")
         if username != "error": 
          async with aiohttp.ClientSession() as session:
           params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7", "user": username, "artist" : artist, "method": "artist.getInfo", "autocorrect": "true", "format":"json"}
           async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
            resp = await response.read()
            jsonData = json.loads(resp)
            try:
             userplays = jsonData['artist']['stats']['userplaycount']
             if len(jsonData['artist']['stats']['userplaycount']) > 1: 
              lis.append(tuple((f"{use.name}#{use.discriminator}", int(userplays), username)))
             else:
              continue
            except KeyError: 
                continue            

       if lis == []:
         embed = discord.Embed(description=f"> {Emotes.lastfm} {ctx.author.mention}: Nobody (not even you) has listened to {artist}",color=Colours.standard)
         await sendmsg(self, ctx, None, embed, None, None, None, None) 
         return 
       list = Sort_Tuple(lis) 
       listeners = ""
       listenerscount = 0
       num = 0
       number = []
       messages =[]
       i = 0
       for l in list:
        num += 1  
        listenerscount += 1
        if num == 1:
            listeners += f"{Emotes.crown} **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n"
        else:    
         listeners += f"`{num}` **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n" 
        if listenerscount == 10:
         messages.append(listeners)
         number.append(discord.Embed(color=Colours.standard, description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{len(lis)} listeners for this artist"))
         i+=1
         listeners = ""
         listenerscount = 0 
       if num == 0:
         embed = discord.Embed(description=f"> {Emotes.lastfm} {ctx.author.mention}: Nobody (not even you) has listened to {artist}",color=Colours.standard)
         await sendmsg(self, ctx, None, embed, None, None, None, None) 
         return 
       messages.append(listeners)
       embe = discord.Embed(color=Colours.standard, description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{len(lis)} listeners for this artist")
       number.append(embe)
       if len(number) > 1:
        paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
        paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
        paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
        paginator.add_button('next', emoji="<:right:1018156484170883154>")
        await paginator.start()
       else: 
        await sendmsg(self, ctx, None, embe, None, None, None, None)   
     except:
        embed = discord.Embed(description = f"> {Emotes.warning} {ctx.message.author.mention}: `{artist}` is not a **valid** artist", color = Colours.standard)
        await sendmsg(self, ctx, None, embed, None, None, None, None)   

    @commands.command(aliases=['np'])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def nowplaying(self, ctx: commands.Context, *, member: discord.User=None):
        if member is None:
            member = ctx.author
        try:
            async with ctx.typing():
             async with self.bot.db.cursor() as cursor:   
              await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
              check = await cursor.fetchone()
              if check is not None:   
                user = str(check[1]).replace("('", "").replace("',)", "")
                if user != "error":      
                    a = await lastfmhandler.get_tracks_recent(user, 1)
                    artist = a['recenttracks']['track'][0]['artist']['#text'].replace(" ", "+")
                    embed = discord.Embed(colour=Colours.standard)
                    embed.add_field(name="**Track:**", value = f"""[{"" + a['recenttracks']['track'][0]['name']}]({"" + a['recenttracks']['track'][0]['url']})""", inline = True)
                    embed.add_field(name="**Artist:**", value = f"""[{a['recenttracks']['track'][0]['artist']['#text']}](https://last.fm/music/{artist})""", inline = True)
                    embed.set_author(name = user, icon_url = member.display_avatar, url = f"https://last.fm/user/{user}")                               
                    embed.set_thumbnail(url=(a['recenttracks']['track'][0])['image'][3]['#text'])
                    embed.set_footer(text = f"Track Playcount: {await lastfmhandler.get_track_playcount(user, a['recenttracks']['track'][0])}・Album: {a['recenttracks']['track'][0]['album']['#text']}", icon_url = (a['recenttracks']['track'][0])['image'][3]['#text'])
                    message = await sendmsg(self, ctx, None, embed, None, None, None, None) 
              elif check is None: 
                embed = discord.Embed(description=f"> {Emotes.lastfm} {ctx.author.mention}: You don't have a **Last.fm account** linked. Use `;lastfm set <username>` to link your **account**.", color=Colours.standard)
                await sendmsg(self, ctx, None, embed, None, None, None, None) 
        except Exception as e:
          embed = discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: unable to get your recent track - {e}", color=Colours.standard)
          await sendmsg(self, ctx, None, embed, None, None, None, None) 
    
async def setup(bot) -> None:
    await bot.add_cog(lastfm(bot))           


# This Bot Is Owned By Andrei Lord#0001 #
# All credits receive to sent, vlaz #
# Use Luma https://discord.gg/luma #