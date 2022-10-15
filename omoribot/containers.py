from .layout import *

from PIL import ImageDraw


class FixedSize(Widget):
    def __init__(self, w: int, h: int, child: Widget, **kwargs):
        super().__init__(**kwargs)

        self.width = w
        self.height = h
        self.child = child

    def anim_done(self) -> bool:
        return self.child.anim_done()

    def _get_size(self) -> tuple[int, int]:
        self.child.get_size()  # Has side effects so I need to do this first

        return self.width, self.height

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        self.child.render(x, y, w, h, image)


class Layer(Container):
    def _get_size(self) -> tuple[int, int]:
        w = 0
        h = 0

        for c in self.children:
            cw, ch = c.get_size()

            if cw > w:
                w = cw

            if ch > h:
                h = cw

        return w, h

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        for c in self.children:
            c.render(x, y, w, h, image)


class Box(Widget):
    def __init__(self, child: Widget, **kwargs):
        super().__init__(**kwargs)

        self.child = child

    def anim_done(self) -> bool:
        return self.child.anim_done()

    def _get_size(self) -> tuple[int, int]:
        w, h = self.child.get_size()

        return w + 10, h + 10

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        draw = ImageDraw.Draw(image)
        draw.rectangle((x, y, x+w-1, y+h-1), fill=(0, 0, 0, 255))
        draw.rectangle((x + 1, y + 1, x + w - 2, y + h - 2), outline=(255, 255, 255, 255), width=3)

        self.child.render(x + 5, y + 5, w - 10, h - 10, image)


class VStack(Container):
    def __init__(self, *args, padding: int = 4, **kwargs):
        super().__init__(*args, **kwargs)

        self.padding = padding

    def _get_size(self) -> tuple[int, int]:
        w = 0
        h = (len(self.children) - 1) * self.padding

        for c in self.children:
            cw, ch = c.get_size()

            if cw > w:
                w = cw

            h += ch

        return w, h

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        cy = y

        for c in self.children:
            ch = c.get_size()[1]
            c.render(x, cy, w, ch, image)
            cy += ch + self.padding


class HStack(Container):
    def __init__(self, *args, padding: int = 4, **kwargs):
        super().__init__(*args, **kwargs)

        self.padding = padding

    def _get_size(self) -> tuple[int, int]:
        w = (len(self.children) - 1) * self.padding
        h = 0

        for c in self.children:
            cw, ch = c.get_size()

            if ch > h:
                h = ch

            w += cw

        return w, h

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        cx = x

        for c in self.children:
            cw = c.get_size()[0]
            c.render(cx, y, cw, h, image)
            cx += cw + self.padding
