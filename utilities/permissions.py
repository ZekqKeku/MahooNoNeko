import functools
import nextcord
from typing import Callable, List, Any

def super_user_only(
        get_allowed_ids: Callable[[Any], List[int]],
        error_message: str = "**Permission denied!** This command is restricted to bot administrators."
):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, interaction: nextcord.Interaction, *args, **kwargs):
            allowed_users = get_allowed_ids(self)

            if interaction.user.id not in allowed_users:
                return await interaction.response.send_message(
                    error_message,
                    ephemeral=True
                )

            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator