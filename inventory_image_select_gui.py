# for multiple images use more labels and functions
import tkinter as tk
from tkinter import *
import cv2
import numpy as np
import os
from PIL import Image, ImageTk
from functools import partial


pictdict = {}
jpeglist = []
label = []
filepointer = 0
stillrunning = True
missingImages = ["The following items were either not found or need attention:", "", ]


class popupWindow(object):
    def __init__(self, master):
        top = self.top = tk.Toplevel(master)
        top.geometry("600x400")
        self.title = Label(top,
                           text="Optional - enter comment.",
                           fill="#666666",
                           font=("Catamaran-Regular", int(32.0)))
        self.title.pack()
        self.default = Label(top,
                             text="Default: Images do not match item description",
                             fill="#666666",
                             font=("Catamaran-Regular", int(28.0)))
        self.default.pack()
        self.e = Entry(top)
        self.e.pack()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        self.value = self.e.get()
        if not self.value or self.value.strip() == "":
            self.value = "Images do not match item description"
        return self.value
        self.top.destroy()


class DisplayImage:

    def __init__(self, master):
        self.master = master
        master.title("GUI")
        global jpeglist, filepointer, stillrunning, missingimages, subdir, pictdict
        self.w = 1440
        self.h1 = 183
        self.w1 = 275
        self.cum_w = 0
        self.counter = 0
        self.deletephotos = []
        self.savephoto = ""
        self.fp = filepointer
        self.master.geometry("1440x1024")
        self.master.configure(bg="#ffffff")
        self.canvas = Canvas(
            self.master,
            bg="#ffffff",
            height=1024,
            width=1440,
            bd=0,
            highlightthickness=0,
            relief="ridge")
        self.canvas.place(x=0, y=0)
        self.canvas.create_text(
            720.0, 195.5,
            text="Select photo",
            fill="#666666",
            font=("Catamaran-Regular", int(48.0)))
        self.canvas.create_rectangle(
            630, 880, 634+176, 884+59,
            fill="#ffffff",
            outline="#ffffff")
        self.img1 = PhotoImage(
            file=f"/Users/john.tamm-buckle/Documents/CompAVTech/JAMF/generated_code/img0.png")
        self.b1 = tk.Button(
            image=self.img1,
            borderwidth=0,
            highlightthickness=0,
            command=self.skipSelection,
            relief="flat")
        self.b1.place(
            x=598, y=749,
            width=250,
            height=59)
        self.img0 = PhotoImage(
            file="/Users/john.tamm-buckle/Documents/CompAVTech/JAMF/Inventory2021/generated_code/img0.png")
        self.b0 = tk.Button(
            image=self.img0,
            borderwidth=20,
            highlightthickness=10,
            command=self.delete_files,
            state="disabled",
            relief="flat")
        self.b0.place(
            x=632, y=882,
            width=176,
            height=59)
        self.spacing = (self.w-(5*self.w1))/5

    def keepGoing(self, event=None):
        global stillrunning, filepointer
        stillrunning = True
        filepointer = self.fp + 1
        print(stillrunning)
        print(f"Filepointer: {filepointer}")

    def nextSet(self, fname, event=None):
        self.savephoto = fname
        if self.savephoto in self.deletephotos:
            self.b0["state"] = "normal"

    def skipSelection(self, *fCount, event=None):
        i = os.path.basename(os.path.split(subdir[self.fp])[0])
        self.keepGoing()
        print(stillrunning)
        print(filepointer)
        print(f"fCount: {fCount}")
        for l in globals():
            print(l)
        if fCount and len(fCount) == 2:
            i = f"{i} - NOTE - {fCount[1]}"
        if not fCount:
            # fCount = self.popup()
            missingImages.append(f"{i} - NOTE - {fCount}")
        elif fCount[0] == 0:
            missingImages.append(i)
        self.master.destroy()

    def popup(self):
        self.w = popupWindow(self.master)
        self.b1["state"] = "disabled"
        self.master.wait_window(self.w.top)
        self.b1["state"] = "normal"
        return self.w.value

    def delete_files(self, event=None):
        try:
            self.deletephotos.remove(self.savephoto)
            for i in self.deletephotos:
                os.remove(subdir[self.fp] + i)
                self.keepGoing()
            self.master.destroy()
        except ValueError:
            tkinter.messagebox.showinfo(
                title="No file selected", message="Please select an image.  If none are suitable, skip this selection", **options)
            print("No file selected")

    def read_image(self, event=None):
        print(f"Subdirectories: {subdir}")
        try:
            i = subdir[self.fp]
            print(f"Current directory: {i}")
        except IndexError:
            stillrunning = False
            self.master.destroy()
        imgdict = {}
        try:
            self.files = os.listdir(i)
            print(f"Current directory contents: {self.files}")
        except NotADirectoryError:
            self.master.destroy()
        if not self.files:
            print("No files found")
            self.skipSelection(0, "Search returned no results")
        elif len(self.files) == 1:
            print("1 file found, probably already selected")
            self.skipSelection(1)
        elif len(self.files) > 1:
            self.canvas.create_text(
                720, 245.5,
                text=self.files[0][:len(self.files[0])-7],
                fill="#666666",
                font=("Catamaran-Regular", int(36.0)))
            self.heights = []
            for j in range(len(self.files)):
                self.load = Image.open(f"{i}/{self.files[j]}")
                self.width, self.height = self.load.size
                self.cum_w += self.width
                self.heights.append(self.height)

            self.maxheight = max(self.heights)
            self.spacing = (self.w-self.cum_w)/len(self.files)
            jpeglist = []
            print(f"Spacing: {str(self.spacing)}")

            self.label = list(range(len(self.files)))
            self.buttons = list(range(len(self.files)))
            for k, fname in enumerate(self.files):
                self.deletephotos.append(fname)
                self.load = Image.open(f"{i}/{fname}")
                self.render = ImageTk.PhotoImage(self.load)
                imgdict[fname] = self.load
                self.label[k] = Label(self.master, image=self.render, text=f"{self.counter+1}")
                self.wa, self.ha = self.load.size
                if self.counter == 0:
                    self.xa = self.spacing/2
                    jpeglist.append(self.wa+self.spacing+self.xa)
                else:
                    self.xa = sum(jpeglist)
                    jpeglist.append(self.wa+self.spacing)
                self.x1 = (self.counter*(self.wa+self.spacing))+self.wa
                self.ya = self.ha+316
                self.buttons[k] = Button(self.master, command=partial(self.nextSet, fname),
                                         text="Select image", width=15, default=ACTIVE)
                self.label[k].image = self.render  # keep a reference!
                self.label[k].place(x=self.xa-1, y=315)  # pack when you want to display it
                self.buttons[k].place(
                    x=((self.xa-1)+((self.wa/2)-(45+self.spacing))), y=self.maxheight + 325)
                self.counter = self.counter + 1
            pictdict[f"{i}"] = imgdict
            print(f"Label: {self.label}")
            self.cum_w = 0


def pre_init():
    globals()['stillrunning'] = False
    window = Tk()
    GUI = DisplayImage(window)
    GUI.read_image()  # list of args...
    window.mainloop()


def main():
    global cols, imgdir, subdir, filepointer, missingImages
    dirs = {}
    subdir = []
    cols = ['Asset_Inventory', 'Computers', 'iPads', 'Misc']
    imgdir = '/Users/john.tamm-buckle/Documents/CompAVTech/DatabaseImages/'
    for dir in cols:
        dirs[dir] = os.listdir(imgdir + dir + '/')
        for i in dirs[dir]:
            if i == ".DS_Store":
                continue
            else:
                subdir.append(imgdir + dir + '/' + i + '/')
    while stillrunning:
        print(f"Filepointer: {filepointer + 1}")
        print(f"No. of directories: {len(subdir)}")
        if filepointer >= len(subdir):
            print("End of file.  Exiting...")
            break
        else:
            pre_init()

    # Log missing images
    with open('/Users/john.tamm-buckle/Documents/CompAVTech/JAMF/missing_log.txt', 'w') as f:
        for item in missingImages:
            f.write("%s\n" % item)


if __name__ == '__main__':
    main()
