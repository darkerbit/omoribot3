import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)


@bot.command()
async def hello(ctx: commands.Context):
    await ctx.reply("hello")


with open("token", "r") as f:
    token = f.read().strip()

bot.run(token)
