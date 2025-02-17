import discord
from discord import app_commands
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get
from discord.ui import Button, View
import asyncio
from yt_dlp import YoutubeDL
import time
import json
import random

#設定檔
ydl_wait_embed = discord.Embed(title="喵喵喵~ 請稍等一下喔~~~" , color=0xffd700)
ydl_embed = ydl_wait_embed
playing_embed = discord.Embed(title="好啦 就是工具貓啦 幫你播就是了" , color=0xffd700)
pause_embed=discord.Embed(title="播了又要暫停 你真的是麻煩大王欸" , color=0xffd700)
embed_server = None
bot_at = 'None'
ftp=0
YDL_OPTIONS = {'format': 'm4a/bestaudio/best', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

with open('setting.json', 'r', encoding='utf8') as jsonFile:
    setting = json.load(jsonFile)

def journal(user, event):
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S |', time.localtime())
    print(f'{nowtime} Requester: {user} | {event}')

def openJData():
    with open('playlist.json', 'r', encoding='utf8') as pl:
        Playlist = json.load(pl)
    return Playlist

def writeJData(Data):
    with open('playlist.json', 'w', encoding='utf-8') as file:
        json.dump(Data, file, indent=4, ensure_ascii=False)

def setPlayingEmbed(title, url):
    playing_embed=discord.Embed(title="好啦 就是工具貓啦 幫你播就是了" , color=0xffd700)
    playing_embed.add_field(name="播放狀態", value="播放中🐵", inline=True)
    playing_embed.add_field(name="正在播放", value=f"【***[{title}]({url})***】", inline=False)
    return playing_embed

def setPauseEmbed(title, url):
    pause_embed=discord.Embed(title="播了又要暫停 你真的是麻煩大王欸" , color=0xffd700)
    pause_embed.add_field(name="播放狀態", value="暫停中🙊", inline=True)
    pause_embed.add_field(name="正在播放", value=f"【***[{title}]({url})***】", inline=False)
    return pause_embed



class MusicControlView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def process_action(self, interaction: discord.Interaction, action: str):
        """處理按鈕點擊事件"""
        global ydl_embed, playing_embed, pause_embed

        if action == "繼續播放":
            ErrorCode = await resume(interaction, self.bot)
            if ErrorCode == 0:
                await ydl_embed.edit(embed=playing_embed)
                await interaction.response.defer()
            elif ErrorCode == 1:
                await interaction.response.send_message("你還沒播放任何東西呢", ephemeral=True)
            elif ErrorCode == 2:
                await interaction.response.send_message("已經在播放了喔 沒聽見的話可能要檢查耳朵了(´･_･`)", ephemeral=True)
            elif ErrorCode == 3:
                await interaction.response.send_message("不是 我連房間都沒進去，你是想要我繼續播甚麼?", ephemeral=True)

        elif action == "暫停播放":
            ErrorCode = await pause(interaction, self.bot)
            if ErrorCode == 0:
                await ydl_embed.edit(embed=pause_embed)
                await interaction.response.defer()
            elif ErrorCode == 1:
                await interaction.response.send_message("現在沒有在播放喔", ephemeral=True)
            elif ErrorCode == 3:
                await interaction.response.send_message("不是 我連房間都沒進去，你是想要我暫停甚麼?", ephemeral=True)

        elif action == "跳下一首":
            ErrorCode = await next(interaction, self.bot)
            if ErrorCode == 0:
                await interaction.response.defer()
            elif ErrorCode == 1:
                await interaction.response.send_message("現在沒有在播放喔", ephemeral=True)
            elif ErrorCode == 3:
                await interaction.response.send_message("不是 我連房間都沒進去，你是怎麼樣才會覺得我生得出下一首歌?", ephemeral=True)
            elif ErrorCode == 4:
                await interaction.response.send_message("已經沒有下一首歌了喵", ephemeral=True)

    @discord.ui.button(label="繼續播放", emoji="▶", style=discord.ButtonStyle.green, custom_id="continue")
    async def continue_button(self, interaction: discord.Interaction, button: Button):
        await self.process_action(interaction, "繼續播放")

    @discord.ui.button(label="暫停播放", emoji="⏸", style=discord.ButtonStyle.blurple, custom_id="pause")
    async def pause_button(self, interaction: discord.Interaction, button: Button):
        await self.process_action(interaction, "暫停播放")

    @discord.ui.button(label="跳下一首", emoji="⏩", style=discord.ButtonStyle.red, custom_id="skip")
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        await self.process_action(interaction, "跳下一首")



class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.bot.tree.on_error = on_tree_error

    @app_commands.command(description='播放')
    @app_commands.describe(search = "直接輸入要播放的歌名，或是輸入YT影片連結，或YT Music歌曲連結")
    @app_commands.describe(interrupting = "選擇True立即插播歌曲")
    async def play(self, interaction, search:str, interrupting:bool=False):

        view = MusicControlView(self.bot)
        Mode = 0
        if "youtube.com" in search or "youtu.be" in search:
            Mode = 1

        voice = get(self.bot.voice_clients, guild=interaction.guild)                #取得Bot所在頻道
            
        if voice == None:                                                           #如果Bot不在語音頻道中就加入指令請求者所在之頻道
            try:                                                                    #try是為了偵測指令請求者是否在語音頻道中
                channel = interaction.user.voice.channel
            
                await channel.connect()
                global bot_at
                bot_at = channel                                                    #紀錄Bot連接到哪個語音頻道
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
                if voice.is_playing() or voice.is_paused():
                    requester = interaction.user.voice.channel
                    if requester != bot_at:                                             #如果指令請求者和Bot不在同一個語音頻道
                        await interaction.response.send_message('請不要嘗試在別人的房間放聲音')
                        return

            except Exception:                                                       #如果指令請求者不在語音頻道中，發送提示
                await interaction.response.send_message('你有在頻道裡嗎?')
                return

        try:                                                                        #偵測擷取音訊時是否發生錯誤
            global ydl_embed, playing_embed, pause_embed, ftp, embed_server
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
            
            if voice.is_playing() or voice.is_paused():
                playlist = openJData()

                new_item = {
                    "Title": f"{video_title}",
                    "Video_url": f"{video_url}",
                    "URL": f"{URL}"
                }

                if interrupting:
                    playlist.insert(0, new_item)
                    writeJData(playlist)
                    await next(interaction, self.bot)
                    await interaction.followup.send("照你要求的播了喵")
                    journal(interaction.user, 'Bro interrupting the song')
                else:
                    playlist.append(new_item)
                    writeJData(playlist)
                    await interaction.followup.send(f"已將歌曲加入至播放清單!```fix\n{video_title}```\n使用**/playlist**查看待播歌曲!")
                    journal(interaction.user, 'Join Video To Playlist')

            else:
                voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: self.bot.loop.create_task(Videoplay(interaction, self.bot, view)))
                voice.is_playing()

                playing_embed=setPlayingEmbed(video_title, video_url)
                pause_embed=setPauseEmbed(video_title, video_url)

                if ftp==0:
                    await ydl_embed.edit(embed=playing_embed, view=view)
                    ftp=1
                else:
                    if embed_server != interaction.guild:
                        ydl_embed = await interaction.channel.send(embed=playing_embed, view=view)
                    else:
                        try:
                            await ydl_embed.edit(embed=playing_embed)
                        except Exception as e:
                            ydl_embed = await interaction.channel.send(embed=playing_embed, view=view)
                            print("send view from play | ftp=1,except")
                    await interaction.followup.send("照你要求的播了喵")

                embed_server = interaction.guild
                journal(interaction.user, 'Play video')
            
        except Exception as e:                                                      #按發生錯誤之類型提示使用方式
            print('捕捉錯誤資訊: '+ str(e))
            print('-------------------------------------------- \n')

            if(str(e) == "Not connected to voice."):
                channel = interaction.user.voice.channel
                await channel.connect()
                
            if ftp == 0:
                error_embed = discord.Embed(title="出錯了喵 檢查一下連結是否正確吧!" , color=0xffd700)
                await ydl_embed.edit(embed = error_embed)
            else:
                try:
                    await interaction.followup.send('你輸入的連結有誤(可能是輸入成Youtube外或是搜尋頁面的連結)，請重新輸入正確的「影片連結」')
                
                except Exception:
                    await interaction.response.send_message('你輸入的連結有誤(可能是輸入成Youtube外或是搜尋頁面的連結)，請重新輸入正確的「影片連結」')
        
    @app_commands.command(description='查看播放清單、移除歌曲、插播清單中歌曲')
    @app_commands.describe(delete = "選擇要刪除的歌曲")
    @app_commands.describe(interrupting = "選擇要插播的歌曲")
    async def playlist(self, interaction, delete:str=None, interrupting:str=None):
        await interaction.response.defer()
        playlist = openJData()

        PL_embed = discord.Embed(title="目前待播歌曲!" , color=0xffd700)

        if isinstance(playlist, list) and not playlist:
            PL_embed = discord.Embed(title="清單就像本喵的餐盤一樣空空的喔" , color=0xffd700)
            PL_embed.add_field(name="餐盤實況 ↓", value="🍽️🍃...", inline=True)

        elif interrupting != None:
            index = await matchPlaylist(interaction, playlist, interrupting)
            if index == "bad":
                return 
            cutSong = playlist.pop(index)
            playlist.insert(0, cutSong)
            writeJData(playlist)
            await next(interaction, self.bot)
            await interaction.followup.send("切切切切切成功!")
            return
            
        elif delete != None:
            index = await matchPlaylist(interaction, playlist, delete)
            if index == "bad":
                return
            playlist.pop(index)
            writeJData(playlist)
            PL_embed = discord.Embed(title="刪除成功! 目前待播歌曲" , color=0xffd700)
            if isinstance(playlist, list) and not playlist:
                msg = ["\n我們的感情就像這個歌單一樣 沒有任何聯繫 渣男😾","\n放棄本來就會遺憾 但有些事堅持本就沒什麼意義 一定要擁有嗎 或許失去更輕鬆嘛 你先快樂 我的事以後再說😼"]
                PL_embed.add_field(name="被你刪光了", value=f"{msg[random.randint(0,1)]}", inline=True)
                await interaction.followup.send(embed=PL_embed)
                return
        
        Number = 1
        for song in playlist:
            if Number==25:
                PL_embed.add_field(name=f"以及剩下的{len(playlist)-24}首歌曲...", value=f"", inline=False)
                break
            PL_embed.add_field(name=f"下 {Number} 首播放歌曲", value=f"***[{song['Title']}]({song['Video_url']})***", inline=False)
            Number += 1

        await interaction.followup.send(embed=PL_embed)

    @playlist.autocomplete("delete")
    @playlist.autocomplete("interrupting")
    async def text_autocomplete(self, interaction, current:str):
        # 根據用戶輸入進行模糊搜尋（不區分大小寫）
        playlist = openJData()
        matching_options = [option["Title"] for option in playlist if current.lower() in option["Title"].lower()]
        # 返回最多 25 個結果
        return [discord.app_commands.Choice(name=option, value=option) for option in matching_options[:25]]

