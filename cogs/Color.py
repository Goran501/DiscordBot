import discord
import asyncio
import unicodedata
from discord.ext import commands
import sqlite3
import random
from PermCheck import CheckIfAdmin

rainbowHex = ['f04d4d','f0924d','e1d035','1f8b4c','78beb5','4766f3','bc47f3','f347af']
rainbowText = ['Red','Orange','Yellow','Green','Cyan','Blue','Purple','Pink']

async def applyRole(context, chosenColor):
    guild = context.author.guild
    member = guild.get_member(context.author.id)
    try:
        for role in guild.roles:
            if str(role) == ('USER-' + str(context.author.id)):
                await role.edit(color = chosenColor)
                await context.send("Existing role found, and color changed!")
                return
    except:
        await context.sent ("I found your role, but couldn't change its color!")
        return
            
    try:
        for role in member.roles:
            if 'RAINBOW-' in str(role):
                await member.remove_roles(role)
                break
    except:
        await context.send("I could not remove your default color role!")

    try:
        role = await context.guild.create_role(name = ('USER-'+ str(context.author.id)), color=chosenColor)
        await member.add_roles(role)
        await context.send("Color changed!")
    except:
        await context.send("I could not assign your color role!")

class ColorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#Used to change username display color to any Hex value by creating and modifying a server role
    @commands.command(pass_context = True)
    async def color(self, context):
        guild = context.author.guild
        member = guild.get_member(context.author.id)

        fullMessage = context.message.content.split()
        try:
            pickedColor = fullMessage[1]
        except:
            await context.send("Please add a hex color ----> https://htmlcolorcodes.com/      `.color hexcode`")
            return            

        for index, presetColor in enumerate(rainbowText):
            if str(pickedColor).lower() == str(presetColor).lower():
                await applyRole(context, discord.Color(int(rainbowHex[index], 16)))
                return

        if pickedColor.startswith('#'):
            pickedColor = pickedColor[1:]
        #Discord will not accept a pure black color (has it reserved for the default role color)
        if pickedColor == '000000':
            pickedColor = '000001'

        try:
            await applyRole(context, discord.Color(int(pickedColor, 16)))
        except:
            await context.send("Color _" + str(pickedColor) +"_ was not found.")
            return             

#Rainbow 
#Command to replace default color of all users (without a custom color role), with a random one from a selection of 8
    @commands.command(pass_context = True, hidden = True)
    async def rainbow(self, context):
        allow = CheckIfAdmin(self, context)
        if allow == False:
            return
        #List of roles will be added to this array
        rainbow = [0] * 8 

        #Removes previously implemented standard color roles
        rainbowContext = str(context.message.content[9:])
        if rainbowContext == 'remove':
            for role in context.guild.roles:
                if 'RAINBOW-' in str(role):
                    await role.delete()
            await context.send('🌈 removed!')
            return

        #Checks if server already has created roles
        rainbowExists = False
        for role in context.guild.roles:
            if 'RAINBOW-' in str(role):
                rainbowExists = True
                break
        #Creates roles on the server if the command is ran for the first time
        if rainbowExists == False:
            i = 0
            while (i != 8):
                for role in context.guild.roles:
                    rolePosition = role.position

                rainbow[i] = await context.guild.create_role(name = ('RAINBOW-'+ rainbowText[i]), color= discord.Color(int(rainbowHex[i], 16)))
                await asyncio.sleep(0.3)
                await rainbow[i].edit(position = rolePosition)
                i+= 1
        #Loads already existing roles
        else:
            for role in context.guild.roles:
                i = 0
                while (i != 8):
                    if role.name == ('RAINBOW-' + rainbowText[i]):
                        rainbow[i] = role
                        i = 8
                        break
                    i += 1

        #Adds a standard color role to every server member without a custom (.color) one
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