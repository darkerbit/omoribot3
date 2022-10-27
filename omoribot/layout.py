from PIL import Image, ImageDraw


class Widget:
    def __init__(self, horizontal=0, vertical=0):
        self.w = 0
        self.h = 0

        self.horizontal = horizontal
        self.vertical = vertical

    def anim_done(self) -> bool:
        raise NotImplementedError

    def get_size(self) -> tuple[int, int]:
        self.w, self.h = self._get_size()
        return self.w, self.h

    def _get_size(self) -> tuple[int, int]:
        raise NotImplementedError

    def render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        if dbg is not None:
            dbg.emit_name(self.__class__.__name__)

            from .text import TextElement

            dbg_im = image.copy()
            draw = ImageDraw.Draw(dbg_im, "RGBA")

            font = TextElement.cache(TextElement.font_omori, 16)

            draw.rectangle((x, y, w+x-1, h+y-1), fill=(0, 0, 255, 255))
            draw.text((x, y), f"{x} {y}\n{w} {h}\n{self.w} {self.h}", fill=(255, 255, 255, 255), stroke_fill=(0, 0, 0, 255), stroke_width=1, font=font, anchor="la")
            dbg.emit_frame(dbg_im)

        if self.horizontal < 0:
            w = self.w
        elif self.horizontal > 0:
            x = x + w - self.w
            w = self.w

        if self.vertical < 0:
            h = self.h
        elif self.vertical > 0:
            y = y + h - self.h
            h = self.h

        if dbg is not None:
            from .text import TextElement

            dbg_im = image.copy()
            draw = ImageDraw.Draw(dbg_im, "RGBA")

            font = TextElement.cache(TextElement.font_omori, 16)

            draw.rectangle((x, y, w + x - 1, h + y - 1), fill=(0, 255, 0, 255))
            draw.text((x, y), f"{x} {y}\n{w} {h}\n{self.w} {self.h}", fill=(255, 255, 255, 255), stroke_fill=(0, 0, 0, 255), stroke_width=1, font=font, anchor="la")
            dbg.emit_frame(dbg_im)

        self._render_bodge(x, y, w, h, image, dbg)

    def _render_bodge(self, x, y, w, h, image, dbg):
        self._render(x, y, w, h, image, dbg)

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        raise NotImplementedError


class Blank(Widget):
    def anim_done(self) -> bool:
        return True

    def _get_size(self) -> tuple[int, int]:
        return 0, 0

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        pass


class Container(Widget):
    def __init__(self, *children: Widget, **kwargs):
        super().__init__(**kwargs)

        self.children = list(children)

    def anim_done(self) -> bool:
        return all(c.anim_done() for c in self.children)

    def add_child(self, child: Widget):
        self.children.append(child)

    def remove_child(self, child: Widget):
        self.children.remove(child)

    def _get_size(self) -> tuple[int, int]:
        raise NotImplementedError

    def _render_bodge(self, x, y, w, h, image, dbg):
        if dbg is not None:
            dbg.push()

        self._render(x, y, w, h, image, dbg)

        if dbg is not None:
            dbg.pop()

    def _render(self, x: int, y: int, w: int, h: int, image: Image, dbg):
        raise NotImplementedError
