#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主程序入口文件
用于启动GUI应用程序
"""

import sys
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from gui.app import App

def main():
    """
    主程序入口函数
    """
    root = TkinterDnD.Tk()
    root.title("ComfyUI节点翻译工具 - By OLDX")
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main() 