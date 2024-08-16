'''This should probably live in game.py'''
# TODO: move dis bihth
import asyncio
import tkinter as tk
from tkinter import ttk

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

class BaseWindow(tk.Canvas):
    '''Contains player stats to the left and log to the right'''
    def __init__(self):
        super().__init__(root, bg='black')
        self.log = self.Log(self)
        self.log.place(relx=1, rely=0.5, relheight=1, relwidth=0.25, anchor='e')
        global current_log
        current_log = self.log

    def Updt(*args):
        '''Override in inhereted classes to update indo every frame'''
        # TODO: add updates
        pass
    
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

class ObjectBar(tk.Frame):
    objs:list[ttk.Frame] = None
    def set_frames(self, objects:list[ttk.Frame] = None):
        self.configure(bg='black')
        self.objs:list[ttk.Frame] = objects
        for i,a in enumerate(self.objs):
            self.columnconfigure(i, weight=1)
            a.grid(row = 0, column = i, padx=3)

class RoomWindow(BaseWindow):
    '''Dungeon Room view. Rooms can contain a centerpiece, exits, and ground objects'''
    def __init__(self, room):
        super().__init__()
        exits:list = []
        centerpiece = room.centerpiece
        grounds = []

        exit_canvas = tk.Frame(bg='black')
        ground_bar = ObjectBar(self)

        for e in room.exits:
            exits.append(self.Exit(exit_canvas, e))
        for obj in room.floor_objects:
            grounds.append(self.Object(ground_bar, obj))
        for item in room.floor_items:
            grounds.append(self.Item(ground_bar, item))

        if centerpiece is not None:
            centerpiece_lab = self.Object(self, centerpiece)
            centerpiece_lab.lab.config(font = ('Arial', 24), padding=10)
            centerpiece_lab.place(relx=0.5,rely=0.5, anchor = 'center')

        if len(exits) > 0:
            exit_canvas.place(relx=0.5, rely=0.05, anchor='n')
            for e in exits:
                e.grid(row=e.pos[1], column=e.pos[0])
        if len(grounds) > 0:
            ground_bar.set_frames(grounds)
            ground_bar.place(relx=0.5,rely=0.95, anchor='s')

    class Exit(tk.Frame):
        def __init__(self, root, exit):
            super().__init__(root)
            self.exit = exit
            dir:str = self.exit.direction
            name = ''
            self.pos:list[int] = [1, 1] # center of 3x3
            if dir[0] == 'n':
                name += 'North'
                self.pos[1] += -1
            elif dir[0] == 's':
                name += 'South'
                self.pos[1] += 1

            elif dir[0] == 'e':
                name += 'East'
                self.pos[0] += 1
            elif dir[0] == 'w':
                name += 'West'
                self.pos[0] += -1
            self.but = ttk.Button(
                self,
                text = name,
                command = self.move
            )
            self.but.pack(ipady=15)
        def move(self):
            global game
            self.exit.dest_room.enter(game)
            log('You walk through the door...')
    
    class Object(tk.Frame):
        def __init__(self, root, obj):
            super().__init__(root)
            self.obj = obj
            self.lab = ttk.Label(
                self,
                text = obj.name
            )
            self.lab.grid(row=0, column=0)
            for i,a in enumerate(obj.actions):
                b = ttk.Button(
                    self,
                    text = a.name,
                    command = self.resolve(a.resolve)
                )
                b.grid(row=i+1,column=0)
        def resolve(self, fn):
            '''This stores a copy of the resolve function on the button'''
            return lambda: fn(game)

    class Item(tk.Frame):
        def __init__(self, root, item):
            super().__init__(root)
            self.item = item
            lab = ttk.Label(
                self,
                text = self.item.name,
                font = ('Arial', 14)
            )
            take_b = ttk.Button(
                self,
                text = 'Take',
                command = self.item.take
            )
            examine_b = ttk.Button(
                self,
                text = "Examine",
                command = self.item.examine
            )
            lab.grid(row = 0, column = 0)
            take_b.grid(row = 1, column = 0)
            examine_b.grid(row = 2, column = 0)

# TODO: currently only first enemy is displayed
class CombatWindow(BaseWindow):
    def __init__(self, plr_actions, enemies:list):
        super().__init__()
        actn_bar = self.ActionBar(self, plr_actions)
        actn_bar.place(relx=0.5, rely=0.75, anchor='center')
        self.plr_stats = self.PlrStats(self)
        self.plr_stats.place(rely=0.6, relx=0.5, anchor='center', width = 250, height=70)
        self.enemy_stats = self.EnemyStats(self, enemies[0])
        self.enemy_stats.place(rely=0.25, relx=0.5, anchor='center')

        self.dist_L = ttk.Label(self, font=('Arial', 14), padding = 4)
        self.dist_L.place(relx=0.5, rely=0.38, anchor='center')

        self.Updt()

    def Updt(self):
        self.plr_stats.update()
        self.enemy_stats.update()
        self.dist_L.configure(text = f'Dist: {self.enemy_stats.enemy.distance}')
    
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

    class ActionBar(ObjectBar):
        def __init__(self, root, actions:list):
            super().__init__(root)
            actns = []
            for a in actions:
                actns.append(self.PlayerAction(self, a))
            self.set_frames(actns)

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
                log('')
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

def EnterRoom(room):
    global current_frame
    global game
    if current_frame is not None:
        current_frame.destroy()
    if len(room.enemies) != 0:
        current_frame = CombatWindow(game.plr.get_combat_actions(), room.enemies)
    else:
        current_frame = RoomWindow(room)
    current_frame.place(relwidth=1.0, relheight=1.0)