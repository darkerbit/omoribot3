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
async def portrait(ctx: commands.Context, portrait_name: str):
    safe = os.path.abspath("portraits/")
    portr = os.path.abspath(f"portraits/{portrait_name}.png")

    await ctx.send(portr)
    await ctx.send(os.path.commonpath([safe, portr]))

    if os.path.commonpath([safe, portr]) != safe:
        await ctx.reply("Can't load portraits from outside the portraits folder!")
        return

    if not os.path.exists(portr):
        await ctx.reply("No such portrait!")
        return

    tree = Box(Portrait(portr))

    path = f"out/{ctx.author.id}.png"
    render(tree, path)

    await ctx.reply(file=discord.File(path))


@bot.command()
async def where_the_fuck_am_i(ctx: commands.Context):
    await ctx.reply(f"I am running from {os.getcwd()}")


if __name__ == '__main__':
    if not os.path.exists("out/"):
        os.makedirs("out/")

    with open("token", "r") as f:
        token = f.read().strip()

    bot.run(token)
