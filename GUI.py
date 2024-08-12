import tkinter as tk
from tkinter import ttk
import asyncio

root = tk.Tk()
root.title('RatLike Redux')
root.configure(background = "black")
root.geometry("1280x720")
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

game = None
current_frame:ttk.Frame = None
current_log = None
log_msgs:list[str] = []

def log(msg:str):
    log_msgs.append(msg)
    if current_log is not None:
        current_log.text.config(state = tk.NORMAL)
        current_log.text.insert(index=tk.END, chars = '\n' + msg)
        current_log.text.see(tk.END)
        current_log.text.config(state = tk.DISABLED)

# TODO: currently only first enemy is displayed
class CombatWindow(tk.Canvas):
    def __init__(self, root, plr_actions, enemies:list):
        super().__init__(root, bg='black')
        actn_bar = ActionBar(self, plr_actions)
        actn_bar.place(relx=0.5, rely=0.75, anchor='center')
        self.plr_stats = self.PlrStats(self)
        self.plr_stats.place(rely=0.6, relx=0.5, anchor='center', relwidth=0.35, relheight=0.1)
        self.enemy_stats = self.EnemyStats(self, enemies[0])
        self.enemy_stats.place(rely=0.25, relx=0.5, anchor='center')

        self.log = Log(self)
        self.log.place(relx=1, rely=0.5, relheight=1, relwidth=0.3, anchor='e')

        self.Updt()

    def Updt(self):
        self.plr_stats.update()
        self.enemy_stats.update()
    
    class PlrStats(ttk.Frame):
        def __init__(self, root):
            super().__init__(root)
            self.hp_L = ttk.Label(self, font=('Arial', 18))
            self.exh_L = ttk.Label(self, font=('Arial', 18))
            self.hp_B = ttk.Progressbar(self, mode = 'determinate')
            self.exh_B = ttk.Progressbar(self, mode = 'determinate')
            self.hp_L.place(relx=0.45, rely=0.5, anchor='se')
            self.exh_L.place(relx=0.55, rely=0.5, anchor='sw')
            self.hp_B.place(relx=0.45, rely=0.55, anchor='ne')
            self.exh_B.place(relx=0.55, rely=0.55, anchor='nw')
        def update(self):
            self.hp_L.configure(text = f'HP: {game.plr.hp}/{game.plr.max_hp}')
            self.exh_L.configure(text = f'Ex: {game.plr.exhaust}/{game.plr.max_exh}')
            self.hp_B.configure(value = 100*(game.plr.hp / game.plr.max_hp))
            self.exh_B.configure(value = 100*(game.plr.exhaust / game.plr.max_exh))

    class EnemyStats(ttk.Frame):
        def __init__(self, root, enemy):
            super().__init__(root, padding=15)
            self.enemy = enemy
            self.label = ttk.Label(self, text=enemy.name, font=('Arial', 16))
            self.label.grid(row=0, column=0)
            self.hp_L = ttk.Label(self, font=('Arial', 14))
            self.exh_L = ttk.Label(self, font=('Arial', 14))
            self.hp_L.grid(row=1, column=0)
            self.exh_L.grid(row=2, column=0)
            self.x_B = ttk.Button(self, text='Examine', command = self.examine)
            self.x_B.grid(row=3, column=0)
        def update(self):
            self.hp_L.configure(text = f'HP: {self.enemy.hp}/{self.enemy.max_hp}')
            self.exh_L.configure(text = f'Ex: {self.enemy.exhaust}/{self.enemy.max_exh}')
        def examine(self):
            log(self.enemy.desc)

class Log(tk.Canvas):
    def __init__(self, root):
        super().__init__(root)
        global current_log
        current_log = self
        self.bar = ttk.Scrollbar(self)
        self.text = tk.Text(self, wrap='word',
                            yscrollcommand = self.bar.set,
                            background='black',
                            foreground='white'
                            )
        self.bar.pack(side=tk.RIGHT, fill='y')
        global log_msgs
        for m in log_msgs:
            self.text.insert(index=tk.END, chars = m)
            self.text.insert(index=tk.END, chars = '\n')
        self.text.pack(side=tk.TOP, fill='both', expand=True)
        self.text.see(tk.END)
        self.text.config(state = tk.DISABLED) # stops from being able to type into

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
        def __init__(self, root, action):
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
            actn_b.grid(row = 0, ipady = 20)
            info_b.grid(row = 1)
        
        def choose_action(self):
            global game
            game.select_player_action(self.action)
        def examine_action(self):
            log(f'{self.action.name}: \n{self.action.desc}')
            log(f'  Exhaustion Cost: {self.action.exh_cost}')
            if hasattr(self.action, 'reach'):
                log(f'  Reach: {self.action.reach}')
            if hasattr(self.action, 'dmg_mod'):
                log(f'  Damage: x{self.action.dmg_mod}')
                log(f'  Stagger: x{self.action.stagger_mod}')
            if hasattr(self.action, 'styles'):
                if len(self.action.styles) > 0:
                    for i,s in enumerate(self.action.styles):
                        if i == 0:
                            ls = [s]
                        else:
                            ls.append(f', {s}')
                    log(f'  Attack Styles: {ls}')
            log('\n')
   
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

def EnterCombat(enemies:list):
    global current_frame
    global game
    if current_frame is not None:
        current_frame.destroy()
    current_frame = CombatWindow(root, game.plr.get_combat_actions(), enemies)
    current_frame.place(relwidth=1.0, relheight=1.0)
    print('created combat')