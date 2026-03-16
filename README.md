# MahooNoNeko - Media Downloader Discord Bot

MahooNoNeko is a feature-rich Discord bot built with Python and Nextcord. It allows users to download videos and audio from various platforms (like YouTube, TikTok, etc.) directly through Discord. To bypass Discord's file size limits, the bot utilizes `yt-dlp` for downloading and seamlessly uploads the media to Pixeldrain. 

Links are provided to the user, and the bot automatically cleans up the hosted files after a specified number of days to save space.

## ✨ Features

* **High-Quality Downloads**: Fetches the best available audio and video qualities using `yt-dlp`.
* **Multiple Formats**: Supports extracting audio (e.g., MP3) or downloading full videos (MP4).
* **Bypass Size Limits**: Automatically uploads downloaded files to Pixeldrain and returns a convenient download link.
* **Auto-Cleanup**: Files are automatically removed after `X` days to ensure privacy and optimize storage.
* **Modern Async Framework**: Built on top of `nextcord` for fast and asynchronous Discord API interactions.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your machine:
* **Python 3.14+**
* **FFmpeg**: Required by `yt-dlp` for extracting audio and merging video/audio tracks.
* **Discord Bot Token**: You can get this from the Discord Developer Portal.
* **Pixeldrain API Key**: Required for uploading files to Pixeldrain.

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   https://github.com/ZekqKeku/MahooNoNeko.git
   cd MahooNoNeko
