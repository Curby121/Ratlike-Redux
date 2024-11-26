import baseclasses as bc
import effects

class Gem(bc.Item):
    effect_class:effects.Effect # a CLASS
    effect_amount:float
    def make_effect(self) -> effects.Effect:
        return self.effect_class(self.effect_amount)

class Ring(bc.Equippable):
    slot = 'Hand'
    def __init__(self, gem_class:Gem, **kwargs):
        super().__init__(**kwargs)
        self.name = gem_class.name + ' Ring'
        self.effects = [gem_class.make_effect(gem_class)]

class Ruby(Gem):
    name = 'Ruby'
    desc = 'A firey Red Stone'
    effect_class = effects.Stregth
    effect_amount = 1

class Opal(Gem):
    name = 'Opal'
    desc = 'A clear stone. Peering through it makes the world seem clearer...'
    effect_class = effects.Accuracy
    effect_amount = 1.5