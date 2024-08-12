import baseclasses as bc

class Chest(bc.RoomObject):
    name = 'Chest'
    desc = 'What could be inside?'
    def __init__(self, contents:list):
        self.actions = [
            self.Open(parent = self)
        ]
        self.contents = contents
        super().__init__()
        
    class Open(bc.ObjectAction):
        name = 'Open'
        def resolve(self, game):
            while len(self.parent.contents) > 0:
                game.room.add_to_floor(self.parent.contents.pop())
            self.parent.actions.remove(self)
            game._reload_room()