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

    async def send_error_message(self, interaction, error_message, type, format):
        embed = discord.Embed(title="哭阿 抓不到啦", color=0xffd700)
        embed.add_field(name="下載狀態", value="下載失敗", inline=True)
        embed.add_field(name="檔案類型", value=type, inline=True)
        embed.add_field(name="檔案格式", value=format, inline=True)
        embed.add_field(name="錯誤訊息", value=error_message, inline=False)
        await interaction.edit_original_response(embed=embed)

    @app_commands.command(description='下載影片(音檔)')
    @app_commands.describe(url = "要下載的影片連結", audio_only = "選True只下載音檔", video_only = "選True只下載影片")
    async def download(self, interaction, url:str, audio_only:bool=False, video_only:bool=False):
        
        requestsData=setting["Default"].copy()
        requestsData["url"]=url
        format = "mp4"
        type = "video"

        if audio_only:
            format = "mp3"
            type = "audio"
            requestsData["downloadMode"] = "audio"
        elif video_only:
            requestsData["downloadMode"] = "mute"

        if audio_only and video_only:
            embed = discord.Embed(title="你搞啥啊!", color=0xffd700)
            embed.add_field(name="下載狀態", value="下載失敗", inline=True)
            embed.add_field(name="檔案類型", value="搞不懂", inline=True)
            embed.add_field(name="檔案格式", value="啥X啦 格", inline=True)
            embed.add_field(name="錯誤訊息", value="關聲音又關影片，你到底想怎樣嘛", inline=False)
            await interaction.response.send_message(embed=embed)
            return
        
        await interaction.response.send_message(embed=ydl_wait_embed)

        try:
            response = requests.post('https://meow.akkkou.com/', headers=setting["headers"], data=json.dumps(requestsData))
            response_dict = response.json()

            if response_dict["status"] == "error":
                error_map = {
                    "error.api.link.unsupported": "不支援的服務",
                    "error.api.link.invalid": "無效的網址",
                    "error.api.invalid_body": "無效的網址",
                    "error.api.content.post.age": "影像設有年齡限制",
                    "error.api.content.too_long": "影片過長(限制180分鐘)",
                    "error.api.content.video.unavailable": "無法取得影片",
                    "unknownError": "未知的錯誤"
                }
                error_message = error_map.get(response_dict["error"], "喵喵喵! 下載時發生錯誤，請確認您輸入的網址是否正確並再試一次")
                await self.send_error_message(interaction, error_message, type, format)

            else:
                embed = discord.Embed(title="呼~好累，先睡了喔 おにゃすみ～", color=0xffd700)
                embed.add_field(name="下載狀態", value="下載完成", inline=True)
                embed.add_field(name="檔案類型", value=type, inline=True)
                embed.add_field(name="檔案格式", value=format, inline=True)
                embed.add_field(name="檔案連結", value=f"[{response_dict['filename']}]({response_dict['url']})", inline=False)
                await interaction.edit_original_response(embed=embed)

                print('\n------------------下載影片------------------')
                print(f'Video linked to "{url}" \n')
                journal(interaction.user, 'Video Download')
                print('-------------------------------------------- \n')

        except requests.exceptions.RequestException as e:
            await self.send_error_message(interaction, "請求發生錯誤，無法連線至伺服器", type, format)

async def setup(bot):
    await bot.add_cog(Download(bot))