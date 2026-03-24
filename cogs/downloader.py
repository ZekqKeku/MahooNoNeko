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

        self.token_limit = 350

        self.cooldown_manager = CogSharedCooldown(rate=1, per=60.0)

    async def _handle_media_error(self, interaction: nextcord.Interaction, media_info: dict):
        error_type = media_info.get("error")
        if error_type == "live_stream":
            await interaction.followup.send(
                "**Error:** This link points to a live stream, which cannot be downloaded.",
                 ephemeral=True)
        elif error_type == "too_long":
            await interaction.followup.send(
                f"**Error:** The file is too long. It lasts **{media_info['duration']}s**, but the allowed limit is **{media_info['max_length']}s**.",
                ephemeral=True)
        elif error_type == "too_heavy":
            await interaction.followup.send(
                f"**Error:** The file is too large. The estimated size is **{media_info['filesize_gb']} GB**, but the limit is **{media_info['max_size_gb']} GB**.",
                ephemeral=True)
        else:
            await interaction.followup.send(
                "**Error:** Failed to fetch file information from the provided link.",
                 ephemeral=True)

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

        max_length = self.config.get_pixeldrain_max_file_length()
        max_size_gb = self.config.get_pixeldrain_max_file_size()

        media_info = self.downloader.verify_media(
            url=url,
            max_length=max_length,
            max_size_gb=max_size_gb,
            audio_format="mp3",
            is_audio=True
        )

        if not media_info["success"]:
            await self._handle_media_error(interaction, media_info)
            return

        cost = media_info["cost"]
        if not self.database.can_use_tokens(interaction.user.id, cost, self.token_limit):
            await interaction.followup.send(
                f"**Insufficient tokens.** This operation costs **{cost} points**, which would exceed your daily limit.",
                ephemeral=True)
            return

        file_name = baseUtils.Utils.random_name()
        ext = "mp3"

        dl_result = self.downloader.download_audio(url, file_name)

        if not dl_result or (isinstance(dl_result, dict) and not dl_result.get('success')):
            await interaction.followup.send(
                "**Error:** An issue occurred while downloading and processing the audio file.", ephemeral=True)
            return

        duration = media_info.get("duration", 0)

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

        self.database.add_tokens(interaction.user.id, cost)

        content = (
            f"**Success.** Below is the download link for your .mp3 file.\n"
            f"Operation cost: **{cost} points**\n\n"
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

        max_length = self.config.get_pixeldrain_max_file_length()
        max_size_gb = self.config.get_pixeldrain_max_file_size()

        media_info = self.downloader.verify_media(
            url=url,
            max_length=max_length,
            max_size_gb=max_size_gb,
            resolution=resolution,
            is_audio=False
        )

        if not media_info["success"]:
            await self._handle_media_error(interaction, media_info)
            return

        cost = media_info["cost"]
        if not self.database.can_use_tokens(interaction.user.id, cost, self.token_limit):
            await interaction.followup.send(
                f"**Insufficient tokens.** This operation costs **{cost} points**, which would exceed your daily limit.",
                ephemeral=True)
            return

        file_name = baseUtils.Utils.random_name()
        ext = "mp4"

        dl_result = self.downloader.download_video(url, file_name=file_name, resolution=resolution)

        if not dl_result or (isinstance(dl_result, dict) and not dl_result.get('success')):
            await interaction.followup.send(
                "**Error:** An issue occurred while downloading and processing the video file.", ephemeral=True)
            return

        duration = media_info.get("duration", 0)

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

        self.database.add_tokens(interaction.user.id, cost)

        content = (
            f"**Success.** Below is the download link for your .mp4 file.\n"
            f"Operation cost: **{cost} tokens**\n\n"
            f"{file_url}"
        )

        await interaction.followup.send(content=content, ephemeral=True)