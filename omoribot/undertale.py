from .layout import *
from .text import TextElement

from PIL import ImageDraw


class UndertaleText(Widget):
    font_undertale = "fonts/8bitoperator_jve.ttf"

    font_size = 16 * 2

    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)

        self.text = text

    def anim_done(self) -> bool:
        return True

    def _get_size(self) -> tuple[int, int]:
        lines = self.text.splitlines(False)

        w = 0

        for line in lines:
            lw = 25 * 2

            for c in line.strip().removeprefix("*").strip():
                if c == ' ':
                    lw += 8 * 2
                else:
                    lw += 8 * 2

            if lw > w:
                w = lw

        return w * 2 + 11 * 2, 6 * 2 + len(lines) * 19 * 2

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        font = TextElement.cache(self.font_undertale, self.font_size)
        draw = ImageDraw.Draw(image, "RGBA")

        lines = self.text.splitlines(False)

        dy = 6 * 2

        for line in lines:
            if line.strip().startswith("*"):
                draw.text((x + 11 * 2, dy + y), "*", font=font, anchor="la", fill=(255, 255, 255, 255))

            dx = 27 * 2

            for word in line.strip().removeprefix("*").strip().split():
                if dx + len(word) * 8 * 2 >= w - 8 * 2:
                    dx = 27 * 2
                    dy += 19 * 2

                for c in word:
                    draw.text((dx + x, dy + y), c, font=font, anchor="la", fill=(255, 255, 255, 255))
                    dx += 8 * 2

                dx += 8 * 2

            dy += 19 * 2


class UndertaleBox(Widget):
    def __init__(self, child: Widget, **kwargs):
        super().__init__(**kwargs)

        self.child = child

    def anim_done(self) -> bool:
        return self.child.anim_done()

    def _get_size(self) -> tuple[int, int]:
        w, h = self.child.get_size()

        return w * 2 + 6 * 2, h + 6 * 2

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        draw = ImageDraw.Draw(image, "RGBA")

        draw.rectangle((x, y, x + w - 1 * 2, y + h - 1 * 2), fill=(255, 255, 255, 255))
        draw.rectangle((x + 3 * 2, y + 3 * 2, x + w - 4 * 2, y + h - 4 * 2), fill=(0, 0, 0, 255))

        if dbg is not None:
            dbg.push()

        self.child.render(x + 3 * 2, y + 3 * 2, w - 6 * 2, h - 6 * 2, image, dbg)

        if dbg is not None:
            dbg.pop()


class UndertalePortrait(Widget):
    def __init__(self, portrait, **kwargs):
        super().__init__(**kwargs)

        self.raw_portrait = Image.open(portrait)

        self.i = 0
        self.last = 0

    def anim_done(self) -> bool:
        return self.i >= getattr(self.raw_portrait, "n_frames", 1)

    def _get_size(self) -> tuple[int, int]:
        return self.raw_portrait.size

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        if self.anim_done():
            self.i = 0

        if self.i != self.last:
            self.raw_portrait.seek(self.i)
            self.last = self.i

        portrait = self.raw_portrait.convert("RGBA").resize((self.raw_portrait.width * 2, self.raw_portrait.height * 2), Image.NEAREST)

        (cw, ch) = portrait.size

        image.alpha_composite(portrait, dest=(int(x + (w - cw) / 2), int(y + (h - ch) / 2)))

        self.i += 1
