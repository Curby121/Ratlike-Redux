import baseclasses as bc
import items
import enemies

class Chest(bc.RoomObject):
    name = 'Chest'
    def __init__(self, contents:list = None):
        self.desc = 'What could be inside?'
        self.actions = [
            self.Open(parent = self)
        ]
        self.contents = contents
        if self.contents is None:
            self.contents = []
        self.contents.extend(self.contents)
        if len(self.contents) == 0:
            self.contents.append(items.RollTable(items.BasicDrops))
        super().__init__()
        
    class Open(bc.ObjectAction):
        name = 'Open'
        def resolve(self, gameobj):
            while len(self.parent.contents) > 0:
                import game
                game.current_room.add_to_floor(self.parent.contents.pop())
            self.parent.actions.remove(self)
            self.parent.desc = f'Much less interesting now...'
            gameobj._reload_room()

class Troll(bc.RoomObject):
    name = 'Sleeping Troll'
    desc = 'Fury awaits whatever distrubs this beast.'
    def __init__(self):
        self.actions = [
            self.Wake(parent = self)
        ]
        super().__init__()
    class Wake(bc.ObjectAction):
        name = 'Disturb'
        def resolve(self, gameobj):
            import game
            game.current_room.enemies.append(enemies.CaveTroll())
            game.current_room.centerpiece = None
            print('resolve')
            gameobj._reload_room()