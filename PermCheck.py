#Checks if the person running an Admin command has the required permission level
import discord
import sqlite3

def CheckIfAdmin(self, context):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    server = int(context.message.guild.id)
    allow = False

    if context.message.author.id == context.guild.owner_id:
        allow = True

    elif str(2146958847) in str(context.message.author.guild_permissions):       
        allow = True
        
    else:
        c.execute("SELECT admin_role FROM server_info WHERE server_id = (?);", (server,))
        adminRole = str(c.fetchone())
        for role in context.message.author.roles:
           if str(role) in str(adminRole):
              allow = True
              break

    conn.close()
    return(allow)