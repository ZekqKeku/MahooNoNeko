import time
import functools
import nextcord

class CogSharedCooldown:
    def __init__(self, rate: int, per: float):
        self.rate = rate
        self.per = per
        self._buckets = {}

    def get_retry_after(self, user_id: int):
        now = time.time()
        if user_id not in self._buckets:
            self._buckets[user_id] = now
            return None

        elapsed = now - self._buckets[user_id]
        if elapsed >= self.per:
            self._buckets[user_id] = now
            return None

        return self.per - elapsed

def cog_cooldown(message: str = "**Cooldown!** Next use possible in **&value&s**."):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, interaction: nextcord.Interaction, *args, **kwargs):
            raw_super_users = self.config.get_super_users()
            super_users = [int(u) for u in raw_super_users if str(u).isdigit()]

            if interaction.user.id in super_users:
                return await func(self, interaction, *args, **kwargs)

            manager = getattr(self, "cooldown_manager", None)
            if not manager:
                return await func(self, interaction, *args, **kwargs)

            retry_after = manager.get_retry_after(interaction.user.id)

            if retry_after:
                parsed_message = message.replace("&value&", f"{retry_after:.1f}")

                return await interaction.response.send_message(
                    parsed_message,
                    ephemeral=True
                )

            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator