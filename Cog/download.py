import discord
from discord.ext import commands
from discord import app_commands
import time
import json
import requests

#設定檔
ydl_wait_embed = discord.Embed(title="喵喵喵~ 請稍等一下喔~~~" , color=0xffd700)

def journal(user,event):
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S |', time.localtime())
    print(f'{nowtime} Requester: {user} | {event}')

with open('setting.json', 'r', encoding='utf8') as jfile:
    setting=json.load(jfile)
    
class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description='下載影片(音檔)')
    @app_commands.describe(url = "要下載的影片連結", audio_only = "選True只下載音檔", video_only = "選True只下載影片")
    async def download(self, interaction, url:str, audio_only:bool=False, video_only:bool=False):
        headers = {"Accept": "application/json","Content-Type": "application/json"}

        requestsData=setting["Default"]
        requestsData["url"]=url
        if audio_only==True:
            requestsData["isAudioOnly"]=True
            format="mp3"
            type="audio"
        else:
            requestsData["isAudioOnly"]=False
            format="mp4"
            type="video"

        if video_only==True:
            requestsData["isAudioMuted"]=True
        else:
            requestsData["isAudioMuted"]=False

        global vdl_embed
        await interaction.response.send_message(embed=ydl_wait_embed)
        vdl_embed = await interaction.original_response()
        if (audio_only and video_only)==True:
            embed=discord.Embed(title="你搞啥啊!" , color=0xffd700)
            embed.add_field(name="下載狀態", value="下載失敗", inline=True)
            embed.add_field(name="檔案類型", value="搞不懂", inline=True)
            embed.add_field(name="檔案格式", value="啥X啦 格", inline=True)
            embed.add_field(name="錯誤訊息", value="關聲音又關影片，你到底想怎樣嘛", inline=False)
            await vdl_embed.edit(embed=embed)
            return
        
        response = requests.post('https://co.wuk.sh/api/json', headers=headers, data=json.dumps(requestsData)).text
        response_dict = json.loads(response)
        

        if (response_dict["status"]) == "error":
            embed=discord.Embed(title="哭阿 抓不到啦" , color=0xffd700)
            embed.add_field(name="下載狀態", value="下載失敗", inline=True)
            embed.add_field(name="檔案類型", value=f"{type}", inline=True)
            embed.add_field(name="檔案格式", value=f"{format}", inline=True)
            print(response_dict["text"])
            if (response_dict["text"])=="couldn't find anything about this tweet. this could be because its visibility is limited. try another one!":
                embed.add_field(name="錯誤訊息", value="Twitter影片下載時發生錯誤，這是因為影片的檢視權限受到限制，通常是因為影片位於私人帳號中，又或者是你載的影片被Twitter判定為暴力、血腥或是瑟瑟的所以就不給載囉~~", inline=False)
            elif(response_dict["text"])=="i don't see anything i could download by your link. try a different one!":
                embed.add_field(name="錯誤訊息", value="影片下載時發生錯誤，這是因為影片的檢視權限受到限制，通常是因為你連結根本就打錯了，或是影片位於私人帳號中，又或者是你載的影片被Instagram判定為暴力、血腥或是瑟瑟的所以就不給載囉~~", inline=False)
            else:
                embed.add_field(name="錯誤訊息", value="下載時發生錯誤，請確認您輸入的網址是否正確", inline=False)
            await vdl_embed.edit(embed=embed)

        else:
            embed=discord.Embed(title="呼~好累，先睡了喔 おにゃすみ～" , color=0xffd700)
            embed.add_field(name="下載狀態", value="下載完成", inline=True)
            embed.add_field(name="檔案類型", value=f"{type}", inline=True)
            embed.add_field(name="檔案格式", value=f"{format}", inline=True)
            embed.add_field(name="檔案連結", value=response_dict["url"], inline=False)
            await vdl_embed.edit(embed=embed)
            print('\n------------------下載影片------------------')
            print(f'Video linked to "{url}" \n')
            journal(interaction.user , 'Video Download')                                   #在後台紀錄發生事件
            print('-------------------------------------------- \n')

async def setup(bot):
    await bot.add_cog(Download(bot))
