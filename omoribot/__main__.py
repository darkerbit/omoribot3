import discord
from discord.ext import commands

import os
import sys
import shutil
import requests
import subprocess

from omoribot import *


class GifDebugger:
    def __init__(self, folder, file):
        self.i = 0
        self.folder = folder
        self.file = file
        self.indent = 0

    def emit_frame(self, dbg):
        dbg.save(f"{self.folder}{str(self.i).zfill(5)}.png")
        self.i += 1

    def emit_name(self, name):
        self.file.write(". " * self.indent + name + "\n")

    def push(self):
        self.indent += 1

    def pop(self):
        self.indent -= 1


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!' if len(sys.argv) > 1 and sys.argv[1] == "local" else '?', intents=intents)


async def render(tree: Widget, out, ctx, debug):
    im = Image.new("RGBA", tree.get_size())
    w, h = im.size

    if debug:
        folder = f"debug/{out}/"

        if os.path.exists(folder):
            shutil.rmtree(folder)

        os.makedirs(folder)

        f = open(f"{folder}trace.txt", "w")
        dbg = GifDebugger(folder, f)
        tree.render(0, 0, w, h, im, dbg)
        dbg.emit_frame(im)
        f.close()

        subprocess.run(f'ffmpeg -framerate 3 -i {folder}%05d.png -vf "fps=3,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 {folder}{out}.gif',
                       capture_output=True, check=True, shell=True)

        await ctx.send("Debug:", files=[discord.File(f"{folder}{out}.gif"), discord.File(f"{folder}trace.txt")])
    else:
        tree.render(0, 0, w, h, im, None)

    append = []
    rendering = None

    if not tree.anim_done():
        rendering = await ctx.reply("Rendering...")

    while not tree.anim_done():
        frame = Image.new("RGBA", im.size)
        tree.render(0, 0, w, h, frame, None)
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
        subprocess.run(f'ffmpeg -framerate 30 -i {folder}%05d.png -vf "fps=30,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 {folder}{out}.gif',
                       capture_output=True, check=True, shell=True)

        await rendering.delete()

        return f"{folder}{out}.gif"
    else:
        path = f"out/{out}.png"
        im.save(path)
        return path


async def download_attachment(ctx: commands.Context, prefix: str = "portrait"):
    folder = f"downloads/{ctx.author.id}/"

    if not os.path.exists(folder):
        os.makedirs(folder)

    if len(ctx.message.attachments) < 1:
        await ctx.reply(f"You forgot to attach the {prefix}")
        return

    attachment = ctx.message.attachments.pop()

    path = f"{folder}{prefix}_{attachment.filename}"

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


async def generate(ctx: commands.Context, debug: bool, tree: Widget):
    try:
        await ctx.reply(file=discord.File(await render(tree, ctx.author.id, ctx, debug)))
    except discord.HTTPException as e:
        if e.status != 413:
            raise

        await ctx.reply("Resulting render is too large!")


