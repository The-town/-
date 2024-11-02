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


class Shot:
    def __init__(self, field: tkinter.Canvas, x: int, y: int) -> None:
        shot_length = 5
        self.id = field.create_line(x, y, x, y + shot_length, width=3)
        self.field = field

    def move(self):
        self.field.move(self.id, 0, -5)
    
    def check_overlap(self) -> tuple:
        x1, y1, x2, y2 = self.field.bbox(self.id)
        overlap_ids = self.field.find_overlapping(x1, y1, x2, y2)

        return overlap_ids


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
    
    def attack(self, event=None):
        x1, y1, x2, y2 = self.field.bbox(self.id)
        x_center = x2 - (x2 - x1) / 2
        y_center = y2 - (y2 - y1) / 2
        shots.append(Shot(self.field, x_center, y_center))


class Enemy:
    def __init__(self, field: tkinter.Canvas) -> None:
        self.field = field
        self.field.update_idletasks()
        rand_x = random.randrange(50, self.field.winfo_width() - 50)
        self.id = self.field.create_rectangle(rand_x, 0, rand_x+20, 20, fill="red")

        self.point = 1
        
    def move(self):
        self.field.move(self.id, 0, 5)


def add_enemy():
    enemies.append(Enemy(field=game_canvas))
    game_canvas.after(1000, add_enemy)

def update():
    enemy_ids = []
    for enemy in enemies:
        enemy.move()
        enemy_ids.append(enemy.id)
    
    for shot in shots:
        shot.move()
        overlap_enemy_ids = list(set(enemy_ids) & set(shot.check_overlap()))
        if overlap_enemy_ids:
            game_canvas.delete(shot.id)
            shots.remove(shot)

            game_canvas.delete(overlap_enemy_ids[0])
            shotted_enemy = enemies.pop(enemy_ids.index(overlap_enemy_ids[0]))

            global score
            score += shotted_enemy.point
            game_canvas.itemconfigure(score_text, text=f"score {score}")

    
    game_canvas.after(100, update)


player = Player(field=game_canvas)
enemies = []
shots = []
score = 0
score_text = game_canvas.create_text(10, 10, text=f"score {score}", fill="black", anchor="w")

root.bind("<KeyPress-Right>", player.right)
root.bind("<KeyPress-Left>", player.left)
root.bind("<KeyPress-Up>", player.up)
root.bind("<KeyPress-Down>", player.down)
root.bind("<KeyPress-space>", player.attack)

update()
add_enemy()

root.mainloop()
