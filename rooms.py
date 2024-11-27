import baseclasses as bc
import roomobjects as ro
import enemies
import random
random.seed()

class LabyrinthRoom(bc.Room):
    centerpieces = [
        (ro.Chest, 80),
        (None, 30)
    ]
    encounters = [
        (enemies.Rat, 50),
        (enemies.Goblin, 30),
        (enemies.Skeleton, 15),
        (None, 10)
    ]
    
    def __init__(self, conn_rooms: dict[str,] = None, enemies: list[bc.Enemy] = None, centerpiece: bc.RoomObject = None):
        if enemies is None:
            self.enemies = []
            new_e_class:bc.Enemy = self.rand_choice(self.encounters)
            if new_e_class is not None:
                self.enemies.append(new_e_class())
        if centerpiece is None:
            c = self.rand_choice(self.centerpieces)
            if c is not None:
                centerpiece = c()

        # sleeping troll chance
        if random.randint(0,4) >= 0 and len(self.enemies) == 0:
            centerpiece = ro.Troll()
        
        super().__init__(enemies = enemies, centerpiece = centerpiece, conn_rooms = conn_rooms)

        rm_count = random.choice(range(2)) + 2 # 2 - 4 rooms
        rm_count -= len(self.conn_rooms)

        for i in range(rm_count):
            dirs = ['n','s','e','w']
            for d,r in self.conn_rooms.items():
                dirs.remove(d)
            rand_dir = random.choice(dirs)
            self.conn_rooms[rand_dir] = None
    def on_enter(self):
        # make a new room for connected rooms that have not been generated yet
        dirs = list(self.conn_rooms.keys())
        for exit in self.exits:
            if exit.direction in dirs:
                dirs.remove(exit.direction) # remove dirs that already have an exit
        for dir in dirs:
            r = LabyrinthRoom(conn_rooms = {
                    self._dir_opposites[dir] : self
                })
            self.add_exit(dir, r)