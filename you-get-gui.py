#! /usr/bin/env python
#  coding: utf-8

import Tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, width=800, height=600)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W) # stretchable window
        self.createWidgets()
        self.grid_propagate(0)

    def createWidgets(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        row = 0
        tk.Label(self, text='Proxy:').grid(sticky=tk.W)
        self.proxy = tk.StringVar(self, '127.0.0.1:8087')
        tk.Entry(self, textvariable=self.proxy).grid(row=row, column=1, sticky=tk.W+tk.E)

        row += 1
        tk.Label(self, text='URL:').grid(sticky=tk.W)
        self.url = tk.StringVar(self, 'http://v.youku.com/v_show/id_XOTA4MjY1MzU2.html')
        tk.Entry(self, textvariable=self.url).grid(row=row, column=1, sticky=tk.W+tk.E)

        row += 1
        tk.Label(self, text='Extra parameters:').grid(sticky=tk.W)
        self.extra = tk.StringVar(self, '-i')
        tk.Entry(self, textvariable=self.extra).grid(row=row, column=1, sticky=tk.W+tk.E)

        row += 1
        tk.Label(self, text='Command:').grid(sticky=tk.W)
        self.cmd = tk.StringVar(self)
        tk.Entry(self, textvariable=self.cmd, state='readonly').grid(row=row, column=1, sticky=tk.W+tk.E)

        row += 1
        tk.Label(self, text='Operations:').grid(sticky=tk.W)
        tk.Button(self, text='Run', command=self.download).grid(row=row, column=1)

        row += 1
        self.output = tk.Text(self)
        self.output.grid(columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

        # update command entry
        def cb(name, index, mode):
            self.update_command()

        self.proxy.trace('w', cb)
        self.url.trace('w', cb)
        self.extra.trace('w', cb)
        self.update_command()

        self.rowconfigure(row, weight=1)

    def download(self):
        self.output.delete(1.0, tk.END)
        cmd = self.get_cmd()
        import subprocess
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            self.output.insert(tk.END, line)

    def get_cmd(self):
        cmd =  'you-get'
        if self.proxy.get():
            cmd += ' -x ' + self.proxy.get()
        if self.extra.get():
            cmd += ' ' + self.extra.get()
        if self.url.get():
            cmd += ' "{}"'.format(self.url.get())
        return cmd

    def update_command(self):
        self.cmd.set(self.get_cmd())


app = Application()
app.master.title('Video Downloader (powered by you.get)')
app.mainloop()