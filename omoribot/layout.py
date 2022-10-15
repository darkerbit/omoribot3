from PIL import Image


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

    def render(self, x: int, y: int, w: int, h: int, image: Image):
        if self.horizontal < 0:
            w = self.w
        elif self.horizontal > 0:
            x = w - self.w
            w = self.w

        if self.vertical < 0:
            h = self.h
        elif self.vertical > 0:
            y = h - self.h
            h = self.h

        self._render(x, y, w, h, image)

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        raise NotImplementedError


class Blank(Widget):
    def anim_done(self) -> bool:
        return True

    def _get_size(self) -> tuple[int, int]:
        return 0, 0

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
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

    def _render(self, x: int, y: int, w: int, h: int, image: Image):
        raise NotImplementedError
