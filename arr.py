from tkinter import *
import os
import numpy as np
from PIL import ImageTk, Image
import cv2


path = "./test4.tif"
path_map = "./16bit_calibration.dat"

mappings = {}

# read file and create mappings
with open(path_map, "r") as map_f:
    for line in map_f:
        intensity, volume = line.rstrip().split(",")
        mappings[intensity] = float(volume)

print("---------------")
img = cv2.imread(path, -1)

print("Data type: ", img.dtype)

print("Image shape: ", img.shape)

# x = 461
# y = 511
# w = 96
# h = 55

x = 462
y = 512
w = 97
h = 55

total_pixels = w*h

print("Total pixels: ", total_pixels)

crop_img = img[y-1:y+h+1, x-1:x+w+1]

print("Box shape: ", crop_img.shape)

# cv2.imshow("cropped", crop_img)
# cv2.waitKey(0)

# summing the total volume of box by grabbing each mapping
vol = 0
for i in range(1, h+1):
    for j in range(1, w+1):
        m = mappings[str(crop_img[i, j])]
        vol += m

print("Volume OD: ", vol)


# summing volume of edges to get mean background
mean_b = 0
for j in range(0, h+2):
    mean_b += mappings[str(crop_img[j, 0])] + mappings[str(crop_img[j, w+1])]
for i in range(1, w):
    mean_b += mappings[str(crop_img[0, i])] + mappings[str(crop_img[h+1, i])]

# divide sum of edges volume by pixels
mean_b /= ((w+2) * 2) + (h * 2)
#mean_b /= ((w) * 2) + ((h-1) * 2)

print("Mean Bkgd: ", mean_b)


# calculating adjusted volume
adj_vol = vol - (total_pixels * mean_b)

print("Adj Vol: ", adj_vol)


print("*******Bigger box*********")


x = 462
y = 512
w = 97
h = 55

total_pixels = w*h

print("Total pixels: ", total_pixels)

crop_img = img[y:y+h, x:x+w]

print("Box shape: ", crop_img.shape)

# cv2.imshow("cropped", crop_img)
# cv2.waitKey(0)

# get inner box volume
vol = 0
for i in range(1, h-1):
    for j in range(1, w-1):
        m = mappings[str(crop_img[i, j])]
        vol += m

print("Volume OD: ", vol)

# Get mean background of bigger box
mean_b = 0
for j in range(0, h):
    mean_b += mappings[str(crop_img[j, 0])] + mappings[str(crop_img[j, w-1])]
for i in range(1, w-1):
    mean_b += mappings[str(crop_img[0, i])] + mappings[str(crop_img[h-1, i])]

mean_b /= (w * 2) + ((h-2) * 2)

print("Mean Bkgd: ", mean_b)


adj_vol = vol - (total_pixels * mean_b)

print("Adj Vol: ", adj_vol)
