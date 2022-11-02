import discord
from discord.ext import commands
import sqlite3
import asyncio
from PermCheck import CheckIfAdmin

#Roles.py enables an embedded message that Users on a server react to. Each reaction adds them automatically to a pingable role (group) for their convenience.
#Admins can create new roles that are added to the embedded message, both role creation and message editing is done with the "addrole" and "removerole" commands.

#Edit the role message with new info, called when adding or removing roles.
async def editMessage(self, context):       
    server = int(context.message.guild.id)
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("SELECT emoji, role FROM roles WHERE server_id = (?);", (server,))
    sortingList = c.fetchall()
    c.execute("SELECT ping_message_id FROM server_info WHERE server_id = (?);", (server,))
    messageID = str(c.fetchall())
    messageID = messageID[2:-3]
    c.execute("SELECT ping_message_channel FROM server_info WHERE server_id = (?);", (server,))
    channelName = c.fetchall()
    conn.close()
    sorting = '\n'.join(map(str, sortingList)) 
    message = None

    for channel in context.message.guild.channels:
        if str(channel) in str(channelName):
            message = await channel.fetch_message(int(messageID))
            break 
    myEmbed = discord.Embed(
              title = 'List of roles!',
              color = discord.Color.dark_red()
              )
    if sorting == '':
        myEmbed.add_field(name='React to the roles you wish to be pinged with.', value = 'Empty List!', inline = False)
    else:
        myEmbed.add_field(name='React to the roles you wish to be pinged with.', value = sorting, inline = False)

    await message.edit(content=None, embed=myEmbed)

class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#Setting the server's message ID for role reaction (the bot will save it for use later to find the message)
    @commands.command(pass_context = True, hidden = True)
    async def message(self, context):
        allow = CheckIfAdmin(self, context)
        if allow == False:
            return
            
        myEmbed = discord.Embed(
                  title = 'List of roles!',
                  color = discord.Color.dark_red()
                  )
        botMessage = await context.send(content=None, embed=myEmbed)

        serverid = int(context.message.guild.id)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM server_info WHERE server_id = (?);", (serverid,))

        if c.fetchone() == None:
            c.execute("INSERT INTO server_info VALUES (?,?,?,?,?);", (serverid, 0, 0, 0, None)) 
        else:
            c.execute("SELECT ping_message_id FROM server_info WHERE server_id = (?);", (serverid,))
            messageID = str(c.fetchall())
            messageID = messageID[2:-3]
            c.execute("SELECT ping_message_channel FROM server_info WHERE server_id = (?);", (serverid,))
            channelName = c.fetchall()

            for channel in context.message.guild.channels:
                if str(channel) in str(channelName):
                    try:
                        message = await channel.get_message(int(messageID))
                        await message.delete()
                        break
                    except:
                        pass

            c.execute("SELECT emoji FROM roles WHERE server_id = (?);", (serverid,))
            emojiPopulation = c.fetchall()

            for emoji in emojiPopulation:
                emoji = str(emoji).replace('(', '').replace(')', '').replace('\'', '').replace(',', '').replace('<', '').replace('>', '')
                await botMessage.add_reaction(emoji)

        try:
            await context.message.delete()
        except:
            pass
       
        c.execute("UPDATE server_info SET ping_message_id = (?), ping_message_channel = (?)  WHERE server_id = (?);", (int(botMessage.id), str(botMessage.channel), serverid))
        conn.commit()
        conn.close()
        await editMessage(self, context)

#Command to add a new role for pings to the embedded message (Can rewrite old ones)
    @commands.command(pass_context = True, hidden = True)
    async def addrole(self, context):
        allow = CheckIfAdmin(self, context)
        if allow == False:
            return

        info = context.message.content[8:].split(' ')
        if len(info) > 3:
            await context.send("You cannot have spaces in your role name.")
            return
        if len(info) < 3:
            await context.send("`.addrole (Role Emoji) (Role Name)`")
            return

        try:
            await context.guild.create_role(name = info[2])
            #await editMessage(self, context)
        except:
            await context.send("Sorry, I cannot create the role!")
            return

        server = int(context.message.guild.id)  
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        c.execute("SELECT * FROM roles WHERE server_id = (?) AND emoji = (?);", (server, info[1]))
        if c.fetchone() == None:
            c.execute("INSERT INTO roles VALUES (?,?,?);", (server, None, info[1]))
        c.execute("UPDATE roles SET emoji = (?), role = (?) WHERE server_id = (?) AND emoji = (?);", (info[1], info[2], server, info[1]))

        c.execute("SELECT ping_message_id FROM server_info WHERE server_id = (?);", (server,))
        messageID = str(c.fetchall())
        messageID = messageID[2:-3]
        c.execute("SELECT ping_message_channel FROM server_info WHERE server_id = (?);", (server,))
        channelName = c.fetchall()
        message = None

        for channel in context.message.guild.channels:
            if str(channel) in str(channelName):
                message = await channel.fetch_message(int(messageID))
                break         
        try:
            await message.add_reaction(info[1])
        except:
            await context.send("Sorry, I cannot add the role!")
            return      

        conn.commit()
        conn.close()
        await editMessage(self, context)
        await context.send("Role added!")

