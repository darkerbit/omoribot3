from .layout import *

from PIL import ImageDraw


class FilledRect(Widget):
    def __init__(self, w: int, h: int, fill, **kwargs):
        super().__init__(**kwargs)

        self.width = w
        self.height = h
        self.fill = fill

    def anim_done(self) -> bool:
        return True

    def _get_size(self) -> tuple[int, int]:
        return self.width, self.height

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        draw = ImageDraw.Draw(image)

        draw.rectangle((x, y, x + w - 1, y + h - 1), fill=self.fill)


class Portrait(Widget):
    def __init__(self, portrait, **kwargs):
        super().__init__(**kwargs)

        self.portrait = None
        self.raw_portrait = Image.open(portrait)

        self.recrop()

        self.i = 0
        self.last = 0

    def anim_done(self) -> bool:
        return self.i >= getattr(self.raw_portrait, "n_frames", 1)

    def recrop(self):
        self.portrait = self.raw_portrait.convert("RGBA").resize((106, 106)).crop((1, 0, 105, 104))

    def _get_size(self) -> tuple[int, int]:
        return self.portrait.size

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        if self.anim_done():
            self.i = 0

        if self.i != self.last:
            self.raw_portrait.seek(self.i)
            self.recrop()
            self.last = self.i

        image.alpha_composite(self.portrait, dest=(x, y))

        self.i += 1
