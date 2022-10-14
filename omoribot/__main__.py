import discord
from discord.ext import commands
from PIL import Image

import os
import requests

from omoribot import *


def render(tree: Widget, out):
    im = Image.new("RGBA", tree.get_size())

    w, h = im.size
    tree.render(0, 0, w, h, im)

    im.save(out)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)


async def download_attachment(ctx: commands.Context):
    folder = f"downloads/{ctx.author.id}/"

    if not os.path.exists(folder):
        os.makedirs(folder)

    if len(ctx.message.attachments) < 1:
        await ctx.reply("you forgor attachment")
        return

    attachment = ctx.message.attachments.pop()

    path = f"{folder}{attachment.filename}"

    with open(path, "wb") as o:
        r = requests.get(attachment.url)

        for chunk in r.iter_content(8192):
            o.write(chunk)

    return path


async def resolve_portrait(ctx: commands.Context, portrait_name: str):
    if portrait_name == "attached":
        return await download_attachment(ctx)

    safe = os.path.abspath("portraits/")
    portr = os.path.abspath(f"portraits/{portrait_name}.png")

    if os.path.commonpath([safe, portr]) != safe:
        await ctx.reply("Can't load portraits from outside the portraits folder!")
        return

    if not os.path.exists(portr):
        await ctx.reply("No such portrait!")
        return

    return portr


@bot.command()
async def portrait(ctx: commands.Context, portrait_name: str):
    portr = ""

    if portrait_name != "attached":
        portr = await resolve_portrait(ctx, portrait_name)
    else:
        portr = await download_attachment(ctx)

    if portr is None:
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

    if not os.path.exists("downloads/"):
        os.makedirs("downloads/")

    with open("token", "r") as f:
        token = f.read().strip()

    bot.run(token)
