# This Bot Is Owned By Andrei Lord#0001 #
# All credits receive to sent, vlaz #
# Use Luma https://discord.gg/luma #

import discord, json
from discord.ext import commands
from discord.ui import View, Button
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist

class jail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
     async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM setme WHERE guild_id = {}".format(channel.guild.id))
      chec = await cursor.fetchone()
      if chec is not None:  
        await channel.set_permissions(channel.guild.get_role(int(chec[1])), view_channel=False, reason="overwriting permissions for jail role")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member): 
     async with self.bot.db.cursor() as cursor:
       await cursor.execute("SELECT * FROM jail WHERE guild_id = {} AND user_id = {}".format(member.guild.id, member.id))
       check = await cursor.fetchone()
       if check is not None: 
         await cursor.execute("SELECT * FROM setme WHERE guild_id = {}".format(member.guild.id))
         chec = await cursor.fetchone()
         if chec is not None: 
          try:
           await member.add_roles(member.guild.get_role(int(chec[1])))   
          except:
            pass 

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def setjail(self, ctx: commands.Context):
     if not ctx.author.guild_permissions.administrator: return await noperms(self, ctx, "administrator")
     await ctx.message.channel.typing()
     async with self.bot.db.cursor() as cursor:
      await cursor.execute(f"SELECT * FROM setme WHERE guild_id = {ctx.guild.id}")  
      res = await cursor.fetchone()
      if res is not None: return await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Jail is already set"), None, None, None, None)
      role = await ctx.guild.create_role(name="affect jail", color=Colours.standard)
      for channel in ctx.guild.channels:
       await channel.set_permissions(role, view_channel=False, send_messages=False)
 
      overwrite = { role: discord.PermissionOverwrite(view_channel=True, send_messages=False), ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)}
      jail = await ctx.guild.create_text_channel(name="jail", category=None, overwrites=overwrite)
      await cursor.execute("INSERT INTO setme VALUES (?,?,?)", (jail.id, role.id, ctx.guild.id))
      await self.bot.db.commit()
      embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: jail set")
      await sendmsg(self, ctx, None, embed, None, None, None, None)  

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def unsetjail(self, ctx: commands.Context):
     if (not ctx.author.guild_permissions.administrator):
       e = discord.Embed(title="Command: unsetjail", description="disable jail module on your server",color=Colours.standard, timestamp=ctx.message.created_at)
       e.add_field(name="category", value="config")
       e.add_field(name="Arguments", value="<subcommand>")
       e.add_field(name="permissions", value="administrator", inline=True)
       e.add_field(name="Command Usage",value="```Syntax: ;setjail\nSyntax: ;nunsetjail```", inline=False)
       await sendmsg(self, ctx, None, e, None, None, None, None)
       return

     async with self.bot.db.cursor() as cursor:
      await cursor.execute(f"SELECT * FROM setme WHERE guild_id = {ctx.guild.id}") 
      check = await cursor.fetchone()
      if check is None:
       em = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: jail module is not set")
       await sendmsg(self, ctx, None, em, None, None, None, None) 
       return
      elif check is not None:
       button1 = Button(style=discord.ButtonStyle.grey, emoji=Emotes.approve)
       button2 = Button(style=discord.ButtonStyle.grey, emoji=Emotes.nono)
       embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: are you sure you want to clear jail module for this server?")

      async def button1_callback(interaction: discord.Interaction):
       if interaction.user != ctx.author:
         emb = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {interaction.user.mention}: this is not your message")  
         await interaction.response.send_message(embed=emb, ephemeral=True)
         return
       async with self.bot.db.cursor() as cursor:
        await cursor.execute(f"SELECT * FROM setme WHERE guild_id = {ctx.guild.id}") 
        check = await cursor.fetchone()
        channelid = check[0]
        roleid = check[1]
        channel = ctx.guild.get_channel(channelid)
        role = ctx.guild.get_role(roleid)
        try:   
         await role.delete()
        except:
          pass

        try:    
         await channel.delete()
        except:
         pass
       
        try:
         await cursor.execute(f"DELETE FROM setme WHERE guild_id = {ctx.guild.id}")
         await self.bot.db.commit() 
         embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: jail module has been cleared")
         await interaction.response.edit_message(embed=embed, view=None)  
        except:
          pass

      button1.callback = button1_callback

      async def button2_callback(interaction: discord.Interaction):
       if interaction.user != ctx.author:
        emb = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {interaction.user.mention}: this is not your message")  
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return

       embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: you have changed your mind") 
       await interaction.response.edit_message(embed=embed, view=None) 

      button2.callback = button2_callback

      view = View()
      view.add_item(button1)
      view.add_item(button2)
      await sendmsg(self, ctx, None, embed, view, None, None, None) 
    
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def jail(self, ctx: commands.Context, member: discord.Member=None, *, reason=None):
     if not ctx.author.guild_permissions.manage_channels: return await noperms(self, ctx, "manage_channels")
     if member == None:
       e = discord.Embed(title="Command: jail", description="jail a member",color=Colours.standard, timestamp=ctx.message.created_at)
       e.add_field(name="category", value="config")
       e.add_field(name="Arguments", value="[member]")
       e.add_field(name="permissions", value="manage_channels", inline=True)
       e.add_field(name="Command Usage",value="```Syntax: ;jail @andreilord```", inline=False)
       await sendmsg(self, ctx, None, e, None, None, None, None)
       return

     if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=Colours.standard, description=f"{ctx.author.mention}: you can't jail {member.mention}")
       await sendmsg(self, ctx, None, nope, None, None, None, None) 
       return
     
     async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM setme WHERE guild_id = {}".format(ctx.guild.id))
      chec = await cursor.fetchone()
      if chec is None:
        em = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: you don't setup the jail module")
        await sendmsg(self, ctx, None, em, None, None, None, None) 
        return

      await cursor.execute("SELECT * FROM jail WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
      check = await cursor.fetchone()
      if check is not None:
        em = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: {member.mention} is jailed already on this server")
        await sendmsg(self, ctx, None, em, None, None, None, None) 
        return
     
      if reason == None:
       reason = "No reason provided"

      roles = []
      for role in member.roles:
        if str(role.name): continue
        else:
            roles.append(role.id)

      sql_as_text = json.dumps(roles)
      await cursor.execute("INSERT INTO jail VALUES (?,?,?)", (ctx.guild.id, member.id, sql_as_text))
      await self.bot.db.commit()
      for role in member.roles:
        try:
            await member.remove_roles(role)
        except:
          continue

      roleid = chec[1]
      try:
       jail = ctx.guild.get_role(roleid)
       await member.add_roles(jail, reason=f"jailed by {ctx.author} - {reason}")
       success = discord.Embed(color=Colours.standard, description=f"{member.mention} got jailed - {reason}")
       await sendmsg(self, ctx, None, success, None, None, None, None) 
      except Exception as e:
       embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: there was a problem jailing {member.mention}...")
       await sendmsg(self, ctx, None, embed, None, None, None, None) 

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def unjail(self, ctx, *, member: discord.Member=None):
     k = 0
     name = "jail access"
     for role in ctx.author.roles:
        if name in role.name:
            k+=1

     if not ctx.author.guild_permissions.manage_channels and k==0: return await noperms(self, ctx, "manage_channels or jail access")

     if member == None:
       e = discord.Embed(title="Command: unjail", description="unjail a member",color=Colours.standard, timestamp=ctx.message.created_at)
       e.add_field(name="category", value="config")
       e.add_field(name="Arguments", value="[member]")
       e.add_field(name="permissions", value="manage_channels or jail access", inline=True)
       e.add_field(name="Command Usage",value="```Syntax: ;unjail @andreilord```", inline=False)
       await sendmsg(self, ctx, None, e, None, None, None, None)
       return

     if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: you can't jail {member.mention}")
       await sendmsg(self, ctx, None, nope, None, None, None, None) 
       return
    
     async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM setme WHERE guild_id = {}".format(ctx.guild.id))
      chec = await cursor.fetchone()
      if chec is None:
        em = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: you don't setup the jail module")
        await sendmsg(self, ctx, None, em, None, None, None, None) 
        return
      await cursor.execute("SELECT * FROM jail WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
      check = await cursor.fetchone()
      if check is None:
        em = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: {member.mention} is not jailed on this server")
        await sendmsg(self, ctx, None, embed, None, None, None, None) 
        return
    
      jail = chec[1]
      try:
        jailrole = ctx.guild.get_role(jail)
        await member.remove_roles(jailrole)
      except:
        pass

      sq = check[2]
      roles = json.loads(sq)
      for role in roles:
        try:
            rol = ctx.guild.get_role(role)
            await member.add_roles(rol, reason=f"unjailed by {ctx.author}")
        except:
            continue

      await cursor.execute("DELETE FROM jail WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))
      await self.bot.db.commit()
      embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: {member.mention} unjailed and has no roles")             
      await sendmsg(self, ctx, None, embed, None, None, None, None) 

async def setup(bot) -> None:
    await bot.add_cog(jail(bot))       


# This Bot Is Owned By Andrei Lord#0001 #
# All credits receive to sent, vlaz #
# Use Luma https://discord.gg/luma #