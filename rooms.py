import baseclasses as bc
import roomobjects as ro
import enemies
import random
random.seed()

class LabyrinthRoom(bc.Room):
    encounters = [
        ([enemies.Goblin], 30),
        ([enemies.Skeleton], 10),
        ([], 120)
    ]
    centerpieces = [
        (ro.Chest, 15),
        (None, 85)
    ]
    def __init__(self, conn_rooms: dict[str,] = {}, enemies: list[bc.Enemy] = [], centerpiece: bc.RoomObject = None):
        if len(enemies) == 0:
            es = self.rand_choice(self.encounters)
            for e in es:
                enemies.append(e())
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
        dirs = list(self.conn_rooms.keys())
        # remove all used dirs
        for e in self.exits:
            if e.direction in dirs:
                dirs.remove(e.direction)
        for dir in dirs:
            print('new room')
            r = LabyrinthRoom(conn_rooms = {
                    self._dir_opposites[dir] : self
                })
            self.add_exit(dir, r)
        return super().enter(game)