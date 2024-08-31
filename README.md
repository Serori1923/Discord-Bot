# Discord-Bot
***為了使伺服器變得更加歡樂及便利而存在***

## 支持的功能
| 管理員 | 使用者 |
| ----- | ----- |
| 封禁伺服器成員(Ban、Unban) | 製作QRCode |
| 踢出伺服器成員(Kick) | 播放音樂 |
| 清除頻道訊息 | 下載知名影音平台影片 |

下載影片支援平台請參考[cobalt套件](https://github.com/imputnet/cobalt)說明

## 安裝方式
### 安裝依賴套件
```bash
pip install -r requirements.txt
```

播放功能需使用[ffmpeg](https://ffmpeg.org/download.html)套件
Windows用戶請至官網下載，並設定環境變數

Linux用戶執行以下指令即可
```bash
sudo apt install ffmpeg
```

## 依賴套件
### [segno](https://github.com/heuer/segno)
此套件為製作QRcode的功能提供支持，感謝原開發者的貢獻!
### [yt-dlp](https://github.com/yt-dlp/yt-dlp)
此套件為音樂播放功能提供支持，感謝原開發者的貢獻!
### [ffmpeg](https://ffmpeg.org/)
此套件為音樂播放功能提供支持，感謝原開發者的貢獻!
### [cobalt](https://github.com/imputnet/cobalt)
此套件為下載影片功能提供支持，感謝原開發者的貢獻!
