import tkinter

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

root = tkinter.Tk()
root.title("Tkinter Game")

game_title_label = tkinter.Label(root, text="Tkinter Shot", font=("メイリオ", 20))
game_title_label.grid(column=0, row=0)

game_canvas = tkinter.Canvas(root, bg="#cceb51")
game_canvas.grid(column=0, row=1)


class Player:
    def __init__(self, field: tkinter.Canvas) -> None:
        self.id = field.create_rectangle(100, 100, 110, 110, fill="black")


player = Player(field=game_canvas)

root.mainloop()
