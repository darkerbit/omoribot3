from .layout import *


class FixedSize(Widget):
    def __init__(self, w: int, h: int, child: Widget, **kwargs):
        super().__init__(**kwargs)

        self.width = w
        self.height = h
        self.child = child

    def _get_size(self) -> tuple[int, int]:
        self.child.get_size() # Has side effects so I need to do this first
        
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
