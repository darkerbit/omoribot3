from .layout import *
from .containers import HFlow

from PIL import ImageFont, ImageDraw


class TextElement(Widget):
    font_omori = "fonts/OMORI_GAME2.ttf"
    font_alt = "fonts/OMORI_GAME.ttf"
    font_undertale = "fonts/DTM-Mono.otf"
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

        "undertale": font_undertale,
        "ut": font_undertale,
        "deltarune": font_undertale,
        "dr": font_undertale,

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
        x, y, w, h = self.font.getbbox(self.text, anchor="lt")
        return w, h

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        draw = ImageDraw.Draw(image, "RGBA")

        draw.text((x, y), self.text, font=self.font, anchor="lt", fill=self.color)
