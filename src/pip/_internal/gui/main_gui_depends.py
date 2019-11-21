
from __future__ import absolute_import
from .myglobals import *
from .pypi_simple_download import *

import re
import tkinter as tk
from collections import deque

from pip._internal.operations.check import (
    check_package_set,
    create_package_set_from_installed,
)


def package_set_load():
    package_set, parsing_probs = create_package_set_from_installed()
    missing, conflicting = check_package_set(package_set)
    return package_set


class MainWnd(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=1, fill="both")

        self.hist = deque(maxlen=16)

        col_r = 3
        self.columnconfigure(col_r, weight=1)
        self.rowconfigure(1, weight=1)

        self.index = tk.Label(self, text="index:")
        self.index.bind("<Double-Button-1>", self.on_index_double_click)
        self.index.bind("<Button-1>", self.on_index_click)
        self.index.grid()

        self.evar = tk.StringVar()
        self.e = tk.Entry(self, width=26, textvariable=self.evar)
        self.e.bind("<KeyRelease>", self.on_key)
        self.e.grid(row=0, column=1)

        self.starv = '>'  # '>'=起始匹配 '*'=模糊匹配
        self.star = tk.Label(self, text=self.starv)
        self.star.grid(row=0, column=2)
        self.star.bind("<1>", self.on_star)

        self.lbv = tk.StringVar()
        self.lb = tk.Listbox(self, listvariable = self.lbv, height=28, width=36)
        self.lb.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.lb.bind("<ButtonRelease-1>", self.on_sel)

        self.text_ready = ""
        self.text = tk.Text(self, height=38, width=100)
        self.text.grid(row=0, column=col_r, rowspan=2, padx=3, sticky="nsew")
        scroll = tk.Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=col_r + 1, rowspan=2, sticky="ns")

        fontname = 'Verdana'
        self.text.tag_config("version", foreground="black", font=(fontname, 14))
        self.text.tag_config("download", foreground="blue", underline=1, font=(fontname, 12))

        self.text.tag_config("h1", foreground="black", font=(fontname, 24, 'bold'))
        self.text.tag_config("h2", foreground="black", font=(fontname, 18, 'bold'))
        self.text.tag_config("hyper", foreground="blue", underline=1, font=(fontname, 12, 'bold'))

        self.text.tag_config("help1", foreground="blue", font=(fontname, 14))
        # self.text.tag_bind("ydoc", "<Button-1>", self.on_ydoc)

        self.text.tag_config("y", foreground="blue", underline=1)
        # self.text.tag_bind("y", "<Button-1>", self.on_y)

        self.lba = self.home_index()
        self.on_key(None)
        self.e.focus_set()

    def home_index(self):
        return ['help', 'todo']

    def home_todo(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, 'TODO')
        self.text.insert(tk.END, "\n")

    def home_help(self):
        self.text.delete(1.0, tk.END)

        self.text.insert(tk.END, "\n\n")

        self.text.insert(tk.END, 'click on label "index:" left to the input box:\n', 'help1')
        self.text.insert(tk.END, "back to last key\n\n")

        self.text.insert(tk.END, 'click on label ">" right to the input box:\n', 'help1')
        self.text.insert(tk.END, "switch to substr mode\n\n")

        self.text.insert(tk.END, 'click on label "*" right to the input box:\n', 'help1')
        self.text.insert(tk.END, "switch to startswith mode\n\n")

        self.text.insert(tk.END, "\n")

        self.text.insert(tk.END, "\n")

    def on_index_click(self, event):
        """
        点击index标签
        """
        print(self.hist)
        if len(self.hist) < 1: return
        k = self.hist.pop()
        print("pop", k)
        self.evar.set(k)
        self.on_key(None)

    def on_index_double_click(self, event):
        """
        双击index标签
        """
        pass

    def on_star(self, event):
        """
        点击星号标签
        """
        if self.starv == '*': self.starv = '>'
        else:                 self.starv = '*'
        self.star.config(text=self.starv)
        self.on_key(None)

    def lookup_dict(self, s:str):
        if not s:
            return sorted(g.yindex_d.keys())

        cnt = 0
        a = []
        s = s.lower()
        for k in g.yindex_d:
            k_ = k.lower()
            if self.starv == '*':
                if k_.find(s) < 0: continue
            else:
                if not k_.startswith(s): continue
            a.append(k)
            cnt += 1
            if cnt >= 50: break
        return sorted(a)

    def on_key(self, _):
        """
        用户输入新的key
        """

        k = self.e.get()
        if _ is not None and k:
            if self.hist:
                lastk = self.hist[-1]
                if k.startswith(lastk):
                    self.hist[-1] = k
                elif not lastk.startswith(k):
                    self.hist.append(k)
                else:
                    pass
            else:
                self.hist.append(k)
        print(self.hist)

        self.lba = self.lookup_dict(k)
        self.lb.delete(0, tk.END)
        self.lb.insert(0, *self.lba)
        self.lb.select_set(0)
        self.on_sel(None)

    def on_sel(self, _):
        """
        用户选择列表中的项目
        """
        sel = self.lb.curselection()
        if not sel: return
        i = sel[0]
        k = self.lba[i]

        if k == 'help': self.home_help(); return

        if self.text_ready == k: return

        self.text.delete(1.0, tk.END)
        pkgd = g.yindex_d.get(k, None)  # type: PackageDeails
        print(pkgd)
        self.text.insert(tk.END, k + " " + pkgd.version + '\n\n', "h2")

        if not pkgd.requires:
            self.text.insert(tk.END, "no depends\n")
            return
        for require in pkgd.requires:
            name = require.name
            self.text.insert(tk.END, name + '\n', "hyper")
            self.text.insert(tk.END, "specifier: " + str(require.specifier) + '\n')
            self.text.insert(tk.END, "project_name: " + require.project_name + '\n')
            self.text.insert(tk.END, "unsafe_name: " + require.unsafe_name + '\n')
            self.text.insert(tk.END, '\n')


def main_gui_depends():
    g.yindex_d = package_set_load()
    root = tk.Tk()
    root.title("pip gui_depends")
    wnd = MainWnd(master=root)
    g.wnd = wnd
    wnd.mainloop()


if __name__ == "__main__":
    main_gui_depends()