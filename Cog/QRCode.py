import discord
from discord.ext import commands
from discord import app_commands
import urllib
import segno
import time
import urllib.request

#設定檔
wait_embed = discord.Embed(title="喵喵喵~ 請稍等一下喔~~~" , color=0xffd700)

def journal(user,event):
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S |', time.localtime())
    print(f'{nowtime} Requester: {user} | {event}')
    
class QRCode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description='製作一個獨一無二的QRcode')
    @app_commands.describe(url = "要放入QRCode的內容", image_url = "要自訂的圖片或是GIF連結")
    async def create_qr(self, interaction, url:str, image_url:str=None):
        await interaction.response.send_message(embed=wait_embed)
        ydl_embed = await interaction.original_response()
        qrcode = segno.make_qr(url, error='h') #寫入內容
        type = "png"
        
        print('\n-----------------製作QRcode-----------------')
        print(f'QRcode linked to "{url}" \n')

        if image_url != None:
            try:
                if "gif" in image_url:
                    type = "gif"
                req = urllib.request.Request(image_url, headers={'User-Agent' : "User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}) 
                image_url = urllib.request.urlopen(req) #讀取圖片內容
                qrcode.to_artistic(background=image_url, target=f"ArtisticQRcode.{type}", scale=10) #為QRCode加上樣式
            except Exception:
                error_embed = discord.Embed(title="跟你說個秘密，你的圖片好像怪怪的欸，我怎麼抓都抓不到捏!" , color=0xffd700)
                await ydl_embed.edit(embed=error_embed)
                print("QRcode Creat Failed")
                print('-------------------------------------------- \n')
                return
        else:
            qrcode.save("ArtisticQRcode.png", scale=10)

        qrChannel = str(interaction.channel)
        if(not qrChannel.startswith("Direct Message with")):
            await interaction.channel.purge(limit=1)
        else:
            done_embed = discord.Embed(title="耶! QRCode做好了にゃ~ " , color=0xffd700)
            await ydl_embed.edit(embed=done_embed)
        await interaction.channel.send(file=discord.File(f"ArtisticQRcode.{type}"))

        journal(interaction.user, f'Create a QRcode')       #在後台紀錄發生事件
        print('-------------------------------------------- \n')

async def setup(bot):
    await bot.add_cog(QRCode(bot))