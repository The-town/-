import tkinter
import random
import datetime
import csv

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)


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

    def check_reach_bottom(self):
        height = self.field.winfo_height()
        _, y1, _, _ = self.field.coords(self.id)
        if y1 > height:
            return True


class GameWindow:
    def __init__(self, master) -> None:
        self.master = master
        self.frame = {}
        self.ranking = Ranking()

        self.create_start_window()

    def create_start_window(self):
        self.frame["start"] = tkinter.Frame(self.master)
        self.frame["start"].grid(column=0, row=0)

        label = tkinter.Label(self.frame["start"], text="Tkinter Shot", font="メイリオ, 20", width=20)
        label.grid(column=0, row=0, padx=50, pady=50)

        start_button = tkinter.Button(self.frame["start"], text="Start", font="メイリオ, 12", width=20, command=self.game_start)
        start_button.grid(column=0, row=1, padx=50, pady=50)

    def create_game_field(self):
        self.frame["game_field"] = tkinter.Frame(self.master)
        self.frame["game_field"].grid(column=0, row=0)

        game_title_label = tkinter.Label(self.frame["game_field"], text="Tkinter Shot", font=("メイリオ", 20))
        game_title_label.grid(column=0, row=0)

        self.game_field = GameField(self.frame["game_field"])

    def game_start(self, event=None):
        self.frame["start"].destroy()
        self.create_game_field()
        self.game_field.add_enemy()
        self.game_field_update()
    
    def game_field_update(self):
        if self.game_field.update():
            self.master.after(100, self.game_field_update)
        else:
            self.master.after(5000, self.game_finish)

    def create_ranking_window(self):
        self.frame["ranking"] = tkinter.Frame(self.master)
        label = tkinter.Label(self.frame["ranking"], text="Tkinter Shot Ranking", font="メイリオ, 20", width=20)
        label.grid(column=0, row=0, padx=50, pady=50, columnspan=2)

        self.frame["ranking"].grid(column=0, row=0)
        
        self.ranking.write(self.game_field.score)
        for i, rank in enumerate(self.ranking.get_rank()):
            label_date = tkinter.Label(self.frame["ranking"], text=rank[0], font="メイリオ, 12")
            label_date.grid(column=0, row=i+1, pady=5)
            label_score = tkinter.Label(self.frame["ranking"], text=rank[1], font="メイリオ, 12")
            label_score.grid(column=1, row=i+1, pady=5)

    def game_finish(self):
        self.frame["game_field"].destroy()
        self.create_ranking_window()


class GameField:
    def __init__(self, master) -> None:
        self.game_canvas = tkinter.Canvas(master, bg="#cceb51")
        self.game_canvas.grid(column=0, row=1)
        self.player = Player(field=self.game_canvas)
        self.enemies = []
        self.score = 0
        self.score_text = self.game_canvas.create_text(10, 10, text=f"score {self.score}", fill="black", anchor="w")

        self.enemies_reached_bottom = 0
        self.enemies_reached_bottom_text = self.game_canvas.create_text(
            100, 10, text=f"reached bottom {self.enemies_reached_bottom}", fill="black", anchor="w"
            )
        
        root.bind("<KeyPress-Right>", self.player.right)
        root.bind("<KeyPress-Left>", self.player.left)
        root.bind("<KeyPress-Up>", self.player.up)
        root.bind("<KeyPress-Down>", self.player.down)
        root.bind("<KeyPress-space>", self.player.attack)

    def add_enemy(self):
        self.enemies.append(Enemy(field=self.game_canvas))
        if self.enemies_reached_bottom < 3:
            self.game_canvas.after(1000, self.add_enemy)
            

    def update(self, event=None):
        enemy_ids = []
        for enemy in self.enemies:
            enemy.move()
            if enemy.check_reach_bottom():
                self.enemies_reached_bottom += 1
                self.game_canvas.itemconfigure(
                    self.enemies_reached_bottom_text, text=f"reached bottom {self.enemies_reached_bottom}"
                    )
                self.game_canvas.delete(enemy.id)
                self.enemies.remove(enemy)
            else:
                enemy_ids.append(enemy.id)

        for shot in shots:
            shot.move()
            overlap_enemy_ids = list(set(enemy_ids) & set(shot.check_overlap()))
            if overlap_enemy_ids:
                self.game_canvas.delete(shot.id)
                shots.remove(shot)

                self.game_canvas.delete(overlap_enemy_ids[0])
                shotted_enemy = self.enemies.pop(enemy_ids.index(overlap_enemy_ids[0]))

                self.score += shotted_enemy.point
                self.game_canvas.itemconfigure(self.score_text, text=f"score {self.score}")

        if self.enemies_reached_bottom < 3:
            return True
        else:
            self.game_canvas.create_text(self.game_canvas.winfo_width() / 2, self.game_canvas.winfo_height() /2,
                                    text="Game Over !", fill="black", font="メイリオ, 20")
            return False


class Ranking:
    def __init__(self) -> None:
        self.path = "./rank.csv"
        self.display_rank = 5

    def get_rank(self):
        score = self.read()
        return sorted(score, key=lambda s: int(s[1]), reverse=True)[:self.display_rank]

    def write(self, score):
        with open(self.path, "a", newline="") as f:
            writer = csv.writer(f)
            create_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            writer.writerow([create_time, score])
            f.flush()
        
    def read(self):
        with open(self.path, "r") as f:
            reader = csv.reader(f)
            return list(reader)


root = tkinter.Tk()
root.title("Tkinter Game")

shots = []
        
game_window = GameWindow(root)

root.mainloop()
