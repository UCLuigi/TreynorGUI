from tkinter import *
import os
import numpy as np
from PIL import ImageTk, Image
from tkinter import filedialog, dnd, messagebox
import cv2
import xml.etree.ElementTree


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Project")
        self.root.geometry("800x800")
        self.root.configure(background='grey')
        self.upload_button = Button(root,
                                    text="Upload .scn file",
                                    command=self.look_up_image
                                    )
        self.upload_button.bind('<Button 1>', self.look_up_image)
        self.upload_button.pack(fill=X)

    def look_up_image(self, event):
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
                if img.dtype == 'uint16':
                    messagebox.showerror(
                        "Error", "You need to export 16-bit image...")
                else:
                    #e = xml.etree.ElementTree.parse(file_path).getroot()
                    self.mappings = {}

                    self.img = img
                    self.upload_button.pack_forget()

                    self.topframe = Frame(self.root, bg="green")
                    self.topframe.pack(fill=BOTH)

                    self.bottomframe = Frame(self.root, bg="blue")
                    self.bottomframe.pack(fill=BOTH, side=BOTTOM)
                    # self.label = Label(self.bottomframe, "Lanes")
                    # self.label2 = Label(self.bottomframe, "Adjusted Volume")

                    # self.label.grid(row=0,column=0)
                    # self.label2.grid(row=1, column=0)

                    # self.bottomframe = VerticalScrolledFrame(self.root)
                    # self.bottomframe.pack(side=BOTTOM)

                    # create the canvas, size in pixels
                    self.canvas = Canvas(self.topframe, width=1200, height=800)

                    # pack the canvas into a frame/form
                    self.canvas.pack(fill=BOTH)

                    # load the .gif image file
                    # image = tk.PhotoImage(file=img_path)
                    i = self.img.astype(np.uint8)

                    im = Image.open(img_path)
                    # im = Image.fromarray(i, mode="RGB")
                    # table=[ i/256 for i in range(65536) ]
                    # im2 = im.point(table,'L')

                    im = im.resize((1000, 700), Image.ANTIALIAS)

                    # imarray = np.array(im)
                    # np.set_printoptions(threshold=np.inf)
                    # print(imarray.shape)
                    # print(imarray)

                    # Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
                    self.img_label = ImageTk.PhotoImage(im)

                    # put gif image on canvas
                    # pic's upper left corner (NW) on the canvas is at x=50 y=10
                    self.canvas.create_image(
                        0, 0, image=self.img_label, anchor=NW)
                    # panel = Label(canvas, image = img)

                    # self.rect = Button(self.bottomframe,
                    # 	               text="Lane 1")
                    # button1_window = self.canvas.create_window(120, 325, anchor=NW, window=self.rect)
                    # #self.rect.bind('<Button 1>', self.trial)

                    notesFrame = DnDFrame(self.topframe, bd=5, bg="blue")
                    notesFrame.place(x=10, y=10)
                    notes = Label(notesFrame, text="Lane 1")
                    notes.pack()

                    # dnd = DragManager()
                    # dnd.add_dragable(self.rect)

                    # dnd.dnd_start(self.rect)

                    # self.rect = Canvas(self.root, width=97, height=57)
                    # self.rect.create_image(0,0, image=self.img)
                    # #rect = self.canvas.create_rectangle(300, 350, 397, 407)
                    self.rect.bind('<Button 1>', self.trial)
                    self.rect.pack()
                    dnd.dnd_start(self.rect, self.trial)

    def trial(event):
        print("Mouse clicked")
        print("clicked at ", event.x, event.y)


class DragDropWidget:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.drag_start_x = 0
        self.drag_start_y = 0
        self.bind("<Button-1>", self.drag_start)
        self.bind("<B1-Motion>", self.drag_motion)

    def drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag_motion(self, event):
        x = self.winfo_x() - self.drag_start_x + event.x
        y = self.winfo_y() - self.drag_start_y + event.y
        self.place(x=x, y=y)


class DnDFrame(DragDropWidget, Frame):
    pass


# class DragManager():
#     def add_dragable(self, widget):
#         widget.bind("<ButtonPress-1>", self.on_start)
#         widget.bind("<B1-Motion>", self.on_drag)
#         widget.bind("<ButtonRelease-1>", self.on_drop)
#         # widget.configure(cursor="hand1")

#     def on_start(self, event):
#         # you could use this method to create a floating window
#         # that represents what is being dragged.
#         # self.drag_start_x = event.x
#         # self.drag_start_y = event.y
#         pass

#     def on_drag(self, event):
#         # you could use this method to move a floating window that
#         # represents what you're dragging
#         # x = self.winfo_x() - self.drag_start_x + event.x
#         # y = self.winfo_y() - self.drag_start_y + event.y
#         # self.place(x=x, y=y)
#         pass

#     def on_drop(self, event):
#         # find the widget under the cursor
#         x, y = event.widget.winfo_pointerxy()
#         target = event.widget.winfo_containing(x, y)
#         try:
#             target.configure(image=event.widget.cget("image"))
#         except:
#             pass

    # #The Pack geometry manager packs widgets in rows or columns.
    # panel.pack(side = "bottom", fill = "both", expand = "yes")

    # def draw_rectangles():
    # 	self.canvas.create_rectangle(100, 100, 197, 157, fill='red')


class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """

    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


#file_path = filedialog.askopenfilename()
# # Code to add widgets will go here...
# w = tk.Canvas(root, height=250, width=300)
# filename = PhotoImage(file = "sunshine.gif")
# image = canvas.create_image(50, 50, anchor=NE, image=filename)
# w.pack()
if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()
