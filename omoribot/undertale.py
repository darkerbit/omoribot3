from .layout import *
from .text import TextElement

from PIL import ImageDraw


class UndertaleText(Widget):
    font_undertale = "fonts/8bitoperator_jve.ttf"

    font_size = 16

    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)

        self.text = text

    def anim_done(self) -> bool:
        return True

    def _get_size(self) -> tuple[int, int]:
        lines = self.text.splitlines(False)

        w = 0

        for line in lines:
            lw = 25

            for c in line.strip().removeprefix("*").strip():
                if c == ' ':
                    lw += 8
                else:
                    lw += 8

            if lw > w:
                w = lw

        return w, 6 + len(lines) * 19

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        font = TextElement.cache(self.font_undertale, self.font_size)
        draw = ImageDraw.Draw(image, "RGBA")

        lines = self.text.splitlines(False)

        dy = 6

        for line in lines:
            if line.strip().startswith("*"):
                draw.text((x + 11, dy + y), "*", font=font, anchor="la", fill=(255, 255, 255, 255))

            dx = 27

            for c in line.strip().removeprefix("*").strip():
                if c == ' ':
                    dx += 8
                else:
                    draw.text((dx + x, dy + y), c, font=font, anchor="la", fill=(255, 255, 255, 255))
                    dx += 8

            dy += 19


class UndertaleBox(Widget):
    def __init__(self, child: Widget, **kwargs):
        super().__init__(**kwargs)

        self.child = child

    def anim_done(self) -> bool:
        return self.child.anim_done()

    def _get_size(self) -> tuple[int, int]:
        w, h = self.child.get_size()

        return w + 6, h + 6

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        draw = ImageDraw.Draw(image, "RGBA")

        draw.rectangle((x, y, x + w - 1, y + h - 1), fill=(255, 255, 255, 255))
        draw.rectangle((x + 3, y + 3, x + w - 4, y + h - 4), fill=(0, 0, 0, 255))

        if dbg is not None:
            dbg.push()

        self.child.render(x + 3, y + 3, w - 3, h - 3, image, dbg)

        if dbg is not None:
            dbg.pop()
