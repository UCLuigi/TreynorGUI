from tkinter import *
import tkinter
import numpy as np
from PIL import ImageTk, Image
import cv2

# The factory function


def dnd_start(source, event):
    h = DndHandler(source, event)
    if h.root:
        return h
    else:
        return None


# The class that does the work

class DndHandler:

    root = None

    def __init__(self, source, event):
        if event.num > 5:
            return
        root = event.widget._root()
        try:
            root.__dnd
            return  # Don't start recursive dnd
        except AttributeError:
            root.__dnd = self
            self.root = root
        self.source = source
        self.target = None
        self.initial_button = button = event.num
        self.initial_widget = widget = event.widget
        self.release_pattern = "<B%d-ButtonRelease-%d>" % (button, button)
        self.save_cursor = widget['cursor'] or ""
        widget.bind(self.release_pattern, self.on_release)
        widget.bind("<Motion>", self.on_motion)
        widget['cursor'] = "hand2"

    def __del__(self):
        root = self.root
        self.root = None
        if root:
            try:
                del root.__dnd
            except AttributeError:
                pass

    def on_motion(self, event):
        x, y = event.x_root, event.y_root
        target_widget = self.initial_widget.winfo_containing(x, y)
        source = self.source
        new_target = None
        while target_widget:
            try:
                attr = target_widget.dnd_accept
            except AttributeError:
                pass
            else:
                new_target = attr(source, event)
                if new_target:
                    break
            target_widget = target_widget.master
        old_target = self.target
        if old_target is new_target:
            if old_target:
                old_target.dnd_motion(source, event)
        else:
            if old_target:
                self.target = None
                old_target.dnd_leave(source, event)
            if new_target:
                new_target.dnd_enter(source, event)
                self.target = new_target

    def on_release(self, event):
        self.finish(event, 1)

    def cancel(self, event=None):
        self.finish(event, 0)

    def finish(self, event, commit=0):
        target = self.target
        source = self.source
        widget = self.initial_widget
        root = self.root
        try:
            del root.__dnd
            self.initial_widget.unbind(self.release_pattern)
            self.initial_widget.unbind("<Motion>")
            widget['cursor'] = self.save_cursor
            self.target = self.source = self.initial_widget = self.root = None
            if target:
                if commit:
                    target.dnd_commit(source, event)
                else:
                    target.dnd_leave(source, event)
        finally:
            source.dnd_end(target, event)


# ----------------------------------------------------------------------
# The rest is here for testing and demonstration purposes only!

class Lane:

    def __init__(self, name):
        self.name = name
        self.canvas = self.label = self.id = None

    def attach(self, canvas, x=10, y=10):
        if canvas is self.canvas:
            self.canvas.coords(self.id, x, y)
            return
        if self.canvas:
            self.detach()
        if not canvas:
            return
        label = tkinter.Label(canvas, text=self.name,
                              borderwidth=2, relief="raised")
        id = canvas.create_window(x, y, window=label, anchor="nw")
        self.canvas = canvas
        self.label = label
        self.id = id
        label.bind("<ButtonPress>", self.press)
        # label.bind('<Left>', self.left)
        # label.bind('<Right>', self.right)
        # label.bind('<Up>', self.up)
        # label.bind('<Down>', self.down)

    def detach(self):
        canvas = self.canvas
        if not canvas:
            return
        id = self.id
        label = self.label
        self.canvas = self.label = self.id = None
        canvas.delete(id)
        label.destroy()

    def press(self, event):
        if dnd_start(self, event):
            # where the pointer is relative to the label widget:
            self.x_off = event.x
            self.y_off = event.y
            # where the widget is relative to the canvas:
            self.x_orig, self.y_orig = self.canvas.coords(self.id)

    def move(self, event):
        x, y = self.where(self.canvas, event)
        self.canvas.coords(self.id, x, y)

    def putback(self):
        self.canvas.coords(self.id, self.x_orig, self.y_orig)

    def where(self, canvas, event):
        # where the corner of the canvas is relative to the screen:
        x_org = canvas.winfo_rootx()
        y_org = canvas.winfo_rooty()
        # where the pointer is relative to the canvas widget:
        x = event.x_root - x_org
        y = event.y_root - y_org
        # compensate for initial pointer offset
        return x - self.x_off, y - self.y_off

    def dnd_end(self, target, event):
        pass

    def left(self, event):
        print("left")
        x, y = self.where(self.canvas, event)
        self.canvas.coords(self.id, x - 1, y)

    def right(self, event):
        x, y = self.where(self.canvas, event)
        self.canvas.coords(self.id, x + 1, y)

    def up(self, event):
        x, y = self.where(self.canvas, event)
        self.canvas.coords(self.id, x, y - 1)

    def down(self, event):
        x, y = self.where(self.canvas, event)
        self.canvas.coords(self.id, x, y + 1)


