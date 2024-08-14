import discord
from discord import app_commands
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get
from discord.ui import Select, View
import asyncio
from yt_dlp import YoutubeDL
import time
import json

#設定檔
ydl_wait_embed = discord.Embed(title="喵喵喵~ 請稍等一下喔~~~" , color=0xffd700)
ydl_embed = ydl_wait_embed
playing_embed = discord.Embed(title="好啦 就是工具貓啦 幫你播就是了" , color=0xffd700)
bot_at = 'None'
bot_used_by = 'None'
ftp=0
YDL_OPTIONS = {'format': 'm4a/bestaudio/best' , 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

with open('setting.json', 'r', encoding='utf8') as jsonFile:
    setting = json.load(jsonFile)

def journal(user,event):
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S |', time.localtime())
    print(f'{nowtime} Requester: {user} | {event}')

def writeJData(Data):
    with open('playlist.json', 'w', encoding='utf-8') as file:
        json.dump(Data, file, indent=4, ensure_ascii=False)

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.bot.tree.on_error = on_tree_error

    @app_commands.command(description='播放')
    @app_commands.describe(search = "直接輸入要播放的歌名，或是輸入YT影片連結，或YT Music歌曲連結")
    async def play(self, interaction, search:str):
        Mode = 0
        if "youtube.com" in search or "youtu.be" in search:
            Mode = 1

        voice = get(self.bot.voice_clients, guild=interaction.guild)                #取得Bot所在頻道
            
        if voice == None:                                                           #如果Bot不在語音頻道中就加入指令請求者所在之頻道
            try:                                                                    #try是為了偵測指令請求者是否在語音頻道中
                channel = interaction.user.voice.channel
            
                await channel.connect()
                global bot_at , bot_used_by
                bot_at = channel                                                    #紀錄Bot連接到哪個語音頻道
                bot_used_by = channel
                voice = get(self.bot.voice_clients, guild=interaction.guild)
                journal(interaction.user, f'Bot Connected to [{channel}]')                #在後台紀錄發生事件

            except asyncio.exceptions.TimeoutError:
                await self.bot.voice_clients.disconnect()
                await channel.connect()
                journal(interaction.user, f'Bot ReConnected to [{channel}]')                #在後台紀錄發生事件
            except Exception:                                                       #如果指令請求者不在語音頻道中，發送提示
                await interaction.response.send_message('你不在任何一個語音頻道中，所以在你想好你要去哪裡之前不要來吵我')
                return


        elif voice != None:                                                         #如果Bot在語音頻道中
            try:                                                                    #try是為了偵測指令請求者是否在語音頻道中
                requester = interaction.user.voice.channel
                if requester != bot_at:                                             #如果指令請求者和Bot不在同一個語音頻道
                    await interaction.response.send_message('請不要嘗試在別人的房間放聲音')
                    return

            except Exception:                                                       #如果指令請求者不在語音頻道中，發送提示
                await interaction.response.send_message('你有在頻道裡嗎?')
                return

        try:                                                                        #偵測擷取音訊時是否發生錯誤
            global ydl_embed, playing_embed, ftp
            if ftp==0:
                await interaction.response.send_message(embed=ydl_wait_embed)
                ydl_embed = await interaction.original_response()
            else:
                await interaction.response.defer(ephemeral=True)
            
            print('\n------------------播放音檔------------------')
            with YoutubeDL(YDL_OPTIONS) as ydl:
                global video_title, video_url
                URL = ""
                if Mode == 0:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)
                    for entry in info['entries']:
                        video_title = entry['title']
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        URL = entry['url']

                else:
                    info = ydl.extract_info(search, download=False)
                    video_title = info.get('title', None)
                    video_url = search
                    URL = info['url']

            print('-------------------------------------------- \n')
            if voice.is_playing():
                with open('playlist.json', 'r', encoding='utf8') as pl:
                    playlist = json.load(pl)

                new_item = {
                    "Title": f"{video_title}",
                    "Video_url": f"{video_url}",
                    "URL": f"{URL}"
                }
                playlist.append(new_item)

                writeJData(playlist)
                
                await interaction.followup.send(f"已將歌曲加入至播放清單! 使用**/playlist**查看待播歌曲!")
                journal(interaction.user, 'Join Video To Playlist')

            else:
                voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: self.bot.loop.create_task(Videoplay(interaction, self.bot)))
                voice.is_playing()

            
                playing_embed=discord.Embed(title="好啦 就是工具貓啦 幫你播就是了" , color=0xffd700)
                playing_embed.add_field(name="播放狀態", value="播放中🐵", inline=True)
                playing_embed.add_field(name="正在播放", value=f"【***[{video_title}]({video_url})***】", inline=False)
                
                select = Select(options=[
                    discord.SelectOption(label="繼續播放", emoji="▶", value="繼續播放"),
                    discord.SelectOption(label="暫停播放", emoji="⏸", value="暫停播放"),
                    discord.SelectOption(label="停止播放", emoji="⏹", value="停止播放"),
                    discord.SelectOption(label="跳下一首", emoji="⏩", value="跳下一首"),
                ])
                view = View(timeout=None)
                view.add_item(select)
                async def my_callback(interaction): #return 0=運行正常 1=沒有播放中的音樂 2=正在播放中 3=Bot不在語音中 4=播放清單已空
                    if select.values[0]=="繼續播放": 
                        ErrorCode = await resume(interaction, self.bot)
                        if ErrorCode==0:
                            await ydl_embed.edit(embed=playing_embed)
                            await interaction.response.defer()
                        elif ErrorCode==1:
                            await interaction.response.send_message("你還沒播放任何東西呢", ephemeral=True)
                        elif ErrorCode==2:
                            await interaction.response.send_message("已經在播放了喔 沒聽見的話可能要檢查耳朵了(´･_･`)", ephemeral=True)

                    if select.values[0]=="暫停播放":
                        ErrorCode = await pause(interaction, self.bot)
                        if ErrorCode==0:
                            await ydl_embed.edit(embed=pause_embed)
                            await interaction.response.defer()
                        elif ErrorCode==1:
                            await interaction.response.send_message("現在沒有在播放喔", ephemeral=True)
                        elif ErrorCode==3:
                            await interaction.response.send_message("不是 我連房間都沒進去，你是想要我暫停甚麼?", ephemeral=True)
                            
                    if select.values[0]=="停止播放":
                        ErrorCode = await stop(interaction, self.bot)
                        if ErrorCode==0:
                            await ydl_embed.edit(embed=stop_embed)
                            await interaction.response.defer()
                        elif ErrorCode==1:
                            await interaction.response.send_message("現在沒有在播放喔", ephemeral=True)

                    if select.values[0]=="跳下一首":
                        ErrorCode = await next(interaction, self.bot)
                        if ErrorCode==0:
                            await interaction.response.defer()
                        elif ErrorCode==1:
                            await interaction.response.send_message("現在沒有在播放喔", ephemeral=True)
                        elif ErrorCode==4:
                            await interaction.response.send_message("已經沒有下一首歌了喵", ephemeral=True)
                
                select.callback=my_callback

                if ftp==0:
                    await ydl_embed.edit(embed=playing_embed)
                    await interaction.channel.send(view=view)
                    ftp=1
                else:
                    try:
                        await ydl_embed.edit(embed=playing_embed)
                        await interaction.followup.send("照你要求的播了喵")
                    except Exception as e:
                        await interaction.channel.purge(limit=2)
                        ydl_embed = await interaction.channel.send(embed=playing_embed)
                        await interaction.channel.send(view=view)
                        await interaction.followup.send("照你要求的播了喵")
                journal(interaction.user, 'Play video')
            
        except Exception as e:                                                      #按發生錯誤之類型提示使用方式
            print('捕捉錯誤資訊: '+ str(e))
            print("播放連結錯誤")
            print('-------------------------------------------- \n')
            if ftp == 0:
                error_embed = discord.Embed(title="出錯了喵 檢查一下連結是否正確吧!" , color=0xffd700)
                await ydl_embed.edit(embed = error_embed)
            else:
                try:
                    await interaction.followup.send('你輸入的連結有誤(可能是輸入成Youtube外或是搜尋頁面的連結)，請重新輸入正確的「影片連結」')
                
                except Exception:
                    await interaction.response.send_message('你輸入的連結有誤(可能是輸入成Youtube外或是搜尋頁面的連結)，請重新輸入正確的「影片連結」')

    @app_commands.command(description='查看播放清單或移除歌曲')
    @app_commands.describe(delete = "輸入要刪除的歌曲編號")
    async def playlist(self, interaction, delete:int=None):
        await interaction.response.defer()
        with open('playlist.json', 'r', encoding='utf8') as pl:
            Playlist = json.load(pl)

        PL_embed = discord.Embed(title="目前待播歌曲!" , color=0xffd700)

        if isinstance(Playlist, list) and not Playlist:
            PL_embed = discord.Embed(title="清單就像本喵的餐盤一樣空空的喔" , color=0xffd700)
            PL_embed.add_field(name="餐盤實況 ↓", value="🍽️🍃...", inline=True)

        elif delete != None:
            try:
                Playlist.pop(delete-1)

                writeJData(Playlist)
                await interaction.channel.send("刪除成功 清單更新囉!")
            except Exception:
                await interaction.followup.send("清單沒這編號捏，要看清楚再刪除喔~")
                return
        
        Number = 1
        for song in Playlist:
            PL_embed.add_field(name=f"下 {Number} 首播放歌曲", value=f"***[{song['Title']}]({song['Video_url']})***", inline=False)
            Number += 1

        await interaction.followup.send(embed=PL_embed)


