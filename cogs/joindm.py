# This Bot Is Owned By Andrei Lord#0001 #
# All credits receive to sent, vlaz #
# Use Luma https://discord.gg/luma #

import discord
from discord.ext import commands
from utils.embedparser import EmbedBuilder
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist

class joindm(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        return 
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM joindm WHERE guild = {}".format(member.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                msg = check[1]
                user = member
                guild = member.guild
                channel = user.dm_channel or await user.create_dm()
                try: 
                  z = msg.replace('{user}', str(user)).replace('{user.name}', str(user.name)).replace('{user.mention}', str(user.mention)).replace('{user.avatar}', str(user.display_avatar.url)).replace('{user.joined_at}', f'<t:{int(user.created_at.timestamp())}:R>').replace('{user.discriminator}', str(user.discriminator)).replace('{guild.name}', str(guild.name)).replace('{guild.count}', str(guild.member_count)).replace('{guild.icon}', str(guild.icon)).replace('{guild.id}', str(guild.id))
                  x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, z))
                  await channel.send(content=x[0],embed=x[1], view=x[2])
                except: await channel.send(EmbedBuilder.embed_replacement(member, z))

  
    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def joindm(self, ctx):
        e = discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: this module will work after the bot is verified",color=Colours.standard)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return 
        e = discord.Embed(title="Command: joindm", description="greet your users into your guild with a direct message",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="config")
        e.add_field(name="Arguments", value="<subcommand> [message / channel]")
        e.add_field(name="permissions", value="manage_guild", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;joindm message\nSyntax: ;joindm config\nSyntax: ;joindm variables\nSyntax: ;joindm delete\nSyntax: ;joindm test```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)


    @joindm.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def message(self, ctx, *, code=None):
        return 
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        embed=discord.Embed(description=f"""> {Emotes.approve} {ctx.author.mention}: set joindm message: 
        ```{code}```""", color=Colours.standard)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM joindm WHERE guild = {}".format(ctx.guild.id))
            check = await cursor.fetchone()
            if check is None:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("INSERT INTO joindm (guild, message) VALUES (?, ?)", (ctx.guild.id, code))
                await self.bot.db.commit()
                await sendmsg(self, ctx, None, embed, None, None, None, None)
            elif check is not None:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("UPDATE joindm SET message = ? WHERE guild = ?", (code, ctx.guild.id))
                await self.bot.db.commit()
                await sendmsg(self, ctx, None, embed, None, None, None, None)


    @joindm.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def config(self, ctx):  
      return  
      if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild") 
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM joindm WHERE guild = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        msg = check[1] or "joindm message not set"
        embed = discord.Embed(color=Colours.standard)
        embed.add_field(name="message", value=f"```{msg}```")
        embed.set_author(name=f"joindm {ctx.guild.name}",icon_url=ctx.guild.icon)
        await sendmsg(self, ctx, None, embed, None, None, None, None)

    @joindm.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def variables(self, ctx):
        return    
        e = discord.Embed(title="Command: joindm variables", description="use the joindm variables for your joindm message/embed",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="config")
        e.add_field(name="user variables",value="```{user} - returns user full name\n{user.name} - returns user's username\n{user.mention} - mentions user\n{user.avatar} - return user's avatar\n{user.joined_at} returns the relative date the user joined the server\n{user.created_at} returns the relative time the user created the account\n{user.discriminator} - returns the user's discriminator\n{user.bot} - check if the user is a bot or not```", inline=False)
        e.add_field(name="guild variables",value="```{guild.name} - returns the server's name\n{guild.count} - returns the server's member count\n{guild.icon} - returns the server's icon\n{guild.id} - returns the server's id\n{guild.vanity} - returns the server's vanity, if any \n{guild.created_at} - returns the relative time the server was created\n{guild.boost_count} - returns the number of server's boosts\n{guild.booster_count} - returns the number of boosters\n{guild.boost_tier} - returns the server's boost level\n{guild.banner} - see the banner at the server\n{guild.splash} - see the splash at the server\n{guild.splash} - see the discovery at the server\n{guild.owner_mention} - you mention the server owner```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return

    @joindm.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def delete(self, ctx):  
      return 
      if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("DELETE FROM joindm WHERE guild = {}".format(ctx.guild.id))
      await self.bot.db.commit()
      embed=discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: deleted the joindm config for *{ctx.guild.name}*", color=Colours.standard)
      await sendmsg(self, ctx, None, embed, None, None, None, None)

    @joindm.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def test(self, ctx):  
        return  
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM joindm WHERE guild = {}".format(ctx.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                msg = check[1]
                user = ctx.author
                guild = ctx.guild
                channel = user.dm_channel or await user.create_dm()
                try: 
                  z = msg.replace('{user}', str(user)).replace('{user.name}', str(user.name)).replace('{user.mention}', str(user.mention)).replace('{user.avatar}', str(user.display_avatar.url)).replace('{user.joined_at}', f'<t:{int(user.created_at.timestamp())}:R>').replace('{user.discriminator}', str(user.discriminator)).replace('{guild.name}', str(guild.name)).replace('{guild.count}', str(guild.member_count)).replace('{guild.icon}', str(guild.icon)).replace('{guild.id}', str(guild.id))
                  x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, z))
                  await channel.send(content=x[0],embed=x[1], view=x[2])
                except: await channel.send(EmbedBuilder.embed_replacement(ctx.author, z))
                channel = user.dm_channel or await user.create_dm()
                embed=discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: joindm message has been sent in your direct messages", color=Colours.standard)
                await sendmsg(self, ctx, None, embed, None, None, None, None)
            elif check is None:
                embed=discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: joindm message isnt configured for *{ctx.guild.name}*", color=Colours.standard)
                await sendmsg(self, ctx, None, embed, None, None, None, None)

async def setup(bot) -> None:
    await bot.add_cog(joindm(bot))

# This Bot Is Owned By Andrei Lord#0001 #
# All credits receive to sent, vlaz #
# Use Luma https://discord.gg/luma #