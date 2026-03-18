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

        if self.config.get_pixeldrain_auto_clear():
            self.clear_expired_files.start()

    def cog_unload(self):
        if self.clear_expired_files.is_running():
            self.clear_expired_files.cancel()

    @tasks.loop(hours=6)
    async def clear_expired_files(self):
        current_timestamp = time.time()

        expired_files = self.database.get_expired_downloads(current_timestamp)

        if not expired_files:
            return

        for db_id, pixeldrain_id in expired_files.items():
            try:
                success = await asyncio.to_thread(self.pixeldrain.delete_file, pixeldrain_id)

                if success:
                    self.database.move_to_archive(db_id)
                    print(f"[ClearEvent] Deleted and archived: {pixeldrain_id} (DB ID: {db_id})")
                else:
                    print(f"[ClearEvent] Failed to delete {pixeldrain_id} from Pixeldrain. Kept in main DB.")

            except Exception as e:
                print(f"[ClearEvent] Error while processing {pixeldrain_id}: {e}")

    @clear_expired_files.before_loop
    async def before_clear_expired_files(self):
        await self.client.wait_until_ready()


def setup(client, config, pixeldrain, database):
    client.add_cog(ClearEvent(client, config, pixeldrain, database))