async def pause(interaction, client):
    try:                                                                        #try是為了偵測Bot是否在語音頻道中
        voice = get(client.voice_clients, guild=interaction.guild)
        global pause_embed
        if voice.is_playing():
            voice.pause()
            pause_embed=discord.Embed(title="播了又要暫停 你真的是麻煩大王欸" , color=0xffd700)
            pause_embed.add_field(name="播放狀態", value="暫停中🙊", inline=True)
            pause_embed.add_field(name="正在播放", value=f"【***[{video_title}]({video_url})***】", inline=False)
            return 0
        else:
            return 1

    except Exception as e:
        print('捕捉錯誤資訊: '+ str(e))
        print("bot尚未加入語音頻道")
        return 3

async def resume(interaction, client):
    voice = get(client.voice_clients, guild=interaction.guild)

    if voice.is_paused():
        voice.resume()
        return 0

    elif voice.is_playing():
        return 2
    else:
        return 1

async def stop(interaction, client):
    voice = get(client.voice_clients, guild=interaction.guild)

    global stop_embed
    if voice.is_playing():
        voice.stop()
        stop_embed=discord.Embed(title="可以休息了 真開心" , color=0xffd700)
        stop_embed.add_field(name="播放狀態", value="痴痴的等待著下一次的點播🐒", inline=True)
        stop_embed.add_field(name="正在播放", value=f"**`甚麼都沒在播啦`**", inline=False)
        return 0

    else:
        return 1

