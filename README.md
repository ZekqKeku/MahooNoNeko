# MahooNoNeko - Media Downloader Discord Bot

MahooNoNeko is a feature-rich Discord bot built with Python and Nextcord. It allows users to download videos and audio from various platforms (like YouTube, TikTok, Instagram, etc.) directly through Discord. To bypass Discord's file size limits, the bot utilizes `yt-dlp` for downloading and seamlessly uploads the media to Pixeldrain. 

Links are provided to the user, and the bot records every download in a built-in SQLite database for tracking and managing quotas.

## ✨ Features

* **High-Quality Downloads**: Fetches the best available audio and video qualities using `yt-dlp`.
* **Multiple Formats & Resolutions**: Supports extracting audio (MP3) or downloading full videos (MP4) with selectable resolutions from 480p up to 2160p (4K).
* **Bypass Size Limits**: Automatically uploads downloaded files to Pixeldrain and returns a convenient download link.
* **Modern Async Framework**: Built on top of `nextcord` for fast and asynchronous Discord API interactions.
* **Cooldown & Quota Management**: Built-in rate limits to prevent spamming. Super users defined in the config can bypass these restrictions.

## 🪙 Token System (Quota)

To prevent abuse and manage server resources, the bot implements a daily token-based quota system for users. Each user receives a daily allowance of tokens (defined by `default_token_limit`), which resets every day at midnight. 

The cost of each download is calculated dynamically before the download begins:
* **Base cost**: 10 points per operation
* **Duration**: 2 points per every minute of the media
* **Quality/Format multiplier**: Additional points are added for higher resolutions (e.g., 1440p costs +100 points, 4K costs +150 points) or lossless audio formats.

If an operation exceeds the user's remaining daily tokens, the download request will be rejected.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
* **Docker** and **Docker Compose** (Recommended)
* OR **Python 3.11+** and **FFmpeg** (For manual setup)
* **Discord Bot Token**: From the [Discord Developer Portal](https://discord.com/developers/applications).
* **Pixeldrain API Key**: From your [Pixeldrain account](https://pixeldrain.com/api).

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ZekqKeku/MahooNoNeko.git
   cd MahooNoNeko
   ```

2. **Configure the bot**
   Rename or edit `config.json` with your credentials:
   ```json
   {
     "bot": {
       "token": "YOUR_DISCORD_BOT_TOKEN_HERE"
     },
     "discord": {
       "super_users": [
         "YOUR_DISCORD_USER_ID"
       ]
     },
     "api": {
       "pixeldrain": {
         "key": "YOUR_PIXELDRAIN_API_KEY",
         "direct_link": false,
         "max_file_size": 2,
         "max_file_length": 5400,
         "default_token_limit": 350
       }
     }
   }
   ```
   - **direct_link**: Requires Pixeldrain premium; changes link format.
   - **max_file_size**: (GB) Maximum allowed file size for download.
   - **max_file_length**: (Seconds) Maximum duration of the media.
   - **default_token_limit**: Daily points allowance for regular users.

### Option A: Run with Docker (Recommended)
The easiest way to run the bot is using Docker Compose. It automatically handles FFmpeg and all dependencies.

```bash
docker-compose up -d
```

### Option B: Manual Setup
1. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```
2. **Ensure FFmpeg is installed** on your system.
3. **Run the bot**
   ```bash
   python main.py
   ```

## 📜 Commands
* `/download_music [url]` - Downloads media from the provided URL, extracts the audio, and returns a Pixeldrain link to the `.mp3` file.
* `/download_video [url] [resolution]` - Downloads media from the provided URL as an `.mp4` video. You can optionally select the maximum resolution (from 480p up to 2160p).