#Command to remove a role for pings from the embedded message
    @commands.command(pass_context = True, hidden = True)
    async def removerole(self, context):
        allow = await CheckIfAdmin(self, context)
        if allow == False:
            return

        info = context.message.content[10:].split(' ')
        if len(info) > 2:
                await context.send("You only need to input the role emoji.")
                return
        if info[1] == None:
                await context.send("`.removerole (Role Emoji)`")
                return
       
        server = int(context.message.guild.id)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("SELECT emoji FROM roles WHERE server_id = (?) AND emoji = (?);", (server, info[1]))
        emojiToRemove = c.fetchall()
        c.execute("SELECT role FROM roles WHERE server_id = (?) AND emoji = (?);", (server, info[1]))
        roleToRemove = c.fetchall()

        try:
            for role in context.message.guild.roles:
                 if str(role) in str(roleToRemove):
                     await role.delete()
                     break
        except:
            await context.send("Sorry, I cannot remove the role!")
            return

        c.execute("SELECT ping_message_id FROM server_info WHERE server_id = (?);", (server,))
        messageID = str(c.fetchall())
        messageID = messageID[2:-3]
        c.execute("SELECT ping_message_channel FROM server_info WHERE server_id = (?);", (server,))
        channelName = c.fetchall()
        c.execute("SELECT ping_message_channel FROM server_info WHERE server_id = (?);", (server,))
        channelName = c.fetchall()

        message = None
        for channel in context.message.guild.channels:
            if str(channel) in str(channelName):
                message = await channel.get_message(int(messageID))
                break
        for reaction in message.reactions:
            if str(reaction.emoji) in str(emojiToRemove):
                async for user in reaction.users():
                    await message.remove_reaction(reaction.emoji, user)

        c.execute("DELETE FROM roles WHERE server_id = (?) AND emoji = (?);", (server, info[1]))
        conn.commit()
        conn.close()
        await editMessage(self, context)
        await context.send("Role removed!")        

#Beneath are a few functions that deal with adding people to different server roles, based on their reactions to a one command set up embed message
#The embed message itself is modified through the Admin.py cog

#Role add or remove on reaction
    #Role add
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("SELECT ping_message_id FROM server_info WHERE server_id = (?);", (payload.guild_id,))
        messageID = c.fetchall()
        c.execute("SELECT ping_message_channel FROM server_info WHERE server_id = (?);", (payload.guild_id,))
        channelName = c.fetchall()
        conn.close()

        if str(payload.message_id) in str(messageID):
            message = None
            for channel in guild.channels:
                if channel.name in str(channelName):
                    message = await channel.get_message(payload.message_id)
                    break
            member = guild.get_member(payload.user_id)
            myEmoji = payload.emoji

            conn = sqlite3.connect('data.db')
            c = conn.cursor()
            c.execute("SELECT emoji FROM roles WHERE server_id = (?);", (payload.guild_id,))
            emojiCheck = c.fetchall()
            check = False
            for emoji in emojiCheck:
                if str(myEmoji) in str(emoji):
                    check = True
                    break
            if check == False:
              await message.remove_reaction(payload.emoji, member)
              return

            c.execute("SELECT role FROM roles WHERE server_id = (?) AND emoji = (?);", (payload.guild_id, str(myEmoji)))
            dataRole = c.fetchall()
            conn.close()

            if "Arcation#9905" == str(member):
                return
            for role in guild.roles:
                if str(role) in str(dataRole):
                   await member.add_roles(role)
                   break

    #Role remove
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("SELECT ping_message_id FROM server_info WHERE server_id = (?);", (payload.guild_id,))
        messageID = c.fetchall()
        c.execute("SELECT ping_message_channel FROM server_info WHERE server_id = (?);", (payload.guild_id,))
        channelName = c.fetchall()
        conn.close()

        if str(payload.message_id) in str(messageID):
            message = None
            for channel in guild.channels:
                if channel.name in channelName: 
                    message = await channel.get_message(payload.message_id)
                    break
            member = guild.get_member(payload.user_id)
            myEmoji = payload.emoji

            conn = sqlite3.connect('data.db')
            c = conn.cursor()
            c.execute("SELECT role FROM roles WHERE server_id = (?) AND emoji = (?);", (payload.guild_id, str(payload.emoji)))
            dataRole = c.fetchall()
            conn.close()
            for role in guild.roles:
                if str(role) in str(dataRole):
                   await member.remove_roles(role)
                   break

async def setup(bot):
    await bot.add_cog(RolesCog(bot))