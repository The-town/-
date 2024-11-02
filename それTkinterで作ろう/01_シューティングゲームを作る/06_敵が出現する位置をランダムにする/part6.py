import tkinter
import random

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
        self.field = field

    def right(self, event=None):
        self.field.move(self.id, 10, 0)

    def left(self, event=None):
        self.field.move(self.id, -10, 0)

    def up(self, event=None):        
        self.field.move(self.id, 0, -10)

    def down(self, event=None):
        self.field.move(self.id, 0, 10)


class Enemy:
    def __init__(self, field: tkinter.Canvas) -> None:
        self.field = field
        rand_x = random.randrange(50, 500)
        self.id = self.field.create_rectangle(rand_x, 0, rand_x+20, 20, fill="red")
        
    def move(self):
        self.field.move(self.id, 0, 5)


def update():
    enemy.move()
    game_canvas.after(100, update)


player = Player(field=game_canvas)
enemy = Enemy(field=game_canvas)

root.bind("<KeyPress-Right>", player.right)
root.bind("<KeyPress-Left>", player.left)
root.bind("<KeyPress-Up>", player.up)
root.bind("<KeyPress-Down>", player.down)

update()

root.mainloop()
