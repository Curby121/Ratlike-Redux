'''This should probably live in game.py'''
# TODO: move dis bihth
import asyncio
import tkinter as tk
from tkinter import ttk

root_win = tk.Tk()
root_win.title('RatLike Redux')
root_win.configure(background = "black")
root_win.geometry("1280x720")
root_win.rowconfigure(0, weight=1)
root_win.columnconfigure(1, weight=1)

game = None
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
        super().__init__(root_win, bg='black')
        self.log = self.Log(self)
        self.log.place(relx=1, rely=0.5, relheight=1, relwidth=0.25, anchor='e')
        global current_log
        current_log = self.log

        self.plr_panel = self.PlrStuff(self)
        self.plr_panel.place(relx=0, rely=0.5, relheight=1, relwidth=0.25, anchor='w')

    def Updt(*args):
        '''Override in inhereted classes to update info every frame'''
        # TODO: add updates

    def Refresh(*args):
        '''Re fetch data to check for game state changes.'''
        pass
    
    class PlrStuff(tk.Canvas):
        def __init__(self, root):
            super().__init__(root, background='black')
            self.face = ttk.Label(self, text='YourFace.jpg', font=('Arial', 14), padding=5)
            self.face.place(relx=0.5, rely=0, height=80, relwidth=.9, anchor='n')
            self.eqp = ttk.Label(self, text='eqp', font=('Times New Roman', 11))
            import game
            self.eqp.configure(text=game.plr.examine_equipment())
            self.eqp.place(relx=0.5, rely=0.2, height=50, relwidth=0.9, anchor='n')
            self.buttons = self.Buttons(self)
            self.buttons.place(relx=0.5, rely=0.75, relheight=.2, relwidth=.5, anchor='s')

        class Buttons(tk.Canvas):
            def __init__(self, root):
                super().__init__(root)
                self.inv = tk.Button(self, text='Inventory', command = ViewInventory)
                self.inv.pack(pady=8)
                self.inv = tk.Button(self, text='Talents', command = ViewTalents)
                self.inv.pack(pady=8)
                self.inv = tk.Button(self, text='Character', command = ViewCharacter)
                self.inv.pack(pady=8)

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

class PopUp(tk.Canvas):
    def __init__(self):
        super().__init__(root_win, bg='red')
        self.Exit = ttk.Button(self, text='X', command=KillPopup)
        self.Exit.pack(anchor='ne', padx=3, pady=3)
        self.place(relx=0.5, rely= 0.5, relwidth=0.48, relheight=0.98, anchor='center')

    class List(tk.Canvas):
        def __init__(self, root):
            super().__init__(root, background='blue')
            self.frame = tk.Frame(self, background='green')
            self.bar = ttk.Scrollbar(self, command=self.yview)
            self.configure(yscrollcommand = self.bar.set)
            self.bar.pack(side=tk.RIGHT, fill='y')
            self.place(relx=0.5, rely= 0.5, relwidth=.9, relheight=.9, anchor='center')

            self.update_idletasks() # updates winfo_width()
            self.create_window(self.winfo_width()/2, 0, anchor='n', window=self.frame)
            self.frame.bind("<Configure>", self.modconfig)

        def modconfig(self, event):
            self.configure(scrollregion=self.frame.bbox('all'), border=3)

