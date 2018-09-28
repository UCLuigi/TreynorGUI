from tkinter import *
import os
from tkinter import filedialog, messagebox
import cv2
from drag import *


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Treynor")
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.image_height = int(self.screen_height * (8/10))
        self.root.geometry(str(self.screen_width)+"x"+str(self.screen_height))
        self.root.configure(background='grey')
        menubar = Menu(root)

        # File menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open file", command=self.look_up_image)
        filemenu.add_command(label="Optomize Adj Vol",
                             command=self.optimize_lanes)
        filemenu.add_command(label="Export table", command=self.export)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Edit menu
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
                                               title="Choose an scn file."
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
                    self.mappings = {}
                    path_map = "./16bit_calibration.dat"
                    with open(path_map, "r") as map_f:
                        for line in map_f:
                            intensity, volume = line.rstrip().split(",")
                            self.mappings[intensity] = float(volume)

                    self.setup()

    def setup(self):
        '''
        Sets up the window with the ImageCanvas and Lanes
        Creates a table
        '''
        self.topframe = Frame(
            self.root, width=self.screen_width, height=self.image_height)
        self.topframe.pack(fill=BOTH)
        self.bottomframe = Frame(self.root)
        self.bottomframe.pack(fill=BOTH, side=BOTTOM)
        self.image_canvas = ImageCanvas(
            self.topframe, self.img_path, self.mappings, self.screen_width, self.image_height)
        self.lanes = []
        x = 0
        # for i in range(20):
        #     lane = Lane("Lane"+str(i+1))
        #     lane.attach(self.image_canvas.canvas, 10 + x, 40)
        #     # self.image_canvas.add_lane()
        #     x += 65
        # self.lanes.append(lane)

    def create_lane(self):
        '''
        Action from menu to add a lane onto the ImageCanvas
        '''
        number = len(self.lanes) + 1
        lane = Lane("Lane" + str(number))
        lane.attach(self.image_canvas.canvas, self.screen_width / 2, 40)
        self.lanes.append(lane)

    def optimize_lanes(self):
        '''
        Action from menu to optimize volume of all lanes
        '''
        # self.image_canvas.optimize_lanes()
        pass

    def export(self):
        '''
        Action from menu to export information into a table
        '''
        # self.lanes is None
        # throw error
        # else
        # start creating table
        pass


if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()
