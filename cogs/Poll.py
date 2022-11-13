import discord
import asyncio
import unicodedata
from discord.ext import commands
import sqlite3
import random

class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#Poll command
    @commands.command(pass_context = True)
    async def poll(self, context):
        timer = 0
        isNumber = context.message.content[6:].split(' ')
        lengthOfNumber = 0
        try:
            timer = float(isNumber[0])
            lengthOfNumber = int(len(isNumber[0]))
            if float(isNumber[0]) > 1440:
                await context.send('Poll cannot last longer than 1440 minutes (24 hours).')
                return
        except:
            pass
        if not context.message.content[6:]:
            await context.send('`.poll [minutes] (poll topic)`')
            return
        line = context.message.content[(6 + lengthOfNumber):].upper()
        myEmbed = discord.Embed(
                    title = '**' + str(line) + '**',
                    color = discord.Color.dark_red()
                    )
        #removed avatar_url
        myEmbed.set_author(name = str(context.author.name), icon_url = context.author.avatar)
        if timer != 0:
            if timer != 1:
                myEmbed.add_field(name = 'The poll lasts for:', value = '`' + str(timer) + ' minutes.`', inline = False)
            else:
                myEmbed.add_field(name = 'The poll lasts for:', value = '`' + str(timer) + ' minute.`', inline = False)
        bot_message = await context.send(content=None, embed=myEmbed)
        
        await bot_message.add_reaction('✅')
        await bot_message.add_reaction('❎')

        if timer != 0:
            pollVoters = await context.guild.create_role(name = 'Poll Voters', mentionable = True)
            votes = [-1, -1]
            counter = 0
            await asyncio.sleep(timer*60)

            bot_message = await bot_message.fetch()
            for reaction in bot_message.reactions:
                async for user in reaction.users():
                    try:
                        if user != bot_message.author: await user.add_roles(pollVoters)
                    except(discord.Forbidden):
                        await context.send('I do not have the permission to add roles.')
                    except(discord.HTTPException):
                        await context.send('Adding roles failed.')
                if (reaction.emoji == '✅') or (reaction.emoji == '❎'):
                    votes[counter] += int(reaction.count)
                counter+=1

            mentionMessage = await context.send(pollVoters.mention)
            await context.send('Poll `' + str(context.message.content[(7 + lengthOfNumber):]) + '` is over!')
            if votes[0] == votes[1]:
                if votes[0] == 0:
                    await context.send('Looks like everyone fell asleep. Let us call it a tie!')
                elif votes[0] > 1:
                    await context.send('And would you look at that, the results are tied at ' + str(votes[0]) + ' votes each!')
                else:
                    await context.send('And would you look at that, the results are tied at 1 vote each. You both were really close to winning there!')
            elif votes[0] > votes[1]:
                if votes[0] > 1:
                    await context.send('It has passed with ' + str(votes[0]) + ' votes!')
                else:
                    await context.send('It has passed with 1 vote! Out of 1 vote!')
            elif votes[0] < votes[1]:
                if votes[1] > 1:
                    await context.send('It has failed with ' + str(votes[1]) + ' people not liking the idea very much!')
                else:
                    await context.send('It has failed with 1 vote!')
            await mentionMessage.delete()
            await pollVoters.delete()

async def setup(bot):
    await bot.add_cog(PollCog(bot))