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

class WoodenShield(bc.Weapon):
    name = 'Wooden Shield'
    desc = 'A small round wooden shield.'
    style = 'None'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attacks = [
            actions.Block
        ]