import discord
import asyncio
import unicodedata
from discord.ext import commands
import sqlite3
import random

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#User on join (welcome message and default color/role add)
    async def on_member_join(self, member):
        if member.bot == True:
            return

        myEmbed = discord.Embed(
                    title = '**Welcome to ' + str(member.guild.name) + '!**',
                    description = 'Please enjoy your stay, and be sure to message an admin if you need any help.',
                    color = discord.Color.dark_red()
                    )
        try:
            await member.send(content=None, embed=myEmbed)
        except:
            return
        
        #If the server has selected to use the .rainbow command the following code runs on user join.
        rainbowExists = False
        for role in member.guild.roles:
          if 'RAINBOW-' in str(role):
                rainbowExists = True
                break
        if rainbowExists == False:
            return

        rainbow = None
        rainbowText = ['Red','Orange','Yellow','Green','Cyan','Blue','Purple','Pink']
        rainbowName = 'RAINBOW-' + rainbowText[random.randint(0, 7)]

        for role in member.guild.roles:
                if role.name == rainbowName:
                        rainbow = role
                        break
        await member.add_roles(rainbow)

#User on leave (color role remove)
    async def on_member_remove(self, member):
        if member.bot == True:
            return

        for role in member.guild.roles:
            if str(role) == ('USER-' + str(member.id)):
                await role.delete()
                break

#Roll command
    @commands.command(pass_context = True)
    async def roll(self, context):
        isNumber = context.message.content[6:].split(' ')
        
        try:
            await context.send(random.randint(1, int(isNumber[0])))
        except:
            await context.send('`.roll (maxnumber)`')

async def setup(bot):
    await bot.add_cog(UserCog(bot))