async def next(interaction, client):
    voice = get(client.voice_clients, guild=interaction.guild)

    if voice.is_playing():
        with open('playlist.json', 'r', encoding='utf8') as pl:
            playlist = json.load(pl)

        if isinstance(playlist, list) and not playlist:
            return 4
        else:
            voice.stop()
            return 0
    else:
        return 1

async def on_tree_error(interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        return await interaction.response.send_message(f"Command is currently on cooldown! Try again in **{error.retry_after:.2f}** seconds!")
    elif isinstance(error, app_commands.MissingPermissions):
        return await interaction.response.send_message(f"You're missing permissions to use that")
    else:
        raise error

async def Videoplay(interaction, client):
    with open('playlist.json', 'r', encoding='utf8') as pl:
        playlist = json.load(pl)
    global playing_embed
    if isinstance(playlist, list) and not playlist:
        print("PlayList is empty")
        # await ydl_embed.edit(embed=stop_embed)
    else:
        print("Play song from playlist")
        SongData = playlist.pop(0)

        writeJData(playlist)

        voice = get(client.voice_clients, guild=interaction.guild)
        voice.play(FFmpegPCMAudio(SongData["URL"], **FFMPEG_OPTIONS), after=lambda e: client.loop.create_task(Videoplay(interaction, client)))
        voice.is_playing()

        SongData['Title'] = SongData['Title'].replace('*', '\*')
        SongData['Video_url'] = SongData['Video_url'].replace('*', '\*')
        playing_embed=discord.Embed(title="好啦 就是工具貓啦 幫你播就是了" , color=0xffd700)
        playing_embed.add_field(name="播放狀態", value="播放中🐵", inline=True)
        playing_embed.add_field(name="正在播放", value=f"【***[{SongData['Title']}]({SongData['Video_url']})***】", inline=False)
        await ydl_embed.edit(embed=playing_embed)

        
async def setup(bot):
    await bot.add_cog(Play(bot))