async def matchPlaylist(interaction, playlist, text):
    matching_options = [option["Title"] for option in playlist if text.lower() in option["Title"].lower()]
    
    if text not in matching_options:
        await interaction.followup.send("喵喵 我找不到這首歌")
        return "bad"
    
    target_title = text
    for i, item in enumerate(playlist):
        if item["Title"] == target_title:
            return i

async def pause(interaction, client):
    try:                                                                        #try是為了偵測Bot是否在語音頻道中
        voice = get(client.voice_clients, guild=interaction.guild)
        if voice.is_playing():
            voice.pause()
            return 0
        else:
            return 1

    except Exception as e:
        print('捕捉錯誤資訊: '+ str(e))
        return 3

async def resume(interaction, client):
    try:
        voice = get(client.voice_clients, guild=interaction.guild)

        if voice.is_paused():
            voice.resume()
            return 0

        elif voice.is_playing():
            return 2
        else:
            return 1
        
    except Exception as e:
        print('捕捉錯誤資訊: '+ str(e))
        return 3

async def next(interaction, client):
    try:
        voice = get(client.voice_clients, guild=interaction.guild)
        playlist = openJData()

        if isinstance(playlist, list) and not playlist:
            return 4
        else:
            voice.stop()
            return 0
        
    except Exception as e:
        print('捕捉錯誤資訊: '+ str(e))
        return 3

