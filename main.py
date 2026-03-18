from utilities import baseUtils
baseUtils.Requirements()

try:
    from utilities import uploader, download
    from nextcord.ext import commands
    import nextcord
except:
    raise RuntimeError('\n > Failed to load libraries!\n')

def main():
    config = baseUtils.ConfigReader('config.json')
    pixeldrain = uploader.PixeldrainUploader(config.get_pixeldrain_api())
    downloader = download.Download('downloads')

    intents = nextcord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.messages = True
    intents.members = True
    intents.guilds = True

    client = commands.Bot(intents=intents)

    payload = {
        'client': client,
        'config': config,
        'pixeldrain': pixeldrain,
        'downloader': downloader,
    }

    baseUtils.Loader(payload)

    client.run(config.get_bot_token())

if __name__ == "__main__":
    main()