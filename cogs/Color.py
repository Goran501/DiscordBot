import discord
import asyncio
import unicodedata
from discord.ext import commands
import sqlite3
import random
from PermCheck import CheckIfAdmin

class ColorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#Used to change username display color to any Hex value by creating and modifying a server role
#TO DO - Reimplement role position logic (roles with higher positions get to override permissions/color of those beneath)
    @commands.command(pass_context = True)
    async def color(self, context):
        guild = context.author.guild
        member = guild.get_member(context.author.id)
        pickedColor = context.message.content[7:]
        existingColor = False

        if not pickedColor:
            await context.send("Please add a hex color ----> https://htmlcolorcodes.com/      `.color hexcode`")
            return
        #A very simple/bad way to trim the response if needed (needs to be updated)
        if pickedColor.startswith(' '):
            pickedColor = pickedColor[1:]
        elif pickedColor.startswith('#'):
            pickedColor = pickedColor[1:]
        if pickedColor.endswith(' '):
            pickedColor = pickedColor[:-1]
        #Discord will not accept a pure black color (has it reserved for the default role color)
        if pickedColor == '000000':
            pickedColor = '000001'
        colorObj = discord.Color(int(pickedColor, 16))
        
        try:
            for role in guild.roles:
                if str(role) == ('USER-' + str(context.author.id)):
                    await role.edit(color = colorObj)
                    await context.send("Existing role found, and color changed!")
                    existingColor = True
                    break
        except:
            await context.sent ("I found your role, but couldn't change its color!")

        if not existingColor:
            try:
                for role in member.roles:
                    if 'RAINBOW-' in str(role):
                        await member.remove_roles(role)
                        break
            except:
                await context.send("I could not remove your default color role!")

            try:
                role = await context.guild.create_role(name = ('USER-'+ str(context.author.id)), color=colorObj)
                await member.add_roles(role)
                await context.send("Color changed!")
            except:
                await context.send("I could not assign your color role!")

#Rainbow 
#Command to replace default color of all users (without a custom color role), with a random one from a selection of 8
    @commands.command(pass_context = True, hidden = True)
    async def rainbow(self, context):
        allow = CheckIfAdmin(self, context)
        if allow == False:
            return

        rainbow = [0] * 8 
        rainbowHex = ['f04d4d','f0924d','e1d035','1f8b4c','78beb5','4766f3','bc47f3','f347af']
        rainbowText = ['Red','Orange','Yellow','Green','Cyan','Blue','Purple','Pink']

        #Removes previously implemented standard color roles
        rainbowContext = str(context.message.content[9:])
        if rainbowContext == 'remove':
            for role in context.guild.roles:
                if 'RAINBOW-' in str(role):
                    await role.delete()
            await context.send('🌈 removed!')
            return

        rainbowExists = False
        for role in context.guild.roles:
            if 'RAINBOW-' in str(role):
                rainbowExists = True
                break

        if rainbowExists == False:
            i = 0
            while (i != 8):
                for role in context.guild.roles:
                    rolePosition = role.position

                rainbow[i] = await context.guild.create_role(name = ('RAINBOW-'+ rainbowText[i]), color= discord.Color(int(rainbowHex[i], 16)))
                await asyncio.sleep(0.3)
                await rainbow[i].edit(position = rolePosition)
                i+= 1
        else:
            for role in context.guild.roles:
                i = 0
                while (i != 8):
                    if role.name == ('RAINBOW-' + rainbowText[i]):
                        rainbow[i] = role
                        i = 8
                        break
                    i += 1

        for member in context.guild.members:
            if member.bot == True:
                continue
            noColor = True
            for role in context.guild.roles:
                if str(role) == ('USER-' + str(member.id)):
                    noColor = False
                    break
            if noColor == True:
                for role in member.roles:
                    if 'RAINBOW-' in str(role):
                        await member.remove_roles(role)
                        break
                await member.add_roles(rainbow[random.randint(0, 7)])
         
        await context.send("🌈")

async def setup(bot):
    await bot.add_cog(ColorCog(bot))