class Inv(PopUp):
    def __init__(self):
        super().__init__()
        self.list = PopUp.List(self)
        import game
        for i, item in enumerate(game.plr.inv):
            itemobj = self.Item(self.list.frame, item)
            itemobj.grid(row=i)
            self.list.frame.rowconfigure(i, minsize=80)

    def refresh(func, *args):
        def deco():
            func(*args)
            KillPopup()
            ViewInventory()
        return deco

    class Item(tk.Canvas):
        def __init__(self, root:tk.Frame, item):
            super().__init__(root, background='black')
            import baseclasses as bc
            item:bc.Item
            actns = item.inventory_actions()
            count = len(actns)
            for i,a in enumerate(actns):
                butt = tk.Button(self, text=a[0], font=('Arial', 12), command=Inv.refresh(a[1]))
                butt.grid(row=0, column=i+1, sticky='e')

            self.name = ttk.Label(self, text=item.name, font=('Arial', 16))
            self.drop = tk.Button(self, text='Drop', font=('Arial', 12), command=Inv.refresh(item.drop, game.room))
            self.examine = tk.Button(self, text='Examine', font=('Arial', 12), command=Inv.refresh(item.examine))
            
            self.name.grid(row =0, sticky='w')
            self.examine.grid(row = 0, column=count+1, sticky='e')
            self.drop.grid(row = 0, column=count+2, sticky='e')

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
        self.room = room
        self.Refresh()

    def Refresh(self):
        exits:list = []
        self.centerpiece = self.room.centerpiece
        grounds = []

        exit_canvas = tk.Frame(bg='black')
        try:
            self.ground_bar.destroy()
        except Exception as e:
            pass
        self.ground_bar = ObjectBar(self)
        for e in self.room.exits:
            exits.append(self.Exit(exit_canvas, e))
        for obj in self.room.floor_objects:
            grounds.append(self.Object(self.ground_bar, obj))
        for item in self.room.floor_items:
            grounds.append(self.Item(self.ground_bar, item))

        if self.centerpiece is not None:
            try:
                self.centerpiece_lab.destroy()
            except Exception as e:
                pass
            self.centerpiece_lab = self.Object(self, self.centerpiece)
            self.centerpiece_lab.lab.config(font = ('Arial', 24), padding=10)
            self.centerpiece_lab.place(relx=0.5,rely=0.5, anchor = 'center')

        if len(exits) > 0:
            exit_canvas.place(relx=0.5, rely=0.05, anchor='n')
            for e in exits:
                e.grid(row=e.pos[1], column=e.pos[0])
        if len(grounds) > 0:
            self.ground_bar.set_frames(grounds)
            self.ground_bar.place(relx=0.5,rely=0.95, anchor='s')

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
        def take(self):
            print(f'take room: {game.room}')
            self.item.take(game.room)
            current_frame.Refresh()
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
                command = self.take
            )
            examine_b = ttk.Button(
                self,
                text = "Examine",
                command = self.item.examine
            )
            lab.grid(row = 0, column = 0)
            take_b.grid(row = 1, column = 0)
            examine_b.grid(row = 2, column = 0)

current_frame:RoomWindow = None

class CombatWindow(BaseWindow):
    def __init__(self, enemies:list):
        super().__init__()
        self.plr_stats = self.PlrStats(self)
        self.plr_stats.place(rely=0.6, relx=0.5, anchor='center', width = 260, height=70)
        self.enemy_stats = self.EnemyStats(self, enemies[0])
        self.enemy_stats.place(rely=0.25, relx=0.5, anchor='center')

        self.enemy_actn = self.ActionLabel(self)
        self.enemy_actn.place(relx=0.5, rely=0.38, anchor='center')
        self.player_actn = self.ActionLabel(self)
        self.player_actn.place(relx=0.5, rely=0.5, anchor='center')

        self.Updt()

    def make_plr_actions(self, plr_actions, available:list[bool]):
        assert len(plr_actions) > 0
        self.actn_bar = self.ActionBar(self, plr_actions, available)
        self.actn_bar.place(relx=0.5, rely=0.75, anchor='center')

    def Updt(self):
        self.plr_stats.update()
        self.enemy_stats.update()
        self.enemy_actn.update(game.get_enemy_action())
        self.player_actn.update(game.get_player_action())

    def Refresh(self):
        p_acts = game.plr.get_combat_actions()
        self.make_plr_actions(p_acts, game.plr.get_availables(p_acts))
    
    class PlrStats(ttk.Frame):
        def __init__(self, root):
            super().__init__(root)
            self.hp_L = ttk.Label(self, font=('Arial', 18))
            self.bal_L = ttk.Label(self, font=('Arial', 18))
            self.hp_B = ttk.Progressbar(self, mode = 'determinate')
            self.bal_B = ttk.Progressbar(self, mode = 'determinate')
            self.hp_L.place(relx=0.45, rely=0.5, anchor='se')
            self.bal_L.place(relx=0.55, rely=0.5, anchor='sw')
            self.hp_B.place(relx=0.45, rely=0.55, anchor='ne')
            self.bal_B.place(relx=0.55, rely=0.55, anchor='nw')
        def update(self):
            self.hp_L.configure(text = f'HP: {game.plr.hp}/{game.plr.max_hp}')
            self.bal_L.configure(text = f'Bal: {game.plr.balance}/{game.plr.bal_max}')
            self.hp_B.configure(value = 100*(game.plr.hp / game.plr.max_hp))
            self.bal_B.configure(value = 100*(game.plr.balance / game.plr.bal_max))

    class EnemyStats(ttk.Frame):
        def __init__(self, root, enemy):
            super().__init__(root, padding=15)
            self.enemy = enemy
            self.label = ttk.Label(self, text=enemy.name, font=('Arial', 16))
            self.label.grid(row=0, column=0)
            self.hp_L = ttk.Label(self, font=('Arial', 14))
            self.bal_L = ttk.Label(self, font=('Arial', 14))
            self.hp_L.grid(row=1, column=0)
            self.bal_L.grid(row=2, column=0)
            self.x_B = ttk.Button(self, text='Examine', command = self.examine)
            self.x_B.grid(row=3, column=0)
        def update(self):
            self.hp_L.configure(text = f'HP: {self.enemy.hp}/{self.enemy.max_hp}')
            self.bal_L.configure(text = f'Bal: {self.enemy.balance}/{self.enemy.bal_max}')
            
        def examine(self):
            log(self.enemy.desc)

    class ActionLabel(ttk.Frame):
        def __init__(self, root):
            super().__init__(root)
            self.name = ttk.Label(self, font=('Arial', 14))
            self.timer = ttk.Label(self, font=('Arial', 14))
            self.info = ttk.Button(self,
                text = 'Info',
                command = self.x
                )
            self.action = None
            self.name.grid()
            self.timer.grid(row=0, column=1)
            self.info.grid(row=1, columnspan=2)
        
        def update(self, action):
            self.action = action
            if action is None:
                self.name.configure(text = '...')
                self.timer.configure(text = '?')
                self.info.config(state = tk.DISABLED)
                return
            self.name.configure(text = action.name)
            self.timer.configure(text = str(action.timer))
            self.info.config(state = tk.NORMAL)

        def x(self):
            examine_action(self.action)

    class ActionBar(ObjectBar):
        def __init__(self, root, actions:list, available:list[bool]):
            super().__init__(root)
            actns = []
            for i,a in enumerate(actions):
                actns.append(self.PlayerAction(self, a, available[i]))
            self.set_frames(actns)

        class PlayerAction(ttk.Frame):
            def __init__(self, root, action, active:bool):
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
                    command = self.x
                    )
                actn_b.grid(row = 0, ipady = 20)
                info_b.grid(row = 1)
                if not active:
                    actn_b.config(state = tk.DISABLED)
            
            def choose_action(self):
                global game
                game.select_player_action(self.action)

            def x(self):
                examine_action(self.action)