async def Videoplay(interaction, client, view):
    playlist = openJData()
    global playing_embed, pause_embed, ydl_embed
    if isinstance(playlist, list) and not playlist:
        print("PlayList is empty\n")
    else:
        SongData = playlist.pop(0)

        writeJData(playlist)

        voice = get(client.voice_clients, guild=interaction.guild)
        voice.play(FFmpegPCMAudio(SongData["URL"], **FFMPEG_OPTIONS), after=lambda e: client.loop.create_task(Videoplay(interaction, client, view)))
        voice.is_playing()

        SongData['Title'] = SongData['Title'].replace('*', '\*')
        SongData['Video_url'] = SongData['Video_url'].replace('*', '\*')

        playing_embed=setPlayingEmbed(SongData['Title'], SongData['Video_url'])
        pause_embed=setPauseEmbed(SongData['Title'], SongData['Video_url'])

        try:
            await ydl_embed.edit(embed=playing_embed)
        except Exception as e:
            ydl_embed = await interaction.channel.send(embed=playing_embed, view=view)
        
async def on_tree_error(interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown): 
        return await interaction.response.send_message(f"Command is currently on cooldown! Try again in **{error.retry_after:.2f}** seconds!")
    elif isinstance(error, app_commands.MissingPermissions):
        return await interaction.response.send_message(f"You're missing permissions to use that")
    else:
        raise error

async def setup(bot):
    await bot.add_cog(Play(bot))