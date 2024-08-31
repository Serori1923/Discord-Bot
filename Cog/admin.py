import discord
from discord.ext import commands
from discord import app_commands
import time

def journal(user,event):
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S |', time.localtime())
    print(f'{nowtime} Requester: {user} | {event}')

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description='清除訊息 (Admin only)')
    @commands.has_any_role('Server Admin')
    async def clear(self, interaction, num:int):
        await interaction.channel.purge(limit=num)
        journal(interaction.user , 'Messages cleared')                                    #在後台紀錄發生事件

    @app_commands.command(description='把壞人趕走 (Admin only)')
    @commands.has_any_role('Server Admin')
    async def kick(self, interaction, member : discord.Member, *,reason:str=""):
        await member.kick(reason=reason)
        await interaction.response.send_message('小菜一碟啦喵')


    @app_commands.command(description='把壞人關進籠子裡 (Admin only)')
    @commands.has_any_role('Server Admin')
    async def ban(self, interaction,member : discord.Member, *,reason:str=""):
        await member.ban(reason=reason)
        await interaction.response.send_message('報告剷屎官!已經把他關進地牢了喵')


    @app_commands.command(description='把壞人放出來 (Admin only)')
    @commands.has_any_role('Server Admin')
    async def unban(self, interaction,*, member : discord.Member):
        banned_users =await interaction.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user =  ban_entry.user

            if (user.name, user.discriminator) ==(member_name, member_discriminator):
                await interaction.guild.unban(user)
                await interaction.response.send_message('好啦勉為其難放他出來')
                return

async def setup(bot):
    await bot.add_cog(Admin(bot))
