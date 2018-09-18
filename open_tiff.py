
# https://stackoverflow.com/questions/23901168/how-do-i-insert-a-jpeg-image-into-a-python-tkinter-window

import os
import tkinter as tk
import numpy
from tkinter import dnd
from PIL import ImageTk, Image

#This creates the main window of an application
root = tk.Tk()
root.title("Join")
root.geometry("1720x1000")
root.configure(background='grey')

w = tk.Canvas(root, width=1720, height=1000, bg="white")
w.pack()

w.create_rectangle(50, 25, 150, 75, fill="blue")

path = "./test2.tif"


im = Image.open(os.path.expanduser(path))

imarray = numpy.array(im)
#Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
img = ImageTk.PhotoImage(im)

#The Label widget is a standard Tkinter widget used to display a text or image on the screen.
panel = tk.Label(w, image = img)

#The Pack geometry manager packs widgets in rows or columns.
panel.pack(side = "bottom", fill = "both", expand = "yes")

w.create_rectangle(50, 25, 150, 75, fill="blue")


print(imarray)
print(imarray.shape)
#Start the GUI
root.mainloop()
