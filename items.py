import baseclasses as bc
import effects
import random
import weapons
random.seed()

class Gem(bc.Item):
    effect_class:effects.Effect # a CLASS
    effect_amount:float
    def make_effect(self) -> effects.Effect:
        return self.effect_class(self.effect_amount)

class Jewelry(bc.Equippable):
    def __init__(self, gem_class:Gem, **kwargs):
        super().__init__(**kwargs)
        self.effects = [gem_class.make_effect(gem_class)]

class Ring(Jewelry):
    slot = 'Hand'
    def __init__(self, gem_class:Gem, **kwargs):
        super().__init__(gem_class, **kwargs)
        self.name = gem_class.name + ' Ring'
        self.desc = f'A ring set with {gem_class.desc}'

class Amulet(Jewelry):
    slot = 'Neck'
    def __init__(self, gem_class:Gem, **kwargs):
        super().__init__(gem_class, **kwargs)
        self.name = gem_class.name + ' Amulet'
        self.desc = f'An amulet set with {gem_class.desc}'

class Ruby(Gem):
    name = 'Ruby'
    desc = 'A firey Red Stone'
    effect_class = effects.Stregth
    effect_amount = 1

class Opal(Gem):
    name = 'Opal'
    desc = 'A clear stone. Peering through it makes the world seem clearer...'
    effect_class = effects.Accuracy
    effect_amount = 2

class DropTable:
    '''Drop tables should never be instantiated'''
    drops:list[tuple[bc.Item, int]]
    def __init__(self) -> None:
        raise Exception('Never instantiate a drop table')
    def roll(self) -> bc.Item:
        items, wgts = zip(*self.drops)
        drop = random.choices(items, wgts)[0]
        if issubclass(drop, DropTable):
            return RollTable(drop)
        else:
            d = drop()
            return d

def RollTable(table:DropTable):
    return table.roll(table)

class RandomJewelry(DropTable):
    gems = [Ruby, Opal]
    slots = [Amulet, Ring]
    def roll(self):
        s = random.choice(self.slots)
        g = random.choice(self.gems)
        return s(g)

class BasicDrops(DropTable):
    drops = [
        (RandomJewelry, 5),
        (weapons.LeatherCap, 1),
        (weapons.LeatherTunic, 1),
        (weapons.Dagger, 2),
        (weapons.Mace, 2),
        (weapons.Sword, 2),
        (weapons.Spear, 2),
    ]