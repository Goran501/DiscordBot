import discord
from discord.ext import commands
import sqlite3
import random
import asyncio
from PermCheck import CheckIfAdmin

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#Custom help command that overrides discord's default. Will be superseeded once prefix commands are changed to slash commands.
    @commands.command(pass_context = True)
    async def help(self, context):
        myEmbed = discord.Embed(
                   title = 'Help is here!',
                   color = discord.Color.dark_red()
                   )
        myEmbed.add_field(name = '`.color (hex)`', value = 'Used to add a custom color to your name.', inline = False)
        myEmbed.add_field(name = '`.poll [time] (poll topic)`', value = 'Call for a poll.', inline = False)
        myEmbed.add_field(name = '`.roll (maxnumber)`', value = 'Roll a random number from 0 to yours.', inline = False)
        await context.author.send(content=None, embed=myEmbed)

        if CheckIfAdmin(self, context) == False:
          return

        myEmbed = discord.Embed(
                   title = 'Admin help is here!',
                   color = discord.Color.dark_red()
                   )
        myEmbed.add_field(name = '`.adduser (name)`', value = 'Used to add a user to the set default rank in case the server is in private mode.', inline = False)
        myEmbed.add_field(name = '`.addrole (Role Emoji) (Role Name)`', value = 'Add a new and pingable role for a game or activity!', inline = False)
        myEmbed.add_field(name = '`.removerole (Role Emoji)`', value = 'Remove an existing role from the roles list.', inline = False)
        myEmbed.add_field(name = '`.rainbow`', value = 'Several color roles to add diversity to your server! Can be overriden with a personalized one (.color)', inline = False)
        myEmbed.add_field(name = '`.user (role name)`', value = 'Defines the default User group for the bot (Owner only)', inline = False)
        myEmbed.add_field(name = '`.admin (role name)`', value = 'Defines the default Admin group for the bot (Owner only)', inline = False)

        await context.author.send(content=None, embed=myEmbed)

#Bot messages server owner on join
    async def on_guild_join(self, guild):
        await guild.owner.send('Thank you for adding me to your server!')
        await guild.owner.send('To check user commands please use `.help`, and to check admin commands simply write the same command in the server you moderate.')

#Command for adding new people to the defined user role without having to go find the user/role
    @commands.command(pass_context = True, hidden = True)
    async def adduser(self, context):
        allow = CheckIfAdmin(self, context)
        if allow == False:
            return

        addRole = None
        server = int(context.message.guild.id)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        c.execute("SELECT * FROM server_info WHERE server_id = (?);", (server,))
        if c.fetchone() == None:
            c.execute("INSERT INTO server_info VALUES (?,?,?,?,?);", (server, 0, 0, 0, None)) 
        c.execute("SELECT user_role FROM server_info WHERE server_id = (?);", (server,))
        userRole = c.fetchall()
        conn.commit()
        conn.close()

        for role in context.message.guild.roles:
            if str(role.id) in str(userRole):
                addRole = role
                break
        guild = context.author.guild
        userToAdd = None
        for member in guild.members:
            memberCompare = str(member)
            memberCompare = memberCompare.split("#")
            if str(memberCompare[0]) == str(context.message.content[9:]):
                userToAdd = member
                break

        try:
            await userToAdd.add_roles(addRole)
            await context.send("User added!")
        except:
            await context.send("Cannot add user. Did you spell the name properly?")

#Setting the server's default admin role for the bot to recognize
    @commands.command(pass_context = True, hidden = True)
    async def admin(self, context):
        if context.message.author.id != context.guild.owner_id:
            await context.send("This is a server owner only command.")
            return
        info = context.message.content[7:]
        if not info:
            await context.send("`.admin (Admin Role ID)`")
            return

        server = int(context.message.guild.id)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        c.execute("SELECT * FROM server_info WHERE server_id = (?);", (server,))
        if c.fetchone() == None:
            c.execute("INSERT INTO server_info VALUES (?,?,?,?,?);", (server, 0, 0, 0, None)) 

        c.execute("UPDATE server_info SET admin_role = (?) WHERE server_id = (?);", (info, server))
        conn.commit()
        conn.close()
        await context.send("Info added.")

#Setting the server's default user role for the bot to recognize
    @commands.command(pass_context = True, hidden = True)
    async def user(self, context):
        if context.message.author.id != context.guild.owner_id:
            await context.send("This is a server owner only command.")
            return
        info = context.message.content[6:]
        if not info:
            await context.send("`.user (User Role ID)`")
            return

        server = int(context.message.guild.id)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        c.execute("SELECT * FROM server_info WHERE server_id = (?);", (server,))
        if c.fetchone() == None:
            c.execute("INSERT INTO server_info VALUES (?,?,?,?,?);", (server, 0, 0, 0, None)) 

        c.execute("UPDATE server_info SET user_role = (?) WHERE server_id = (?);", (info, server))
        conn.commit()
        conn.close()
        await context.send("Info added.")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))