import tkinter

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

root = tkinter.Tk()
root.title("Tkinter Game")

game_title_label = tkinter.Label(root, text="Tkinter Shot", font=("メイリオ", 20))
game_title_label.grid(column=0, row=0)

game_canvas = tkinter.Canvas(root, bg="#cceb51")
game_canvas.grid(column=0, row=1)

root.mainloop()
