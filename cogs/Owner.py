import discord
from discord.ext import commands
import linecache

class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Changes current bot status, and saves the choice to a file so it can load it on restart
    @commands.command(pass_context = True, hidden = True)
    async def status(self, context):
      ownerName = linecache.getline(r'startup.txt',4)
      if ownerName != str(context.message.author):
          await context.send("Sorry, but you do not have permission to use this command.")
          return

      #Save for future use
      status_file = open("status.txt","w")
      status_file.write(context.message.content[8:])
      status_file.close()

      #Change description
      await context.send("Status description updated.")
      await self.bot.change_presence(status=discord.Status.do_not_disturb, activity = discord.Game(context.message.content[8:]))


    @commands.command(pass_context = True, hidden = True)
    async def leave(self, context):
      ownerName = linecache.getline(r'startup.txt',4)
      if ownerName != str(context.message.author):
          await context.send("Sorry, but you do not have permission to use this command.")
          return
      await context.message.guild.leave()
    

async def setup(bot):
    await bot.add_cog(OwnerCog(bot))
