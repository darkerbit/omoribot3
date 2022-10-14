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
async def test(ctx: commands.Context):
    tree = FixedSize(640, 480, Layer(
        FilledRect(0, 0, (255, 0, 0, 255)),
        FilledRect(128, 128, (0, 255, 0, 255), horizontal=-1),
        FilledRect(64, 128, (0, 0, 255), horizontal=1, vertical=-1),
        FilledRect(128, 64, (255, 0, 255), horizontal=1, vertical=1)
    ))

    path = f"out/{ctx.author.id}.png"
    render(tree, path)

    await ctx.reply(file=discord.File(path))


if __name__ == '__main__':
    if not os.path.exists("out/"):
        os.makedirs("out/")

    with open("token", "r") as f:
        token = f.read().strip()

    bot.run(token)
