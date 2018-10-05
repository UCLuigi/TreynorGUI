from tkinter import *
import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
import cv2
from tkinter.ttk import Progressbar

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

    total_pixels = 55*97
    width_ratio = 1
    height_ratio = 1
    mappings = {}
    img = None
    img_canvas = None

    def __init__(self, name):
        self.name = name
        self.canvas = self.label = self.id = None

    def attach(self, canvas, x=10, y=10):
        if canvas is self.canvas:
            self.canvas.coords(self.id, x, y)
            self.label.delete(self.adj)
            info = self.calculate()
            adj = info[0]
            self.adj = self.label.create_text(self.w/2, 3*self.h/4,
                                              text=str(round(adj, 2)))
            return
        if self.canvas:
            self.detach()
        if not canvas:
            return

        self.h = int((55 / 1293) * self.img_canvas.max_height)
        self.w = int((97 / 2273) * self.img_canvas.max_width)

        label = tk.Canvas(canvas, height=self.h,
                          width=self.w, highlightthickness=1)
        self.label_name = label.create_text(self.w/2, self.h/4, text=self.name)

        id = canvas.create_window(x, y, window=label, anchor="nw")
        self.canvas = canvas
        self.label = label
        self.id = id
        info = self.calculate()
        adj = info[0]
        self.adj = self.label.create_text(
            self.w/2, 3*self.h/4, text=str(round(adj, 2)))

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
        if self.img_canvas.selected is not None:
            self.img_canvas.selected.label.config(background="white")
        self.img_canvas.selected = self
        self.img_canvas.selected.label.config(background="red")
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
        if self.img_canvas.clicked_opt == True:
            self.img_canvas.manual_move = True
        x, y = self.canvas.coords(self.id)
        self.attach(self.canvas, x-1, y)

    def right(self, event):
        if self.img_canvas.clicked_opt == True:
            self.img_canvas.manual_move = True
        x, y = self.canvas.coords(self.id)
        self.attach(self.canvas, x+1, y)

    def up(self, event):
        if self.img_canvas.clicked_opt == True:
            self.img_canvas.manual_move = True
        x, y = self.canvas.coords(self.id)
        self.attach(self.canvas, x, y-1)

    def down(self, event):
        if self.img_canvas.clicked_opt == True:
            self.img_canvas.manual_move = True
        x, y = self.canvas.coords(self.id)
        self.attach(self.canvas, x, y+1)

    def optimize_lane(self):
        x, y = self.canvas.coords(self.id)
        x = int(x * self.width_ratio)
        y = int(y * self.height_ratio)

        max_adj = float("-inf")
        max_info = None

        # Find the max adjusted volume
        for i in range(x-10, x+10):
            for j in range(y-10, y+10):
                cur_calc = self.calculate(i, j)
                cur_adj = cur_calc[0]
                if max_adj < cur_adj:
                    max_info = cur_calc
                    max_adj = cur_adj

        x, y = max_info[3]

        x = int(x / self.width_ratio)
        y = int(y / self.height_ratio)

        self.canvas.coords(self.id, x, y)
        self.label.delete(self.adj)

        self.info = max_info
        adj_vol = max_info[0]
        self.adj = self.label.create_text(self.w/2, 3*self.h/4,
                                          text=str(round(adj_vol, 2)))
        return max_info

    def calculate(self, x=None, y=None):
        if x is None and y is None:
            x, y = self.canvas.coords(self.id)
            # convert x and y for original
            x = int(x * self.width_ratio)
            y = int(y * self.height_ratio)

        w = 97
        h = 55

        # crop image
        crop_img = self.img[y-1:y+h+1, x-1:x+w+1]

        min_vol = np.amin(crop_img[1:h+1, 1:w+1])
        max_vol = np.amax(crop_img[1:h+1, 1:w+1])
        vol = np.sum(crop_img[1:h+1, 1:w+1])
        sd = np.std(crop_img[1:h+1, 1:w+1])

        # Calculating average volume and standard deviation
        avg_vol = vol / (w*h)

        # Get mean background
        mean_b = 0
        for j in range(0, h+2):
            mean_b += crop_img[j, 0] + \
                crop_img[j, w+1]
        for i in range(1, w-1):
            mean_b += crop_img[0, i] + \
                crop_img[h+1, i]
        mean_b /= ((w+2) * 2) + (h * 2)

        # Calculate adjusted volume
        adj_vol = vol - (self.total_pixels * mean_b)

        info = (adj_vol, mean_b, vol, (x, y), min_vol, max_vol, avg_vol, sd)
        self.info = info
        return info


class ImageCanvas:

    def __init__(self, root, image_path, mappings, i_width, i_height):
        self.canvas = tk.Canvas(root, width=i_width, height=i_height)
        self.max_width = i_width
        self.max_height = i_height
        self.img_info = cv2.imread(image_path, -1)
        self.map = mappings

        i = self.map_uint16_to_uint8(self.img_info)
        im = Image.fromarray(i, mode="L")
        self.width_ratio = self.img_info.shape[1] / i_width
        self.height_ratio = self.img_info.shape[0] / i_height

        Lane.width_ratio = self.width_ratio
        Lane.height_ratio = self.height_ratio
        Lane.mappings = self.map
        Lane.img = np.vectorize(self.map.__getitem__)(self.img_info)
        Lane.img_canvas = self

        im = im.resize((i_width, i_height), Image.ANTIALIAS)
        self.img_label = ImageTk.PhotoImage(im)
        self.canvas.create_image(0, 0, image=self.img_label, anchor=NW)
        self.canvas.pack(fill=BOTH)

        self.lanes = []
        x = 20
        for i in range(20):
            lane = Lane("Lane"+str(i+1))
            lane.attach(self.canvas, x, self.max_height * (3/10))
            self.lanes.append(lane)
            x += lane.w + 5

        self.canvas.dnd_accept = self.dnd_accept
        self.clicked_opt = False
        self.manual_move = False
        self.selected = None

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
        if self.clicked_opt == True:
            self.manual_move = True
        self.dnd_leave(source, event)
        x, y = source.where(self.canvas, event)
        source.attach(self.canvas, x, y)
        self.selected = source
        # self.selected.label.config(highlightbackground="red")
        self.selected.label.focus_set()
        self.selected.label.bind('<Left>', source.left)
        self.selected.label.bind('<Right>', source.right)
        self.selected.label.bind('<Up>', source.up)
        self.selected.label.bind('<Down>', source.down)

    def add_lane(self):
        number = len(self.lanes) + 1
        lane = Lane("Lane" + str(number))
        lane.attach(self.canvas, self.max_width / 2, 40)
        self.lanes.append(lane)

    def remove_lane(self, event):
        source = self.selected
        self.selected = None
        for lane in self.lanes:
            if lane.name == source.name:
                self.lanes.remove(lane)
                source.detach()
                break
        i = 1
        for lane in self.lanes:
            lane.name = "Lane"+str(i)
            lane.label.delete(lane.label_name)
            lane.label_name = lane.label.create_text(
                lane.w/2, lane.h/4, text=lane.name)
            i += 1
        source.detach()

    def optimize_lanes(self):
        self.clicked_opt = True
        self.manual_move = False
        t = tk.Toplevel(self.canvas)
        progressbar = Progressbar(t,
                                  orient=HORIZONTAL, length=200, mode='determinate')
        progressbar.pack(fill=BOTH)
        progressbar['maximum'] = len(self.lanes) - 1
        i = 0
        for lane in self.lanes:
            lane.optimize_lane()
            i += 1
            progressbar['value'] = i
            progressbar.update()
        t.destroy()
