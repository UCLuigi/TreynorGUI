#!/usr/bin/env python

#version history
#v1.00  Luis Alba   first release
#v1.01  Luis Alba   autopopulate box width and height modals with current values
#v1.02  LA/TT       fix bug that prevented analyzing some gel images
#                   add file name, username, datetime to exported table
#v1.03  TT          replaced "Treynor" at top of session window with name of opened file (and "MM Gel Densitometry Platform" otherwise)
#                   current version number is accessible from File menu


version = "v1.05"

from tkinter import *
import os
from tkinter import filedialog, messagebox, simpledialog
import cv2
import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
import cv2
from tkinter.ttk import Progressbar
from tkinter import messagebox
from time import sleep
from time import localtime, strftime
import getpass


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("MM Gel Densitometry Platform, Version "+version)
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.image_canvas = None

        self.root.geometry(str(self.screen_width)+"x"+str(self.screen_height))
        self.root.configure(background='grey')
        menubar = Menu(root)

        # File menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open file", command=self.look_up_image)
        filemenu.add_command(label="Optimize Adj Vol",
                             command=self.optimize_boxes)
        filemenu.add_command(label="Export table", command=self.export)
        filemenu.add_separator()
        filemenu.add_command(label="You're using Version "+version)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Edit menu
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Add box", command=self.create_box)
        editmenu.add_command(label="Add multiple boxes", command=self.create_multiple_boxes)
        editmenu.add_command(label="Change dimensions of all boxes", command=self.change_boxes_dimensions)
        editmenu.add_command(label="Change dimensions of selected box", command=self.change_selected_box_dimension)
        editmenu.add_command(label="Flash boxes", command=self.flash_boxes)
        menubar.add_cascade(label="Edit", menu=editmenu)
        root.bind('<f>', self.flash_once)

        root.config(menu=menubar)

    def look_up_image(self):
        '''
        Function that looks for a tif image given an scn file.
        Error checks if it doesn't find image and if it's not 16-bit.
        '''
        # Check if image is uploaded already
        if self.image_canvas is not None:
            answer = messagebox.askokcancel(
                'Override', "You have already uploaded an image, would you like to override it?")
            if answer == True:
                for box in self.image_canvas.boxes:
                    box.detach()
                self.topframe.destroy()
            else:
                return

        file_path = filedialog.askopenfilename(filetypes=(("Scn files", "*.scn"),
                                                          ("All Files", "*.*")),
                                               title="Choose an scn file."
                                               )
        # Check if pressed cancel
        if file_path == '':
            return

        img_path = file_path[:-3] + "tif"
        # Check if image exists
        if not os.path.exists(img_path):
            messagebox.showerror(
                "Error", "Couldn't find .tif file with same name in same folder as selected .scn file.\n\n(1) Open selected .scn file in ImageLab.\n(2) Select File > Export > Export for Analysis.\n(3) Save 16-bit .tif file with same name and in same folder as selected .scn file.\n(4) Try again.")
            return

        img = cv2.imread(img_path, -1)
        # Check if image is 16 bits
        if img.dtype != 'uint16':
            messagebox.showerror(
                "Error", "Matching .tif file was found with same name in same folder, but it is not 16-bit.\n\n(1) Delete matching .tif file with wrong resolution.\n(2) Open selected .scn file in ImageLab.\n(3) Select File > Export > Export for Analysis.\n(4) Save 16-bit .tif file with same name and in same folder as selected .scn file.\n(5) Try again.\n\nIf problem persists, re-boot ImageLab and try sequence again.")
            return

        self.scn_file = file_path
        self.img_path = img_path
        self.img = img
        self.root.title(file_path.split("/")[-1])
        self.mappings = {}

        # Parse scn file
        with open(file_path, encoding="utf8", errors='ignore') as f:
            self.mappings[0] = float(0)
            for line in f:
                l = line.lstrip().rstrip()
                if l[:6] == '<table':
                    find_c = l.find('>')
                    l = l[find_c + 1:-8]
                    nums = l.split()
                    i = 1
                    for num in nums:
                        self.mappings[i] = float(num)
                        i += 1
                if l[:17] == '<scan_resolution>':
                    l = l[17:-18]
                    self.scale = float(l)
                if l[:9] == '<size_pix':
                    l = l.split("\"")
                    # print(l)
                    self.img_height = int(l[1])
                    self.img_width = int(l[-2])
                
                
        self.setup()

    def setup(self):
        '''
        Sets up the window with the ImageCanvas and boxes
        Creates a table
        '''
        self.topframe = Frame(
            self.root, width=self.screen_width, height=self.screen_height)
        self.topframe.pack(fill=BOTH)
        self.image_canvas = ImageCanvas(self.topframe, self.img_path, self.mappings,
                                        self.screen_width,self.screen_height,
                                        self.img_width, self.img_height)

    def create_box(self):
        '''
        Action from menu to add a box onto the ImageCanvas
        '''
        # Check if image was uploaded
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        self.image_canvas.add_box()

    def create_multiple_boxes(self):
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        number = simpledialog.askinteger("Input", "How many boxes?",
                                 parent=self.root,
                                 minvalue=1, maxvalue=20)
        if number is not None:
            self.image_canvas.add_box(number)
    
    def change_boxes_dimensions(self):
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        height = simpledialog.askinteger("Input", "How many pixels for the height?",
                                 parent=self.root,
                                 initialvalue=self.image_canvas.boxes[0].h_actual,
                                 minvalue=1, maxvalue=self.screen_height)
        if height is None:
            return
        width = simpledialog.askinteger("Input", "How many pixels for the width?",
                                 parent=self.root,
                                 initialvalue=self.image_canvas.boxes[0].w_actual,
                                 minvalue=1, maxvalue=self.screen_width)
        if width is None:
            return
        if width is not None and height is not None:
            self.image_canvas.change_box_dimensions(height,width)
            return

    def change_selected_box_dimension(self):
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        if self.image_canvas.selected is None:
            messagebox.showerror('Error', 'Please select a box first')
            return
        height = simpledialog.askinteger("Input", "How many pixels for the height?",
                                 parent=self.root,
                                 initialvalue=self.image_canvas.selected.h_actual,
                                 minvalue=1, maxvalue=self.screen_height)
        if height is None:
            return
        width = simpledialog.askinteger("Input", "How many pixels for the width?",
                                 parent=self.root,
                                 initialvalue=self.image_canvas.selected.w_actual,
                                 minvalue=1, maxvalue=self.screen_width)
        if width is None:
            return
        if width is not None and height is not None:
            self.image_canvas.change_selected_box_dimension(height,width)
            return

    def optimize_boxes(self):
        '''
        Action from menu to optimize volume of all boxes
        '''
        # Check if image was uploaded
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        # Check if there are boxes
        if len(self.image_canvas.boxes) == 0:
            messagebox.showerror('Error',
                                 'There are no boxes to optimize, you need to add boxes first')
            return

        self.image_canvas.optimize_boxes()

    def flash_boxes(self):
        # Check if image was uploaded
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        # Check if there are boxes
        if len(self.image_canvas.boxes) == 0:
            messagebox.showerror('Error',
                                 'There are no boxes to flash, you need to add boxes first')
            return
        t = tk.Toplevel(self.root)
        label = tk.Label(t, text="Flashing")
        label.pack(fill=BOTH)
        progressbar = Progressbar(t,
                                  orient=HORIZONTAL, length=100, mode='determinate')
        progressbar['maximum'] = 10
        progressbar.pack(fill=BOTH)
        for i in range(10):
            self.image_canvas.flash_boxes()
            progressbar['value'] = i + 1
            progressbar.update()
        t.destroy()

    def flash_once(self, event):
        # Check if image was uploaded
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        # Check if there are boxes
        if len(self.image_canvas.boxes) == 0:
            messagebox.showerror('Error',
                                 'There are no boxes to flash, you need to add boxes first')
            return
        self.image_canvas.flash_boxes()

    def export(self):
        '''
        Action from menu to export information into a table
        '''
        # Check if image was uploaded
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        # Check if there are boxes
        if len(self.image_canvas.boxes) == 0:
            messagebox.showerror('Error',
                                 'There are no boxes to export, you need to add boxes first')
            return
        # Check if pressed optimized and manually moved
        if self.image_canvas.clicked_opt == True and self.image_canvas.manual_move == True:
            answer = messagebox.askokcancel('Export', 
                                            'You have manually moved boxes since optimizing boxes. Are you sure you want to export anyways?')
            if answer == False:
                return

        if self.image_canvas.clicked_opt == False:
            answer = messagebox.askokcancel('Export', 
                                            'You have not optimized boxes. Are you sure you want to export anyways?')
            if answer == False:
                return
        
        # Save file with name
        name = self.scn_file[:-4].split("/")[-1]
        f = filedialog.asksaveasfile(initialfile=name, mode="w", defaultextension=".csv")
        if f is None:
            return

        columns = [ 'Filename',
                    'No.',
                    'Username',
                    'Date',
                    'Label',
                    'Type',
                    'Volume (OD)',
                    'Adj. Vol. (OD)',
                    'Mean Bkgd. (OD)',
                    'Abs. Quant.',
                    'Rel. Quant.',
                    '# of Pixels',
                    'Min. Value (OD)',
                    'Max. Value (OD)',
                    'Mean Value (OD)',
                    'Std. Dev.',
                    'Area (mm2)',
                    'X (pixels)',
                    'Y (pixels)',
                    'width (pixels)',
                    'height (pixels)',
                    'program version'
                ]
        column_str = ",".join(columns) + "\n"
        f.write(column_str)

        filename = f.name.split("/")[-1]
        username = getpass.getuser()
        date = strftime("%m/%d/%Y %H:%M", localtime())
        t = "Unknown"
        a_quant = r_quant = "N/A"

        # Loop through all boxes
        for box in self.image_canvas.boxes:
            label = box.name
            w = box.w_actual
            h = box.h_actual
            total_pixels = w*h
            area = ((self.scale/1000)**2) * (w*h)
            num = label[3:]
            adj, mean_b, vol, x_y, min_vol, max_vol, avg_vol, sd = box.info
            x,y = x_y
            r = [filename,num,username,date,label,t,vol,adj,mean_b,a_quant,r_quant,total_pixels,
                    min_vol,max_vol,avg_vol,sd,area,x,y,w,h,version]
            row = list(map(str, r))
            row_str = ",".join(row) + "\n"
            f.write(row_str)

        f.close()
        messagebox.showinfo('Success', 'Table information exported')

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


