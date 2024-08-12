import baseclasses as bc
import weapons

class Chest(bc.RoomObject):
    name = 'Chest'
    desc = 'What could be inside?'
    def __init__(self, contents:list):
        super().__init__()
        self.actions = [
            self.Open(parent = self)
        ]
        self.contents = contents
    class Open(bc.ObjectAction):
        name = 'Open'
        def resolve(self, room:bc.Room):
            while len(self.parent.contents) > 0:
                room.add_to_floor(self.parent.contents.pop())