def init(gme):
    global game
    game = gme

async def run():
    while True:
        if current_frame is not None:
            current_frame.Updt()
        root_win.update()
        root_win.update_idletasks()
        await asyncio.sleep(0)

def EnterRoom(room):
    global current_frame
    if current_frame is not None:
        current_frame.destroy()
    if len(room.enemies) != 0:
        EnterCombatRoom(room)
    else:
        current_frame = RoomWindow(room)
    current_frame.place(relwidth=1.0, relheight=1.0)

def EnterCombatRoom(room) -> CombatWindow:
    global current_frame
    if current_frame is not None:
        current_frame.destroy()
    current_frame = CombatWindow(room.enemies)
    current_frame.place(relwidth=1.0, relheight=1.0)
    return current_frame

pop = None
def ViewInventory():
    global pop
    pop = Inv()

def ViewTalents():
    print('View Talents')

def ViewCharacter():
    print('View Character')

def KillPopup():
    global pop
    pop.destroy()
    pop = None
    current_frame.Refresh()

def examine_action(action):
    log('')
    log(f'{action.name} | {action.timer}: \n{action.desc}')
    if hasattr(action, 'acc'):
        log(f'  Accuracy:  {action.acc}')
        log(f'  Parry:    x{action.parry_mod}')
    if hasattr(action, 'dmg_mod'):
        log(f'  Damage:   x{action.dmg_mod}')
        log(f'  Stagger:  x{action.stagger_mod}')
    log    (f'  Balance:   {action.bal_use_cost+action.bal_resolve_cost} ({action.bal_use_cost},{action.bal_resolve_cost})')
    if hasattr(action, 'styles'):
        if len(action.styles) > 0:
            for i,s in enumerate(action.styles):
                if i == 0:
                    ls = [s]
                else:
                    ls.append(f', {s}')
            log(f'  Attack Styles: {ls}')

def updt_plr_combat(acts, activated:list[bool]):
    assert isinstance(current_frame, CombatWindow)
    #current_frame.ActionBar