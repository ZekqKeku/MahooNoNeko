import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta
from utilities import baseUtils, uploader, download, botDatabase
from utilities.cooldowns import CogSharedCooldown, cog_cooldown


class Downloader(commands.Cog):
    def __init__(self,
        client, config: baseUtils.ConfigReader,
        pixeldrain: uploader.PixeldrainUploader,
        downloader: download.Download,
        database: botDatabase.BotDatabase
    ):
        self.client = client
        self.config = config
        self.pixeldrain = pixeldrain
        self.downloader = downloader
        self.database = database

        self.cooldown_manager = CogSharedCooldown(rate=1, per=60.0)

    @nextcord.slash_command(
        name="download_music",
        description="Download a mp3 file",
    )
    @cog_cooldown(message="**Cooldown!** Next download possible in **&value&s**.")
    async def download_music(self,
    interaction: nextcord.Interaction,
    url: str = nextcord.SlashOption(
        name="url",
        description="The URL to the youtube video, instagram reels, etc.",
    )):
        await interaction.response.defer(ephemeral=True)
        file_name = baseUtils.Utils.random_name()
        ext = "mp3"

        dl_result = self.downloader.download_audio(url, file_name)
        duration = dl_result.get('duration', 0) if isinstance(dl_result, dict) else 0

        path = self.downloader.get_path(file_name=file_name, ext=ext)
        file_id = self.pixeldrain.upload_file(path)
        file_url = self.pixeldrain.get_download_link(file_id)
        self.downloader.remove_file(path)

        now = datetime.now()
        deletion_time = now + timedelta(days=self.config.get_pixeldrain_delete_after())
        self.database.add_download(
            now.strftime('%Y-%m-%d %H:%M:%S'),
            interaction.user.id,
            file_id,
            file_name,
            ext,
            duration,
            now.timestamp(),
            deletion_time.timestamp()
        )

        content = (
            "Link do pobrania twojego pliku .mp3\n"
            f"{file_url}"
        )

        await interaction.followup.send(content=content, ephemeral=True)

    @nextcord.slash_command(
        name="download_video",
        description="Download a mp4 file",
    )
    @cog_cooldown(message="**Cooldown!** Next download possible in **&value&s**.")
    async def download_video(self,
        interaction: nextcord.Interaction,
        url: str = nextcord.SlashOption(
         name="url",
         description="The URL to the youtube video, instagram reels, etc.",
        ),
        resolution: int = nextcord.SlashOption(
         name="resolution",
         description="Resolution (downloads up to source max). >1080p costs extra points.",
         required=False,
         choices={
             "480p (SD)": 480,
             "720p (HD)": 720,
             "1080p (Full HD)": 1080,
             "1440p (2K)": 1440,
             "2160p (4K)": 2160
         }
        )):
        await interaction.response.defer(ephemeral=True)
        file_name = baseUtils.Utils.random_name()
        ext = "mp4"

        dl_result = self.downloader.download_video(url, file_name=file_name, resolution=resolution)
        duration = dl_result.get('duration', 0) if isinstance(dl_result, dict) else 0

        path = self.downloader.get_path(file_name=file_name, ext=ext)
        file_id = self.pixeldrain.upload_file(path)
        if self.config.get_pixeldrain_direct_link():
            file_url = self.pixeldrain.get_download_direct_link(file_id)
        else:
            file_url = self.pixeldrain.get_download_link(file_id)
        self.downloader.remove_file(path)

        now = datetime.now()
        deletion_time = now + timedelta(days=self.config.get_pixeldrain_delete_after())
        self.database.add_download(
            now.strftime('%Y-%m-%d %H:%M:%S'),
            interaction.user.id,
            file_id,
            file_name,
            ext,
            duration,
            now.timestamp(),
            deletion_time.timestamp()
        )

        content = (
            "Link do pobrania twojego pliku .mp4\n"
            f"{file_url}"
        )

        await interaction.followup.send(content=content, ephemeral=True)