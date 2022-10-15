import discord
from discord.ext import commands

import os
import shutil
import requests
import subprocess
import random

from omoribot import *


async def render(tree: Widget, out, ctx):
    im = Image.new("RGBA", tree.get_size())

    w, h = im.size
    tree.render(0, 0, w, h, im)

    append = []
    rendering = None

    if not tree.anim_done():
        rendering = await ctx.reply("Rendering...")

    while not tree.anim_done():
        frame = Image.new("RGBA", im.size)
        tree.render(0, 0, w, h, frame)
        append.append(frame)

    if len(append) > 0:
        # Pillow's GIF saving does not work correctly so I have to do this shit
        folder = f"outgifs/{out}/"

        if os.path.exists(folder):
            shutil.rmtree(folder)

        os.makedirs(folder)

        # Save first frame
        im.save(f"{folder}00000.png")

        # Save remaining frames
        for i in range(len(append)):
            append[i].save(f"{folder}{str(i + 1).zfill(5)}.png")

        # Run ffmpeg
        subprocess.run(f'ffmpeg -i {folder}%05d.png -vf "fps=30,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 {folder}{out}.gif',
                       capture_output=True, check=True, shell=True)

        await rendering.delete()

        return f"{folder}{out}.gif"
    else:
        path = f"out/{out}.png"
        im.save(path)
        return path


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
    portr = await resolve_portrait(ctx, portrait_name)

    if portr is None:
        return

    tree = Box(Portrait(portr))

    path = ctx.author.id
    await ctx.reply(file=discord.File(await render(tree, path, ctx)))


@bot.command()
async def where_the_fuck_am_i(ctx: commands.Context):
    await ctx.reply(f"I am running from {os.getcwd()}")


@bot.command(aliases=["tb"])
async def textbox(ctx: commands.Context, name: str, portrait_name: str, *, message: str):
    layer = Layer()

    if name != "none":
        layer.add_child(Box(Margin(Text(name, can_newline=False), top=0, bottom=11, left=7, right=8), horizontal=-1, vertical=1))

    if portrait_name != "none":
        portr = await resolve_portrait(ctx, portrait_name)

        if portr is None:
            return

        layer.add_child(Box(Portrait(portr), horizontal=1, vertical=1))

    tree = VStack(
        layer,
        FixedSize(608, 112, Box(Margin(Text(message), top=6, left=12, right=12)))
    )

    path = ctx.author.id
    await ctx.reply(file=discord.File(await render(tree, path, ctx)))


if __name__ == '__main__':
    if not os.path.exists("out/"):
        os.makedirs("out/")

    if not os.path.exists("outgifs/"):
        os.makedirs("outgifs/")

    if not os.path.exists("downloads/"):
        os.makedirs("downloads/")

    with open("token", "r") as f:
        token = f.read().strip()

    bot.run(token)
