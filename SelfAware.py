import discord
import asyncio
import sqlite3
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import linecache

#To be replaced with slash commands instead of the existing prefix ones
def get_prefix(bot, message):
    prefixes = ['.', '!']
    return commands.when_mentioned_or(*prefixes)(bot, message)

initial_extensions = ['cogs.User',
                    'cogs.Admin',
                    'cogs.Owner',
                    'cogs.Color',
                    'cogs.Poll',
                    'cogs.Roles']
#Bot token for authentication on startup
TOKEN = linecache.getline(r'TOKEN.txt',2)

#Declared intents so the bot can modify users on its servers, read messages, and reactions
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command('help') #overriden with a custom help command

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + "\n")
    print("Servers I'm added to:")
    for server in bot.guilds:
        print(server.name)
    await bot.change_presence(status = discord.Status.do_not_disturb, activity = discord.Game(linecache.getline(r'status.txt',1)))
    return

async def load():
    for extension in initial_extensions:
        await bot.load_extension(extension)
        
async def main():
    await load()
    await bot.start(TOKEN)

asyncio.run(main())