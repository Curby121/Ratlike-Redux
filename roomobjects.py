import baseclasses as bc
import GUI
import weapons

class Chest(bc.RoomObject):
    name = 'Chest'
    def __init__(self, contents:list = []):
        self.desc = 'What could be inside?'
        self.actions = [
            self.Open(parent = self)
        ]
        self.contents = contents
        if len(self.contents) == 0:
            self.contents.append(weapons.WoodenShield())
        super().__init__()
        
    class Open(bc.ObjectAction):
        name = 'Open'
        def resolve(self, game):
            while len(self.parent.contents) > 0:
                game.room.add_to_floor(self.parent.contents.pop())
            self.parent.actions.remove(self)
            self.parent.desc = f'Much less interesting now...'
            game._reload_room()