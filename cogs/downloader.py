import nextcord
from nextcord.ext import commands

from utilities import baseUtils, uploader, download

class Downloader(commands.Cog):
    def __init__(self, client, config: baseUtils.ConfigReader, pixeldrain: uploader.PixeldrainUploader, downloader: download.Download):
        self.client = client
        self.config = config
        self.pixeldrain = pixeldrain
        self.downloader = downloader

    @nextcord.slash_command(
        name="download_music",
        description="Download a mp3 file",
    )
    async def download_music(self,
        interaction: nextcord.Interaction,
        url: str = nextcord.SlashOption(
            name = "url",
            description = "The URL to the youtube video, instagram reels, etc.",
        )
    ):
        await interaction.response.defer(ephemeral=True)
        file_name = baseUtils.Utils.random_name()

        self.downloader.download_audio(url, file_name)
        path = self.downloader.get_path(file_name=file_name, ext="mp3")
        file_id = self.pixeldrain.upload_file(path)
        file_url = self.pixeldrain.get_download_link(file_id)
        self.downloader.remove_file(path)

        content = (
            "Link do pobrania twojego pliku .mp3\n"
            f"{file_url}"
        )

        await interaction.followup.send(content=content, ephemeral=True)

    @nextcord.slash_command(
        name="download_video",
        description="Download a mp4 file",
    )
    async def download_video(self,
        interaction: nextcord.Interaction,
        url: str = nextcord.SlashOption(
            name = "url",
            description = "The URL to the youtube video, instagram reels, etc.",
        )
    ):
        await interaction.response.defer(ephemeral=True)
        file_name = baseUtils.Utils.random_name()

        self.downloader.download_video(url, file_name)
        path = self.downloader.get_path(file_name=file_name, ext="mp4")
        file_id = self.pixeldrain.upload_file(path)
        if self.config.get_pixeldrain_direct_link():
            file_url = self.pixeldrain.get_download_direct_link(file_id)
        else:
            file_url = self.pixeldrain.get_download_link(file_id)
        self.downloader.remove_file(path)

        content = (
            "Link do pobrania twojego pliku .mp4\n"
            f"{file_url}"
        )

        await interaction.followup.send(content=content, ephemeral=True)