async def generate_textbox(ctx: commands.Context, name: str, portrait_name: str, choices, message: str):
    debug = message.startswith("&DEBUG&")

    if debug:
        message = message.removeprefix("&DEBUG&")

    bg_class = None
    if message.startswith("&BACKGROUND&"):
        bg_class = Background
        message = message.removeprefix("&BACKGROUND&")
    elif message.startswith("&BACKGROUND NO RESIZE&"):
        bg_class = ImageWidget
        message = message.removeprefix("&BACKGROUND NO RESIZE&")

    stack = VStack()

    if name != "none" or portrait_name != "none" or (choices is not None and choices != "none"):
        layer = Layer()

        if name != "none":
            layer.add_child(Box(Margin(Text(name, can_newline=False), top=0, bottom=11, left=7, right=8), horizontal=-1, vertical=1))

        if portrait_name != "none" or (choices is not None and choices != "none"):
            hstack = HStack(horizontal=1, vertical=1)

            if choices is not None and choices != "none":
                cstack = VStack(padding=6)

                for choice in choices.split(";"):
                    choice = choice.strip()

                    selected = choice.startswith("->")

                    if selected:
                        choice = choice.removeprefix("->")

                    cstack.add_child(HStack(Margin(Arrow(visible=selected), top=8, bottom=0, left=2, right=-2), Text(choice, can_newline=False)))

                hstack.add_child(Box(Margin(cstack, bottom=11, right=10, left=5, top=6), vertical=1))

            if portrait_name != "none":
                portr = await resolve_portrait(ctx, portrait_name)

                if portr is None:
                    return

                hstack.add_child(Box(Portrait(portr), vertical=1))

            layer.add_child(hstack)

        stack.add_child(layer)

    arrow = message.endswith("->")

    if arrow:
        message = message.removesuffix("->")

    dialogue = Layer(Margin(Text(message), top=6, left=12, right=12))

    if arrow:
        dialogue.add_child(Margin(Arrow(horizontal=1, vertical=1)))

    stack.add_child(FixedSize(608, 112, Box(dialogue)))

    if bg_class is not None:
        bg = await download_attachment(ctx, "background")

        if bg is None:
            return

        stack = Layer(bg_class(bg), HCenter(Margin(stack, left=0, right=0, top=0, bottom=8, vertical=1)))

    await generate(ctx, debug, stack)


@bot.command()
async def portrait(ctx: commands.Context, portrait_name: str):
    debug = portrait_name.startswith("&DEBUG&")

    if debug:
        portrait_name = portrait_name.removeprefix("&DEBUG&")

    portr = await resolve_portrait(ctx, portrait_name)

    if portr is None:
        return

    await generate(ctx, debug, Box(Portrait(portr)))


async def do_frame(ctx: commands.Context, debug: bool):
    im = await download_attachment(ctx, "image")

    if im is None:
        return

    await generate(ctx, debug, Box(ImageWidget(im)))


@bot.command()
async def frame(ctx: commands.Context):
    await do_frame(ctx, False)


@bot.command()
async def frame_debug(ctx: commands.Context):
    await do_frame(ctx, True)


@bot.command()
async def text(ctx: commands.Context, *, message: str):
    debug = message.startswith("&DEBUG&")

    if debug:
        message = message.removeprefix("&DEBUG&")

    await generate(ctx, debug, Box(Margin(Text(message, can_newline=False), top=0, bottom=11, left=7, right=8)))


@bot.command()
async def guide_header(ctx: commands.Context, *, message: str):
    debug = message.startswith("&DEBUG&")

    if debug:
        message = message.removeprefix("&DEBUG&")

    await ctx.message.delete()
    await ctx.send(file=discord.File(await render(Box(Margin(Text(f"[size=40]{message}[/]", can_newline=False), top=0, bottom=11, left=7, right=8)), ctx.author.id, ctx, debug)))


@bot.command()
async def where_the_fuck_am_i(ctx: commands.Context):
    await ctx.reply(f"I am running from {os.getcwd()}")


@bot.command()
async def wipe_cache(ctx: commands.Context):
    TextElement.font_cache = {}
    print("wiped cache!")
    await ctx.reply("Wiped font cache!")


@bot.command(aliases=["tb"])
async def textbox(ctx: commands.Context, name: str, portrait_name: str, *, message: str):
    await generate_textbox(ctx, name, portrait_name, None, message)


@bot.command(aliases=["ch"])
async def choicer(ctx: commands.Context, name: str, portrait_name: str, choices: str, *, message: str):
    await generate_textbox(ctx, name, portrait_name, choices, message)


def main():
    if not os.path.exists("out/"):
        os.makedirs("out/")

    if not os.path.exists("outgifs/"):
        os.makedirs("outgifs/")

    if not os.path.exists("downloads/"):
        os.makedirs("downloads/")

    if not os.path.exists("debug/"):
        os.makedirs("debug/")

    with open("token", "r") as f:
        token = f.read().strip()

    bot.run(token)


if __name__ == '__main__':
    main()
