# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

import Tkinter as tk
import ffmpeg
import time

class App(object):
    def __init__(self, root):
        self.root = root
        self.video = tk.Canvas(root, bg='#000000')
        self.video.pack(side=tk.BOTTOM,anchor=tk.S,expand=tk.YES,fill=tk.BOTH)

        self.ff = ffmpeg.Reader(path=r'f:\projects\ar\data\card.mp4')
        self.photo = tk.PhotoImage(file=r'f:\projects\object_tracking\data\datasets\woman\001.jpg')
        self.video.create_image((0, 0), image=self.photo)

        self.label = tk.Label(self.video, text="")
        self.label.pack()
        self.update_clock()

    def update_clock(self):
        now = time.strftime("%H:%M:%S")
        self.label.configure(text=now + " - " + repr(len(self.ff.read())))
        self.root.after(1000, self.update_clock)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('500x400')
    app = App(root)
    root.mainloop()