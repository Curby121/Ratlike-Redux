import tkinter as tk
from tkinter import ttk
import asyncio
import baseclasses as bc

root = tk.Tk()
root.title('RatLike Redux')
root.configure(background = "black")
root.geometry("1280x720")
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

game = None
current_frame:ttk.Frame = None

class CombatWindow(ttk.Frame):
    def __init__(self, root, plr_actions, enemies:list):
        super().__init__(root)
        actn_bar = ActionBar(self, plr_actions)
        actn_bar.grid(row=1, column=1, columnspan=2)
        self.plr_stats = self.PlrStats(self)
        self.plr_stats.grid(row = 0, column = 1)
        self.plr_stats.update()

    def Updt(self):
        self.plr_stats.update()
    
    class PlrStats(ttk.Frame):
        def __init__(self, root):
            super().__init__(root)
            self.hp_L = ttk.Label(font=('Arial', 18))
            self.ex_L = ttk.Label(font=('Arial', 18))
            self.hp_L.grid(sticky = tk.E, padx = 5)
            self.ex_L.grid(row=0, column = 1,sticky = tk.W, padx = 5)
        def update(self):
            self.hp_L.configure(text = f'HP: {game.plr.hp}/{game.plr.max_hp}')
            self.ex_L.configure(text = f'Ex: {game.plr.exhaust}/{game.plr.max_exh}')

class ActionBar(ttk.Frame):
    def __init__(self, root, actions:list):
        super().__init__(root)
        self.actns = []
        for i,a in enumerate(actions):
            self.columnconfigure(i, weight=1)
            f = self.PlayerAction(self, a)
            f.grid(row = 0, column = i, ipadx=3)
            self.actns.append(f)

    class PlayerAction(ttk.Frame):
        def __init__(self, root, action:bc.Action):
            super().__init__(root)
            self.action = action
            self.rowconfigure(0, weight=4)
            self.rowconfigure(1, weight=1)
            actn_b = ttk.Button(
                self,
                text = action.name,
                command = self.choose_action
                )
            info_b = ttk.Button(
                self,
                text = 'Info',
                command = self.examine_action
                )
            actn_b.grid(row = 0)
            info_b.grid(row = 1)
        
        def choose_action(self):
            global game
            game.select_player_action(self.action)
        def examine_action(self):
            print(self.action.desc)

class PlayerStats(ttk.Frame):
    def __init__(self):
        super().__init__()
        var = tk.StringVar()
        
def init(gme):
    global game
    game = gme

async def run():
    while True:
        if current_frame is not None:
            current_frame.Updt()
        root.update()
        root.update_idletasks()
        await asyncio.sleep(0)

def EnterCombat(enemies):
    global current_frame
    global game
    if current_frame is not None:
        current_frame.destroy()
    current_frame = CombatWindow(root, game.plr.get_combat_actions(), enemies)
    current_frame.grid()
    print('created combat')