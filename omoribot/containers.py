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

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        self.child.render(x, y, w, h, image, dbg)


class Layer(Container):
    def _get_size(self) -> tuple[int, int]:
        w = 0
        h = 0

        for c in self.children:
            cw, ch = c.get_size()

            if cw > w:
                w = cw

            if ch > h:
                h = ch

        return w, h

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        for c in self.children:
            c.render(x, y, w, h, image, dbg)


class Box(Widget):
    def __init__(self, child: Widget, **kwargs):
        super().__init__(**kwargs)

        self.child = child

    def anim_done(self) -> bool:
        return self.child.anim_done()

    def _get_size(self) -> tuple[int, int]:
        w, h = self.child.get_size()

        return w + 10, h + 10

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        draw = ImageDraw.Draw(image)
        draw.rectangle((x, y, x + w - 1, y + h - 1), fill=(0, 0, 0, 255))
        draw.rectangle((x + 1, y + 1, x + w - 2, y + h - 2), outline=(255, 255, 255, 255), width=3)

        self.child.render(x + 5, y + 5, w - 10, h - 10, image, dbg)


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

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        cy = y

        for c in self.children:
            ch = c.get_size()[1]
            c.render(x, cy, w, ch, image, dbg)
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

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        cx = x

        for c in self.children:
            cw = c.get_size()[0]
            c.render(cx, y, cw, h, image, dbg)
            cx += cw + self.padding


class HFlow(Widget):
    def __init__(self, lines: list[list[Widget]], pad_x: int = 4, pad_y: int = 4, can_newline=True, **kwargs):
        super().__init__(**kwargs)

        self.lines = lines
        self.pad_x = pad_x
        self.pad_y = pad_y

        self.can_newline = can_newline

    def anim_done(self) -> bool:
        return all(c.anim_done() for line in self.lines for c in line)

    def _get_size(self) -> tuple[int, int]:
        w = 0
        h = (len(self.lines) - 1) * self.pad_y

        for line in self.lines:
            lw = (len(line) - 1) * self.pad_x
            lh = 0
            for c in line:
                cw, ch = c.get_size()
                lw += cw

                if ch > lh:
                    lh = ch

            if lw > w:
                w = lw

            h += lh

        return w, h

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        rx = x
        ry = y

        for line in self.lines:
            lh = 0

            for c in line:
                cw, ch = c.get_size()

                if rx + cw >= w and self.can_newline:
                    rx = x
                    ry += lh + self.pad_y
                    lh = 0

                    if getattr(c, "is_space", False):
                        continue

                if ch > lh:
                    lh = ch

                c.render(rx, ry, cw, ch, image, dbg)

                rx += cw + self.pad_x

            rx = x
            ry += lh + self.pad_y


class Margin(Widget):
    def __init__(self, child: Widget, left: int = 8, right: int = 8, top: int = 8, bottom: int = 8, **kwargs):
        super().__init__(**kwargs)

        self.child = child

        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def anim_done(self) -> bool:
        return self.child.anim_done()

    def _get_size(self) -> tuple[int, int]:
        cw, ch = self.child.get_size()

        return cw + self.left + self.right, ch + self.top + self.bottom

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        self.child.render(x + self.left, y + self.top, w - self.left - self.right, h - self.top - self.bottom, image, dbg)
