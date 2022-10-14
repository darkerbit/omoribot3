import discord
from discord.ext import commands
from PIL import Image

import os

from omoribot import *


def render(tree: Widget, out):
    im = Image.new("RGBA", tree.get_size())

    w, h = im.size
    tree.render(0, 0, w, h, im)

    im.save(out)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)


@bot.command()
async def portrait(ctx: commands.Context, portrait: str):
    tree = Box(Portrait(f"portraits/{portrait}.png"))

    path = f"out/{ctx.author.id}.png"
    render(tree, path)

    await ctx.reply(file=discord.File(path))


if __name__ == '__main__':
    if not os.path.exists("out/"):
        os.makedirs("out/")

    with open("token", "r") as f:
        token = f.read().strip()

    bot.run(token)
