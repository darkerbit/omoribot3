from .layout import *

from PIL import ImageDraw


class FilledRect(Widget):
    def __init__(self, w: int, h: int, fill, **kwargs):
        super().__init__(**kwargs)

        self.width = w
        self.height = h
        self.fill = fill

    def _get_size(self) -> tuple[int, int]:
        return self.width, self.height

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        draw = ImageDraw.Draw(image)

        draw.rectangle((x, y, x+w-1, y+h-1), fill=self.fill)
