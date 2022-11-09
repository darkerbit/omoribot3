from .layout import *

from PIL import Image


class BadApplePlayer(Widget):
    size = 32

    portrait = Image.open("portraits/hs_mari_smug.png").resize((size, size))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.i = 0
        self.gif = Image.open("BadApple.gif")

    def anim_done(self) -> bool:
        return self.i >= self.gif.n_frames

    def _get_size(self) -> tuple[int, int]:
        return self.size * self.gif.width, self.size * self.gif.height

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        self.gif.seek(self.i)
        self.i += 1

        frame = self.gif.convert("RGBA")

        for j in range(frame.height):
            for i in range(frame.width):
                if frame.getpixel((i, j))[0] > 100:
                    image.alpha_composite(self.portrait, (i * self.size, j * self.size))