class ImageCanvas:

    def __init__(self, root):
        self.canvas = tkinter.Canvas(root, width=1000, height=700)
        img = cv2.imread("test4.tif", -1)
        i = self.map_uint16_to_uint8(img)
        im = Image.fromarray(i, mode="L")
        im = im.resize((1000, 700), Image.ANTIALIAS)
        self.img_label = ImageTk.PhotoImage(im)
        self.canvas.create_image(0, 0, image=self.img_label, anchor=NW)
        self.canvas.pack(fill="both", expand=1)
        self.canvas.dnd_accept = self.dnd_accept

    def map_uint16_to_uint8(self, img, lower_bound=None, upper_bound=None):
        '''
        Map a 16-bit image trough a lookup table to convert it to 8-bit.

        Parameters
        ----------
        img: numpy.ndarray[np.uint16]
            image that should be mapped
        lower_bound: int, optional
            lower bound of the range that should be mapped to ``[0, 255]``,
            value must be in the range ``[0, 65535]`` and smaller than `upper_bound`
            (defaults to ``numpy.min(img)``)
        upper_bound: int, optional
            upper bound of the range that should be mapped to ``[0, 255]``,
            value must be in the range ``[0, 65535]`` and larger than `lower_bound`
            (defaults to ``numpy.max(img)``)

        Returns
        -------
        numpy.ndarray[uint8]
        '''
        if lower_bound is not None and not(0 <= lower_bound < 2**16):
            raise ValueError(
                '"lower_bound" must be in the range [0, 65535]')
        if upper_bound is not None and not(0 <= upper_bound < 2**16):
            raise ValueError(
                '"upper_bound" must be in the range [0, 65535]')
        if lower_bound is None:
            lower_bound = np.min(img)
        if upper_bound is None:
            upper_bound = np.max(img)
        if lower_bound >= upper_bound:
            raise ValueError(
                '"lower_bound" must be smaller than "upper_bound"')
        lut = np.concatenate([
            np.zeros(lower_bound, dtype=np.uint16),
            np.linspace(0, 255, upper_bound -
                        lower_bound).astype(np.uint16),
            np.ones(2**16 - upper_bound, dtype=np.uint16) * 255
        ])
        return lut[img].astype(np.uint8)

    def dnd_accept(self, source, event):
        return self

    def dnd_enter(self, source, event):
        self.canvas.focus_set()  # Show highlight border
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = source.canvas.bbox(source.id)
        dx, dy = x2-x1, y2-y1
        self.dndid = self.canvas.create_rectangle(x, y, x+dx, y+dy)
        self.dnd_motion(source, event)

    def dnd_motion(self, source, event):
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = self.canvas.bbox(self.dndid)
        self.canvas.move(self.dndid, x-x1, y-y1)

    def dnd_leave(self, source, event):
        self.canvas.focus_set()  # Hide highlight border
        self.canvas.delete(self.dndid)
        self.dndid = None

    def dnd_commit(self, source, event):
        self.dnd_leave(source, event)
        x, y = source.where(self.canvas, event)
        source.attach(self.canvas, x, y)
        # self.canvas.focus_set()
        self.selected = source.label
        # self.selected.bind('<Left>', source.left)
        # self.selected.bind('<Right>', source.right)
        # self.selected.bind('<Up>', source.up)
        # self.selected.bind('<Down>', source.down)


def test():
    root = tkinter.Tk()
    root.geometry("1000x800")
    t1 = ImageCanvas(root)
    i1 = Lane("Lane 1")
    i1.attach(t1.canvas, 50, 50)
    # i1.label.bind('<Left>', i1.left)
    # i1.label.bind('<Right>', i1.right)
    # i1.label.bind('<Up>', i1.up)
    # i1.label.bind('<Down>', i1.down)
    root.mainloop()


if __name__ == '__main__':
    test()
