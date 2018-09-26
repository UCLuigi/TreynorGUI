from tkinter import *
import os
import numpy as np
from PIL import ImageTk, Image
from tkinter import filedialog, dnd, messagebox
import cv2
import xml.etree.ElementTree
from drag import *


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Treynor")
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.root.geometry(str(self.screen_width)+"x"+str(self.screen_height))
        self.root.configure(background='grey')

        menubar = Menu(root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open file", command=self.look_up_image)
        filemenu.add_command(label="Optomize Adj Vol",
                             command=self.optimize_lanes)
        filemenu.add_command(label="Export table", command=self.export)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Add lane", command=self.create_lane)
        menubar.add_cascade(label="Edit", menu=editmenu)

        root.config(menu=menubar)

        # self.upload_button = Button(root,
        #                             text="Upload .scn file",
        #                             command=self.look_up_image
        #                             )
        # self.upload_button.bind('<Button 1>', self.look_up_image)
        # self.upload_button.pack(fill=X)

    def look_up_image(self):
        '''
        Function that looks for a tif image given an scn file.
        Error checks if it doesn't find image and if it's not 16-bit.
        '''
        file_path = filedialog.askopenfilename(filetypes=(("Scn files", "*.scn"),
                                                          ("All Files", "*.*")),
                                               title="Choose a file."
                                               )
        if file_path != '':
            img_path = file_path[:-3] + "tif"
            if not os.path.exists(img_path):
                messagebox.showerror(
                    "Error", "You should name your scn file and your tif image the same")
            else:
                img = cv2.imread(img_path, -1)
                if img.dtype != 'uint16':
                    messagebox.showerror(
                        "Error", "You need to export 16-bit image...")
                else:
                    self.scn_file = file_path
                    self.img_path = img_path
                    self.img = img
                    # e = xml.etree.ElementTree.parse(file_path).getroot()
                    self.mappings = {}
                    path_map = path_map = "./16bit_calibration.dat"

                    with open(path_map, "r") as map_f:
                        for line in map_f:
                            intensity, volume = line.rstrip().split(",")
                            self.mappings[intensity] = float(volume)

                    self.setup()

                    # e = xml.etree.ElementTree.parse().getroot()
                    # with open(file_path, "r") as f:
                    #     for line in f:
                    #         print(line)

                    # self.img = img
                    # # self.upload_button.pack_forget()

                    # self.topframe = Frame(self.root)
                    # self.topframe.pack(fill=BOTH)

                    # self.bottomframe = Frame(self.root)
                    # self.bottomframe.pack(fill=BOTH, side=BOTTOM)
                    # self.label = Label(self.bottomframe, "Lanes")
                    # self.label2 = Label(self.bottomframe, "Adjusted Volume")

                    # self.label.grid(row=0,column=0)
                    # self.label2.grid(row=1, column=0)

                    # self.bottomframe = VerticalScrolledFrame(self.root)
                    # self.bottomframe.pack(side=BOTTOM)

                    # create the canvas, size in pixels
                    # self.canvas = Canvas(self.topframe, width=1200, height=800)

                    # # pack the canvas into a frame/form
                    # self.canvas.pack(fill=BOTH)

                    # def map_uint16_to_uint8(img, lower_bound=None, upper_bound=None):
                    #     '''
                    #     Map a 16-bit image trough a lookup table to convert it to 8-bit.

                    #     Parameters
                    #     ----------
                    #     img: numpy.ndarray[np.uint16]
                    #         image that should be mapped
                    #     lower_bound: int, optional
                    #         lower bound of the range that should be mapped to ``[0, 255]``,
                    #         value must be in the range ``[0, 65535]`` and smaller than `upper_bound`
                    #         (defaults to ``numpy.min(img)``)
                    #     upper_bound: int, optional
                    #     upper bound of the range that should be mapped to ``[0, 255]``,
                    #     value must be in the range ``[0, 65535]`` and larger than `lower_bound`
                    #     (defaults to ``numpy.max(img)``)

                    #     Returns
                    #     -------
                    #     numpy.ndarray[uint8]
                    #     '''
                    #     if lower_bound is not None and not(0 <= lower_bound < 2**16):
                    #         raise ValueError(
                    #             '"lower_bound" must be in the range [0, 65535]')
                    #     if upper_bound is not None and not(0 <= upper_bound < 2**16):
                    #         raise ValueError(
                    #             '"upper_bound" must be in the range [0, 65535]')
                    #     if lower_bound is None:
                    #         lower_bound = np.min(img)
                    #     if upper_bound is None:
                    #         upper_bound = np.max(img)
                    #     if lower_bound >= upper_bound:
                    #         raise ValueError(
                    #             '"lower_bound" must be smaller than "upper_bound"')
                    #     lut = np.concatenate([
                    #         np.zeros(lower_bound, dtype=np.uint16),
                    #         np.linspace(0, 255, upper_bound -
                    #                     lower_bound).astype(np.uint16),
                    #         np.ones(2**16 - upper_bound, dtype=np.uint16) * 255
                    #     ])
                    #     return lut[img].astype(np.uint8)

                    # i = map_uint16_to_uint8(self.img)

                    # # load the .gif image file
                    # # image = tk.PhotoImage(file=img_path)
                    # # i = self.img.astype(np.uint8)

                    # # im = Image.open(img_path)
                    # im = Image.fromarray(i, mode="L")
                    # # table=[ i/256 for i in range(65536) ]
                    # # im2 = im.point(table,'L')

                    # im = im.resize((1000, 700), Image.ANTIALIAS)

                    # # imarray = np.array(im)
                    # # np.set_printoptions(threshold=np.inf)
                    # # print(imarray.shape)
                    # # print(imarray)

                    # # Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
                    # self.img_label = ImageTk.PhotoImage(im)

                    # # put gif image on canvas
                    # # pic's upper left corner (NW) on the canvas is at x=50 y=10
                    # self.canvas.create_image(
                    #     0, 0, image=self.img_label, anchor=NW)
                    # panel = Label(canvas, image = img)

                    # self.rect = Button(self.bottomframe,
                    # 	               text="Lane 1")
                    # button1_window = self.canvas.create_window(120, 325, anchor=NW, window=self.rect)
                    # #self.rect.bind('<Button 1>', self.trial)

                    # notesFrame = DnDFrame(self.topframe, bd=3, bg="blue")
                    # notesFrame.place(x=10, y=10)
                    # notes = Label(notesFrame, text="Lane 1")
                    # notes.pack()

                    # c = Canvas(self.canvas, width=97, height=57,
                    #            highlightthickness=4, highlightbackground="blue")
                    # # t_i = cv2.imread('trans.jpg')
                    # # t_img = Image.fromarray(t_i)
                    # t_img = Image.open('trans.png')
                    # ph = ImageTk.PhotoImage(t_img)
                    # self.ph = ph
                    # t_img = t_img.resize((57, 97), Image.ANTIALIAS)
                    # new('RGBA', (97, 57), (0, 0, 0, 0))
                    # c.create_image(0, 0, image=self.ph, anchor=NW)
                    # c.create_text(30, 30, fill="blue", text="Lane 1")
                    # c.place(x=10, y=10)
                    # dnd = DragManager()
                    # dnd.add_dragable(self.rect)

                    # dnd.dnd_start(self.rect)
                    # t1 = Tester(self.canvas)
                    # lane1 = Lane(10, 10)
                    # lane1.attach(t1.canvas)

                    # self.rect = Canvas(self.root, width=97, height=57)
                    # self.rect.create_image(0,0, image=self.img)
                    # #rect = self.canvas.create_rectangle(300, 350, 397, 407)
                    # self.rect.bind('<Button 1>', self.trial)
                    # self.rect.pack()
                    # dnd.dnd_start(self.rect, self.trial)

    def setup(self):
        self.topframe = Frame(self.root)
        self.topframe.pack(fill=BOTH)
        # self.bottomframe = Frame(self.root)
        # self.bottomframe.pack()
        self.image_canvas = ImageCanvas(self.topframe, self.img_path)
        self.lanes = []
        # x = 0
        # for i in range(20):
        #     lane = Lane("Lane"+str(i+1))
        #     lane.attach(self.image_canvas.canvas, 10 + x, 30)
        #     x += 25
        #     self.lanes.append(lane)

    def create_lane(self):
        number = len(self.lanes) + 1
        lane = Lane("Lane" + str(number))
        lane.attach(self.image_canvas.canvas, self.screen_width / 2, 40)
        self.lanes.append(lane)

    def optimize_lanes(self):
        pass

    def export(self):
        pass

    # def trial(event):
    #     print("Mouse clicked")
    #     print("clicked at ", event.x, event.y)


# class Lane:

#     def __init__(self, x, y):
#         # self.id = number
#         self.x = x
#         self.y = y
#         self.canvas = self.label = self.id = None

#     def attach(self, canvas):
#         if canvas is self.canvas:
#             self.canvas.coords(self.id, self.x, self.y)
#             return
#         if self.canvas:
#             self.detach()
#         if not canvas:
#             return
#         label = Label(canvas, text="Lane",
#                       borderwidth=2, relief="raised")
#         id = canvas.create_window(self.x, self.y, window=label, anchor="nw")
#         self.canvas = canvas
#         self.label = label
#         self.id = id
#         self.label.bind("<ButtonPress>", self.press)

#     def detach(self):
#         canvas = self.canvas
#         if not canvas:
#             return
#         id = self.id
#         label = self.label
#         self.canvas = self.label = self.id = None
#         canvas.delete(id)
#         label.destroy()

#     def press(self, event):
#         if dnd.dnd_start(self, event):
#             # where the pointer is relative to the label widget:
#             self.x_off = event.x
#             self.y_off = event.y
#             # where the widget is relative to the canvas:
#             self.x_orig, self.y_orig = self.canvas.coords(self.id)

#     def move(self, event):
#         x, y = self.where(self.canvas, event)
#         self.canvas.coords(self.id, x, y)

#     def putback(self):
#         self.canvas.coords(self.id, self.x_orig, self.y_orig)

#     def where(self, canvas, event):
#         # where the corner of the canvas is relative to the screen:
#         x_org = canvas.winfo_rootx()
#         y_org = canvas.winfo_rooty()
#         # where the pointer is relative to the canvas widget:
#         x = event.x_root - x_org
#         y = event.y_root - y_org
#         # compensate for initial pointer offset
#         return x - self.x_off, y - self.y_off

#     def dnd_end(self, target, event):
#         pass

#     def find_opt(self):
#         pass


# class Tester:

#     def __init__(self, root):
#         self.top = Toplevel(root)
#         self.canvas = Canvas(self.top, width=100, height=100)
#         self.canvas.pack(fill="both", expand=1)
#         self.canvas.dnd_accept = self.dnd_accept

#     def dnd_accept(self, source, event):
#         return self

#     def dnd_enter(self, source, event):
#         self.canvas.focus_set()  # Show highlight border
#         x, y = source.where(self.canvas, event)
#         x1, y1, x2, y2 = source.canvas.bbox(source.id)
#         dx, dy = x2-x1, y2-y1
#         self.dndid = self.canvas.create_rectangle(x, y, x+dx, y+dy)
#         self.dnd_motion(source, event)

#     def dnd_motion(self, source, event):
#         x, y = source.where(self.canvas, event)
#         x1, y1, x2, y2 = self.canvas.bbox(self.dndid)
#         self.canvas.move(self.dndid, x-x1, y-y1)

#     def dnd_leave(self, source, event):
#         self.top.focus_set()  # Hide highlight border
#         self.canvas.delete(self.dndid)
#         self.dndid = None

#     def dnd_commit(self, source, event):
#         self.dnd_leave(source, event)
#         x, y = source.where(self.canvas, event)
#         source.attach(self.canvas, x, y)


if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()
