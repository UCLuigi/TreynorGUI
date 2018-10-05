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
        self.image_canvas = None

        self.root.geometry(str(self.screen_width)+"x"+str(self.screen_height))
        self.root.configure(background='grey')
        menubar = Menu(root)

        # File menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open file", command=self.look_up_image)
        filemenu.add_command(label="Optimize Adj Vol",
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
                for lane in self.image_canvas.lanes:
                    lane.detach()
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
                "Error", "You should name your scn file and your tif image the same")
            return

        img = cv2.imread(img_path, -1)
        # Check if image is 16 bits
        if img.dtype != 'uint16':
            messagebox.showerror(
                "Error", "You need to export 16-bit image...")
            return

        self.scn_file = file_path
        self.img_path = img_path
        self.img = img
        self.mappings = {}

        # Parse scn file
        with open(file_path, encoding="utf8", errors='ignore') as f:
            for line in f:
                l = line.lstrip().rstrip()
                if l[:6] == '<table':
                    find_c = l.find('>')
                    l = l[find_c + 1:-8]
                    nums = l.split()
                    i = 1
                    for num in nums:
                        self.mappings[str(i)] = float(num)
                        i += 1
                if l[:17] == '<scan_resolution>':
                    l = l[17:-18]
                    self.scale = float(l)
        self.setup()

    def setup(self):
        '''
        Sets up the window with the ImageCanvas and Lanes
        Creates a table
        '''
        self.topframe = Frame(
            self.root, width=self.screen_width, height=self.screen_height)
        self.topframe.pack(fill=BOTH)
        self.image_canvas = ImageCanvas(
            self.topframe, self.img_path, self.mappings, self.screen_width, self.screen_height)

    def create_lane(self):
        '''
        Action from menu to add a lane onto the ImageCanvas
        '''
        # Check if image was uploaded
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        self.image_canvas.add_lane()

    def optimize_lanes(self):
        '''
        Action from menu to optimize volume of all lanes
        '''
        # Check if image was uploaded
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        # Check if there are lanes
        if len(self.image_canvas.lanes) == 0:
            messagebox.showerror('Error',
                                 'There are no lanes to optimize, you need to add lanes first')
            return
        self.image_canvas.optimize_lanes()

    def export(self):
        '''
        Action from menu to export information into a table
        '''
        # Check if image was uploaded
        if self.image_canvas is None:
            messagebox.showerror('Error', 'You need to upload an image first')
            return
        # Check if there are lanes
        if len(self.image_canvas.lanes) == 0:
            messagebox.showerror('Error',
                                 'There are no lanes to export, you need to add lanes first')
            return
        # Check if pressed optimized and manually moved
        if self.image_canvas.clicked_opt == True and self.image_canvas.manual_move == True:
            answer = messagebox.askokcancel('Export', 
                                            'You have manually moved lanes since optimizing lanes. Are you sure you want to export anyways?')
            if answer == False:
                return
        
        # Save file with name
        f = filedialog.asksaveasfile(mode="w", defaultextension=".csv")
        if f is None:
            return

        columns = [ 'No.',
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
                    'height (pixels)'
                ]
        column_str = ",".join(columns) + "\n"
        f.write(column_str)

        w = 97
        h = 55
        t = "Unknown"
        a_quant = r_quant = "N/A"
        total_pixels = w*h
        area = ((self.scale/1000)**2) * (w*h)

        # Loop through all lanes
        for lane in self.image_canvas.lanes:
            label = lane.name
            num = label[4:]
            adj, mean_b, vol, x_y, min_vol, max_vol, avg_vol, sd = lane.info
            x,y = x_y
            r = [num,label,t,vol,adj,mean_b,a_quant,r_quant,total_pixels,
                    min_vol,max_vol,avg_vol,sd,area,x,y,w,h]
            row = list(map(str, r))
            row_str = ",".join(row) + "\n"
            f.write(row_str)

        f.close()
        messagebox.showinfo('Success', 'Table information exported')


if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()
