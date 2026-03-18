from nextcord.ext import commands
from utilities import baseUtils, uploader

class StartEventsCog(commands.Cog):
    def __init__(self, client, config: baseUtils.ConfigReader, pixeldrain: uploader.PixeldrainUploader):
        self.client = client
        self.config = config
        self.pixeldrain = pixeldrain

    @commands.Cog.listener()
    async def on_ready(self):
        print(" >>> Client is ready.")
        print(f" > Bot name: {self.client.user.name}")
        print(f" > Bot id: {self.client.user.id}")
        print(f" > https://discord.com/oauth2/authorize?client_id={self.client.user.id}&permissions=8&scope=bot")
        print(f" > Pixeldrain API status: {bool(self.pixeldrain)}")