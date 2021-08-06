""" Application Settings (.env loading) """
from decouple import config

DEBUG = bool(config("DEBUG", default=True, cast=bool))

# This is only required if DEBUG is True.
# Commands will be added to only this guild
TEST_SERVER_ID = str(config("TEST_SERVER_ID", default="", cast=str))

BOT_TOKEN = str(config("BOT_TOKEN", cast=str))
APPLICATION_ID = str(config("APPLICATION_ID", cast=str))
APPLICATION_PUBLIC_KEY = str(config("APPLICATION_PUBLIC_KEY", cast=str))
CLIENT_ID = str(config("CLIENT_ID", cast=str))
CLIENT_SECRET = str(config("CLIENT_SECRET", cast=str))

# Currently, Discord API is pinned to v8 and not strended to be changed per-instance
DISCORD_API_BASE_URL = "https://discord.com/api/"
DISCORD_API_VERSION = "v8"
DISCORD_API_URL = f"{DISCORD_API_BASE_URL}{DISCORD_API_VERSION}/"
DISCORD_GATEWAY_VERSION = "9"
DISCORD_COMMAND_URI = f"{DISCORD_API_URL}/applications/{APPLICATION_ID}/commands"

# Registering commands to a specific guild populates faster,
# so this is used when running in DEBUG mode
if DEBUG:
    DISCORD_COMMAND_URI = f"{DISCORD_COMMAND_URI}/guilds/{TEST_SERVER_ID}/commands"
