import time
import asyncio
from nextcord.ext import commands, tasks
from utilities import baseUtils, uploader, botDatabase

class ClearEvent(commands.Cog):
    def __init__(self,
        client,
        config: baseUtils.ConfigReader,
        pixeldrain: uploader.PixeldrainUploader,
        database: botDatabase.BotDatabase
    ):
        self.client = client
        self.config = config
        self.pixeldrain = pixeldrain
        self.database = database

        self.monitor_expired_files.start()

    def cog_unload(self):
        if self.monitor_expired_files.is_running():
            self.monitor_expired_files.cancel()

    @tasks.loop(hours=6)
    async def monitor_expired_files(self):
        current_timestamp = time.time()

        expired_files = self.database.get_expired_downloads(current_timestamp)

        if not expired_files:
            return

        for db_id, pixeldrain_id in expired_files.items():
            try:
                file_exists = await asyncio.to_thread(self.pixeldrain.check_file_exists, pixeldrain_id)

                if not file_exists:
                    self.database.move_to_archive(db_id)
                    print(f"[ClearEvent] File {pixeldrain_id} is no longer on Pixeldrain. Archived (DB ID: {db_id})")
                else:
                    print(f"[ClearEvent] {pixeldrain_id} still exists on API side. Waiting for Pixeldrain to clean it.")

            except Exception as e:
                print(f"[ClearEvent] Error while processing {pixeldrain_id}: {e}")

    @monitor_expired_files.before_loop
    async def before_monitor_expired_files(self):
        await self.client.wait_until_ready()

def setup(client, config, pixeldrain, database):
    client.add_cog(ClearEvent(client, config, pixeldrain, database))