# MahooNoNeko - Media Downloader Discord Bot

MahooNoNeko is a feature-rich Discord bot built with Python and Nextcord. It allows users to download videos and audio from various platforms (like YouTube, TikTok, Instagram, etc.) directly through Discord. To bypass Discord's file size limits, the bot utilizes `yt-dlp` for downloading and seamlessly uploads the media to Pixeldrain. 

Links are provided to the user, and the bot automatically cleans up the hosted files after a specified number of days to save space. It also features a built-in SQLite database for tracking downloads and managing quotas.

## ✨ Features

* **High-Quality Downloads**: Fetches the best available audio and video qualities using `yt-dlp`.
* **Multiple Formats & Resolutions**: Supports extracting audio (MP3) or downloading full videos (MP4) with selectable resolutions from 480p up to 2160p (4K).
* **Bypass Size Limits**: Automatically uploads downloaded files to Pixeldrain and returns a convenient download link.
* **Auto-Cleanup & Archiving**: Files are automatically monitored and removed from the database after `X` days to ensure privacy and optimize storage.
* **Modern Async Framework**: Built on top of `nextcord` for fast and asynchronous Discord API interactions.
* **Cooldown & Quota Management**: Built-in rate limits to prevent spamming. Super users defined in the config can bypass these restrictions.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your machine:
* **Python 3.14+**
* **FFmpeg**: Required by `yt-dlp` for extracting audio and merging video/audio tracks.
* **Discord Bot Token**: You can get this from the Discord Developer Portal.
* **Pixeldrain API Key**: Required for uploading files to Pixeldrain.

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ZekqKeku/MahooNoNeko.git
   cd MahooNoNeko
   
2. **Install requirements**\
The bot attempts to automatically install requirements on launch, but you can also install them manually:
    ```bash
    pip install -r requirements.txt
   
3. **Configure the bot**\
Edit the config.json file in the root directory with your credentials:
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
          "delete_after": 3,
          "max_file_size": 2,
          "max_file_length": 5400
        }
      }
    }
   ```
   - **super_users** - soon
   - **direct_link** - requires Pixeldrain premium, changes the format of the links returned by the bot
   - **delete_after** - informs the Pixeldrain API after how many days to delete the file; please note that on the free plan, Pixeldrain automatically deletes files after 60 days of inactivity (when they are not viewed or downloaded)
   - **max_file_size** - gigabajty, gigabytes, the maximum size of the file the user wants to download; Pixeldrain's free plan allows a max of 10
   - **max_file_length** - seconds, the maximum length of the downloaded media

_(Note: The configuration file structure is subject to significant changes. Also, please keep in mind that during development, some options might not yet affect the bot's operation)_

4. **Run the bot**
    ```bash
    python main.py
    ```
   (Note: This method is temporary, the bot will eventually run in Docker)

## 📜 Commands
* `/download_music [url]` - Downloads media from the provided URL, extracts the audio, and returns a Pixeldrain link to the `.mp3` file.
* `/download_video [url] [resolution]` - Downloads media from the provided URL as an `.mp4` video. You can optionally select the maximum resolution (from 480p up to 2160p).