class Box:

    total_pixels = 55*97
    width_ratio = 1
    height_ratio = 1
    mappings = {}
    img = None
    img_canvas = None

    def __init__(self, name):
        self.name = name
        self.canvas = self.label = self.id = None

    def attach(self, canvas, x=10, y=10, box_height=55, box_width=97, info=None):
        if canvas is self.canvas:
            self.canvas.coords(self.id, x, y)
            self.x = x
            self.y = y
            self.label.delete(self.adj)
            info = self.calculate()
            adj = info[0]
            self.adj = self.label.create_text(self.w/2, 3*self.h/4,
                                              text=str(round(adj, 2)), font=("Purisa", 8))
            return
        if self.canvas:
            self.detach()
        if not canvas:
            return

        self.h = int((box_height / self.img_canvas.actual_img_height) * self.img_canvas.max_height)
        self.h_actual = box_height
        self.w = int((box_width / self.img_canvas.actual_img_width) * self.img_canvas.max_width)
        self.w_actual = box_width

        self.total_pixels = self.h_actual * self.w_actual

        label = tk.Canvas(canvas, height=self.h,
                          width=self.w, highlightthickness=1, highlightbackground="black")
        self.label_name = label.create_text(
            self.w/2, self.h/4, text=self.name, font=("Purisa", 10))

        id = canvas.create_window(x, y, window=label, anchor="nw")
        self.x = x
        self.y = y
        self.canvas = canvas
        self.label = label
        self.id = id

        if info is not None:
            self.info = info
            adj = info[0]
        else:
            info = self.calculate()
            adj = info[0]

        self.adj = self.label.create_text(
            self.w/2, 3*self.h/4, text=str(round(adj, 2)), font=("Purisa", 8))
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
        self.label.bind('<BackSpace>', self.img_canvas.remove_box)

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
        x = event.x_root - x_org + 1
        y = event.y_root - y_org + 1
        # x = event.x_root - x_org
        # y = event.y_root - y_org
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

    def optimize_box(self):
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

        self.x = x
        self.y = y

        self.canvas.coords(self.id, x, y)
        self.label.delete(self.adj)

        self.info = max_info
        adj_vol = max_info[0]
        self.adj = self.label.create_text(self.w/2, 3*self.h/4,
                                          text=str(round(adj_vol, 2)), font=("Purisa", 8))
        return max_info

    def calculate(self, x=None, y=None):
        if x is None and y is None:
            x, y = self.canvas.coords(self.id)
            # convert x and y for original
            x = int(x * self.width_ratio)
            y = int(y * self.height_ratio)

        w = self.w_actual
        h = self.h_actual

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

    def __init__(self, root, image_path, mappings, i_width, i_height, img_width, img_height):
        self.canvas = tk.Canvas(root, width=i_width, height=i_height)
        self.max_width = i_width
        self.max_height = i_height
        self.actual_img_width = img_width
        self.actual_img_height = img_height
        self.img_info = cv2.imread(image_path, -1)
        self.img_info[self.img_info > 65309] = float(3.654)
        self.map = mappings

        i = self.map_uint16_to_uint8(self.img_info)
        im = Image.fromarray(i, mode="L")
        self.width_ratio = self.img_info.shape[1] / i_width
        self.height_ratio = self.img_info.shape[0] / i_height

        Box.width_ratio = self.width_ratio
        Box.height_ratio = self.height_ratio
        Box.mappings = self.map
        Box.img = np.vectorize(self.map.__getitem__)(self.img_info)
        Box.img_canvas = self

        im = im.resize((i_width, i_height), Image.ANTIALIAS)
        self.img_label = ImageTk.PhotoImage(im)
        self.canvas.create_image(0, 0, image=self.img_label, anchor=NW)
        self.canvas.pack(fill=BOTH)

        self.boxes = []
        x = 20
        for i in range(20):
            box = Box("Box"+str(i+1))
            box.attach(self.canvas, x, int(self.max_height * (3/10)))
            self.boxes.append(box)
            x += box.w + 5

        self.canvas.dnd_accept = self.dnd_accept
        self.clicked_opt = False
        self.manual_move = False
        self.selected = None
        self.top = None
        self.box_height = 55
        self.box_width = 97

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
        self.selected.label.focus_set()
        self.selected.label.bind('<Left>', source.left)
        self.selected.label.bind('<Right>', source.right)
        self.selected.label.bind('<Up>', source.up)
        self.selected.label.bind('<Down>', source.down)

    def add_box(self, num=1):
        x = 20
        for i in range(num):
            number = len(self.boxes) + 1
            box = Box("Box" + str(number))
            box.attach(self.canvas, x, 40, self.box_height, self.box_width)
            x += box.w + 10
            self.boxes.append(box)

    def remove_box(self, event):
        source = self.selected
        self.selected = None
        for box in self.boxes:
            if box.name == source.name:
                self.boxes.remove(box)
                source.detach()
                break
        i = 1
        for box in self.boxes:
            box.name = "Box"+str(i)
            box.label.delete(box.label_name)
            box.label_name = box.label.create_text(
                box.w/2, box.h/4, text=box.name, font=("Purisa", 10))
            i += 1
        source.detach()

    def optimize_boxes(self):
        if self.top is not None:
            self.top.destroy()
            self.top = None
        self.clicked_opt = True
        self.manual_move = False
        t = tk.Toplevel(self.canvas)
        label = tk.Label(t, text="Optimizing")
        label.pack(fill=BOTH)
        progressbar = Progressbar(t,
                                  orient=HORIZONTAL, length=200, mode='determinate')
        progressbar.pack(fill=BOTH)
        progressbar['maximum'] = len(self.boxes) - 1
        i = 0
        opt_bool = True
        for box in self.boxes:
            old_info = box.info
            box.optimize_box()
            new_info = box.info
            i += 1
            progressbar['value'] = i
            progressbar.update()
            if old_info != new_info:
                opt_bool = False
        t.destroy()
        if opt_bool == True:
            messagebox.showinfo(
                'Converged', "Optimization has converged. Click OK to continue.")
        else:
            answer = messagebox.askokcancel('Has not converged', 'Click \"OK\" to test for convergence.\nClick \"Cancel\" to leave boxes where they are.')
            if answer == True:
                self.optimize_boxes()
            
            # self.top = tk.Toplevel(self.canvas)
            # Label(self.top, text="Click \"Repeat Optimization\" to test for convergence. Click \"OK\" to leave boxes where they are.").pack()
            # r = Button(self.top, text="Repeat Optimization",
            #            command=self.optimize_boxes,highlightbackground='#3E4149')
            # r.pack()
            # ok = Button(self.top, text="OK", command=self.ok, bg="blue",highlightbackground='#3E4149')
            # ok.focus_set()
            # ok.bind('<Return>', self.ok)
            # ok.pack()

    # def ok(self, event=None):
    #     self.top.destroy()
    #     self.top = None

    def change_box_dimensions(self, box_height, box_width):
        self.box_height = box_height
        self.box_width = box_width
        for box in self.boxes:
            box.detach()
            box.attach(self.canvas, box.x, box.y, box_height, box_width)

    def change_selected_box_dimension(self, box_height, box_width):
        for box in self.boxes:
            if box.name == self.selected.name:
                box.detach()
                box.attach(self.canvas, box.x, box.y, box_height, box_width)
                break

    def flash_boxes(self):
        progressbar = Progressbar(self.canvas,
                                  orient=HORIZONTAL, length=100, mode='determinate')
        progressbar['maximum'] = 1

        for box in self.boxes:
            box.detach()
        sleep(0.25)
        progressbar['value'] = 1
        progressbar.update()
        for box in self.boxes:
            box.attach(self.canvas, box.x, box.y, box.h_actual, box.w_actual, box.info)
        sleep(0.25)

if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()