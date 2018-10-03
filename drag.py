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

    total_pixels = 54*96
    width_ratio = 1
    heigth_ratio = 1
    mappings = {}
    img = None
    img_canvas = None

    def __init__(self, name):
        self.name = name
        self.canvas = self.label = self.id = None

    def attach(self, canvas, x=10, y=10):
        if canvas is self.canvas:
            self.canvas.coords(self.id, x, y)
            print(self.calculate(x, y))
            return
        if self.canvas:
            self.detach()
        if not canvas:
            return
        label = tkinter.Label(canvas, text=self.name,
                              borderwidth=1, relief="ridge", width=5)
        id = canvas.create_window(x, y, window=label, anchor="nw")
        self.canvas = canvas
        self.label = label
        self.id = id
        print(self.calculate(x, y))
        label.focus_set()
        label.bind("<ButtonPress>", self.press)

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
        self.label.focus_set()
        self.label.bind('<Left>', self.left)
        self.label.bind('<Right>', self.right)
        self.label.bind('<Up>', self.up)
        self.label.bind('<Down>', self.down)
        self.label.bind('<BackSpace>', self.img_canvas.remove_lane)
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
        x, y = self.canvas.coords(self.id)
        self.attach(self.canvas, x-1, y)

    def right(self, event):
        x, y = self.canvas.coords(self.id)
        self.attach(self.canvas, x+1, y)

    def up(self, event):
        x, y = self.canvas.coords(self.id)
        self.attach(self.canvas, x, y-1)

    def down(self, event):
        x, y = self.canvas.coords(self.id)
        self.attach(self.canvas, x, y+1)

    def delete(self, event):
        self.detach()

    def optimize_lane(self):
        x, y = self.canvas.coords(self.id)
        # convert to original x and y
        max_adj = float("-inf")
        max_info = None
        for i in range(x-10, x+10):
            for j in range(y-10, y+10):
                cur_calc = self.calculate(i, j)
                cur_adj = cur_calc[0]
                if max_adj < cur_adj:
                    max_info = cur_calc
        print(max_info)
        return max_info

    def calculate(self, x=None, y=None):
        if x == None and y == None:
            x, y = self.canvas.coords(self.id)
        # convert x and y for original

        print("GUI x: ", x)
        print("GUI y: ", y)

        x = int(x * self.width_ratio)
        y = int(y * self.height_ratio)

        print("New x: ", x)
        print("New y: ", y)
        w = 96
        h = 54

        print(self.img.shape)

        # crop image
        crop_img = self.img[y-1:y+h+1, x-1:x+w+1]
        print(crop_img.shape)

        # summing the total volume of box by grabbing each mapping
        vol = 0
        for i in range(1, h+1):
            for j in range(1, w+1):
                m = self.mappings[str(crop_img[i, j])]
                vol += m
        print("Volume OD: ", vol)

        # Get mean background of bigger box
        mean_b = 0
        for j in range(0, h):
            mean_b += self.mappings[str(crop_img[j, 0])] + \
                self.mappings[str(crop_img[j, w-1])]
        for i in range(1, w-1):
            mean_b += self.mappings[str(crop_img[0, i])] + \
                self.mappings[str(crop_img[h-1, i])]

        mean_b /= (w * 2) + ((h-2) * 2)
        print("Mean Bkgd: ", mean_b)

        adj_vol = vol - (self.total_pixels * mean_b)
        print("Adj Vol: ", adj_vol)

        return adj_vol, mean_b, vol, (x, y)


class ImageCanvas:

    def __init__(self, root, image_path, mappings, i_width, i_height):
        self.canvas = tkinter.Canvas(root, width=i_width, height=i_height)
        self.max_width = i_width
        self.max_height = i_height
        self.img_info = cv2.imread(image_path, -1)
        self.map = mappings

        i = self.map_uint16_to_uint8(self.img_info)
        im = Image.fromarray(i, mode="L")
        self.width_ratio = self.img_info.shape[1] / i_width
        print("Img info shape : ", self.img_info.shape)
        self.height_ratio = self.img_info.shape[0] / i_height
        self.lanes = []

        Lane.width_ratio = self.width_ratio
        Lane.height_ratio = self.height_ratio
        Lane.mappings = self.map
        Lane.img = self.img_info
        Lane.img_canvas = self

        im = im.resize((i_width, i_height), Image.ANTIALIAS)
        self.img_label = ImageTk.PhotoImage(im)
        self.canvas.create_image(0, 0, image=self.img_label, anchor=NW)

        self.canvas.pack(fill=BOTH)
        self.canvas.dnd_accept = self.dnd_accept

    def map_uint16_to_uint8(self, img, lower_bound=None, upper_bound=None):
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
        self.selected = source.label
        self.selected.focus_set()
        self.selected.bind('<Left>', source.left)
        self.selected.bind('<Right>', source.right)
        self.selected.bind('<Up>', source.up)
        self.selected.bind('<Down>', source.down)
        # self.selected.bind('<BackSpace>', source.delete)
        # self.selected.bind('<BackSpace>', self.remove_lane)

    def add_lane(self):
        number = len(self.lanes) + 1
        lane = Lane("Lane" + str(number))
        lane.attach(self.canvas, self.max_width / 2, 40)
        self.lanes.append(lane)

        # self.lanes.append(lane)
        # pass

    def remove_lane(self, source):
        # for lane in lanes:
        #     if lane.id == source.id:
        #         lanes.remove(lane)
        # source.detach()

        pass

    def optimize_lanes(self):
        # for lane in self.lanes:
        #     lane.optimize_lane()
        # update table
        pass


class Table:

    def __init__(self):
        pass
