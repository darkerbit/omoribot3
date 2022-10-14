import discord
from discord.ext import commands

import omoribot

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)


with open("token", "r") as f:
    token = f.read().strip()

bot.run(token)
