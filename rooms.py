import baseclasses as bc
import roomobjects as ro
import enemies
import random
random.seed()

class LabyrinthRoom(bc.Room):
    encounters = [
        ([enemies.Rat], 50),
        ([enemies.Goblin], 30),
        ([enemies.Skeleton], 15),
        ([], 90)
    ]
    centerpieces = [
        (ro.Chest, 20),
        (None, 80)
    ]
    def __init__(self, conn_rooms: dict[str,] = {}, enemies: list[bc.Enemy] = [], centerpiece: bc.RoomObject = None):
        if len(enemies) == 0:
            es = self.rand_choice(self.encounters)
            for e in es:
                new_e:bc.Enemy = e()
                enemies.append(new_e)
        if centerpiece is None:
            c = self.rand_choice(self.centerpieces)
            if c is not None:
                centerpiece = c()
        
        super().__init__(enemies = enemies, centerpiece = centerpiece, conn_rooms = conn_rooms)

        rm_count = random.choice(range(2)) + 2 # 2 - 4 rooms
        rm_count -= len(self.conn_rooms)

        for i in range(rm_count):
            dirs = ['n','s','e','w']
            for d,r in self.conn_rooms.items():
                dirs.remove(d)
            rand_dir = random.choice(dirs)
            self.conn_rooms[rand_dir] = None
    def enter(self, game):
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
        return super().enter(game)