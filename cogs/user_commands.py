import nextcord
from nextcord.ext import commands

class UserCommands(commands.Cog):
    def __init__(self, client, config, database):
        self.client = client
        self.config = config
        self.database = database
        self.token_limit = self.config.get_default_token_limit()

    @nextcord.slash_command(name="tokens", description="Check your current token usage and daily limit")
    async def tokens(self, interaction: nextcord.Interaction):
        used, limit = self.database.get_tokens(interaction.user.id, self.token_limit)
        remaining = limit - used

        embed = nextcord.Embed(
            title="Token Usage Details",
            color=nextcord.Color.from_rgb(255, 255, 255)
        )
        
        embed.add_field(name="Daily Limit", value=f"**{limit}** tokens", inline=True)
        embed.add_field(name="Used Today", value=f"**{used}** tokens", inline=True)
        embed.add_field(name="Remaining", value=f"**{remaining}** tokens", inline=False)
        
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed, ephemeral=True)
