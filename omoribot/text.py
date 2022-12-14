import math

from .layout import *
from .containers import HFlow

import random

from PIL import ImageFont, ImageDraw, ImageColor


class TextElement(Widget):
    font_omori = "fonts/OMORI_GAME2.ttf"
    font_alt = "fonts/OMORI_GAME.ttf"
    font_emoji = "fonts/TwitterColorEmoji-SVGinOT.ttf"
    font_japanese = "fonts/HuiFontP29.ttf"
    font_korean = "fonts/YoonDesignWebDotum_KRfont.ttf"
    font_chinese = "fonts/851tegaki_zatsu_normal_0883.ttf"

    font_dict = {
        "omori": font_omori,
        "default": font_omori,
        "def": font_omori,
        "normal": font_omori,

        "alt": font_alt,
        "alternate": font_alt,
        "other": font_alt,

        "emoji": font_emoji,

        "jp": font_japanese,
        "japanese": font_japanese,

        "kr": font_korean,
        "korean": font_korean,

        "ch": font_chinese,
        "cn": font_chinese,
        "chinese": font_chinese,
    }

    font_cache = {}

    def __init__(self, text, font, color, size, is_space=False, **kwargs):
        super().__init__(**kwargs)

        self.text = text
        self.font = self.cache(self.font_dict[font] if font in self.font_dict else self.font_omori, size)
        self.color = color
        self.is_space = is_space

    @staticmethod
    def cache(font, size) -> ImageFont.FreeTypeFont:
        if (font, size) not in TextElement.font_cache:
            print(f"caching {font} with size {size}")
            TextElement.font_cache[(font, size)] = ImageFont.truetype(font, size)

        return TextElement.font_cache[(font, size)]

    def anim_done(self) -> bool:
        return True

    def _get_size(self) -> tuple[int, int]:
        x, y, w, h = self.font.getbbox(self.text, anchor="la")
        return w, h

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        draw = ImageDraw.Draw(image, "RGBA")

        draw.text((x, y), self.text, font=self.font, anchor="la", fill=self.color)


class SpecialTextElement(TextElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.i = 0

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        cx = x

        for c in self.text:
            self._render_char(c, cx, y, w, h, image, dbg)
            cx += self.font.getbbox(c, anchor="la")[2]

        self.i += 1

    def _render_char(self, c, x: int, y: int, w: int, h: int, image: Image, dbg):
        raise NotImplementedError


class Shivering(SpecialTextElement):
    def anim_done(self) -> bool:
        return self.i >= 8

    def _render_char(self, c, x: int, y: int, w: int, h: int, image: Image, dbg):
        draw = ImageDraw.Draw(image, "RGBA")

        draw.text((x + random.randint(-1, 2), y + random.randint(-1, 2)), c, font=self.font, anchor="la", fill=self.color)


class Wobbly(SpecialTextElement):
    def anim_done(self) -> bool:
        return self.i % 30 == 0

    def _render_char(self, c, x: int, y: int, w: int, h: int, image: Image, dbg):
        draw = ImageDraw.Draw(image, "RGBA")

        dist = 8

        draw.text((x, int(y + dist / 2 + math.sin((float(self.i) / 30 + float(x) / 200) * 2 * math.pi) * float(dist) / 2)), c, font=self.font, anchor="la", fill=self.color)


class TextParser:
    omori_colors = {
        "snack": "#51C059",
        "important": "#FFD966",
        "toy": "#FF9232",
        "skill": "#5E92FA",
        "location": "#5AE0D8",
        "weapon": "#AE58CB",
        "charm": "#C263E2",
    }

    class Settings:
        def __init__(self):
            self.font = "omori"
            self.size = 28
            self.color = (255, 255, 255, 255)
            self.clazz = TextElement

        def copy(self):
            o = self.__class__()
            o.size = self.size
            o.font = self.font
            o.color = self.color
            o.clazz = self.clazz

            return o

    def __init__(self, text):
        self.text = text.strip()

        self.i = 0
        self.stack = []
        self.settings = self.Settings()

    def parse(self) -> list[list[Widget]]:
        lines = []
        line = []

        element = ""

        c = self.next()

        while c is not None:
            if c == ' ':
                line.append(self.make_text(element))
                line.append(self.make_text(" ", is_space=True))
                element = ""
            elif c == '\n':
                line.append(self.make_text(element))
                lines.append(line)
                line = []
                element = ""
            elif c == '\\':
                n = self.next()

                if n is not None:
                    element += n
            elif c == '[':
                line.append(self.make_text(element))
                element = ""

                if self.peek() == '/':
                    self.setting()
                    self.pop_settings()
                else:
                    setting = self.setting().split("=")
                    self.push_settings()

                    if setting[0] == "font":
                        self.settings.font = setting[1]
                    elif setting[0] == "size":
                        self.settings.size = int(setting[1])
                    elif setting[0] == "color" or setting[0] == "colour":
                        col = setting[1].lower()

                        self.settings.color = ImageColor.getcolor(self.omori_colors[col] if col in self.omori_colors else col, "RGBA")
                    elif setting[0] == "normal" or setting[0] == "reset":
                        self.settings.clazz = TextElement
                    elif setting[0] == "shiver" or setting[0] == "shivering" \
                            or setting[0] == "shake" or setting[0] == "shaky":
                        self.settings.clazz = Shivering
                    elif setting[0] == "wobble" or setting[0] == "wobbly":
                        self.settings.clazz = Wobbly
            else:
                element += c

            c = self.next()

        line.append(self.make_text(element))
        lines.append(line)

        return lines

    def make_text(self, text, is_space=False, **kwargs):
        if text == "":
            return TextElement(text, self.settings.font, self.settings.color, self.settings.size, is_space=True, **kwargs)

        clazz = TextElement if is_space else self.settings.clazz

        return clazz(text, self.settings.font, self.settings.color, self.settings.size, is_space=is_space, **kwargs)

    def push_settings(self):
        self.stack.append(self.settings.copy())

    def pop_settings(self):
        if len(self.stack) > 0:
            self.settings = self.stack.pop()

    def setting(self):
        c = self.next()
        o = ""

        while c is not None and c != ']':
            o += c
            c = self.next()

        return o

    def next(self):
        c = self.peek()
        self.i += 1
        return c

    def peek(self):
        if self.i >= len(self.text):
            return None

        return self.text[self.i]


class Text(Widget):
    def __init__(self, text, can_newline=True, **kwargs):
        super().__init__(**kwargs)

        self.flow = HFlow(TextParser(text).parse(), pad_x=0, pad_y=0, can_newline=can_newline)

    def anim_done(self) -> bool:
        return self.flow.anim_done()

    def _get_size(self) -> tuple[int, int]:
        return self.flow.get_size()

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        if dbg is not None:
            dbg.push()

        self.flow.render(x, y, w, h, image, dbg)

        if dbg is not None:
            dbg.pop()
