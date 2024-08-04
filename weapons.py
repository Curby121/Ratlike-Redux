import baseclasses as bc
import actions

class Dagger(bc.Weapon):
    name = 'Dagger'
    desc = 'Stick em with the pointy end!'
    style = 'None'
    def __init__(self):
        super().__init__()
        self.attacks = [
            actions.Stab
        ]
        self.dodge_class = actions.Jab