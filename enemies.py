'''Definitions for enemies.'''
import baseclasses as bc
import strategies as st
import actions
import effects

class Rat(bc.Enemy):
    name = 'Rat'
    desc = 'It thinks it\'s the main character'
    max_hp = 7
    bal_max = 6
    dmg_base = 5
    stagger_base = 1
    parry = 1
    defense = 2
    strategy_class = st.Basic
    actions = [
        (actions.Bite, 4),
        (actions.Dodge, 2)
    ]
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.grant_effect(effects.BalanceHeal(rate = 0.5))
    
class Goblin(bc.Enemy):
    name = 'Goblin'
    desc = 'A stinky goblin! Look out for it\'s pointy spear!'
    max_hp = 12
    bal_max = 16
    dmg_base = 3
    stagger_base = 4
    parry = 3
    defense = 4
    parry_class = actions.Stab
    strategy_class = st.Basic
    actions = [
        (actions.Lunge, 20),
        (actions.Stab, 50)
    ]

class Skeleton(bc.Enemy):
    name = 'Skeleton'
    desc = 'Rattling bones and a sturdy club.'
    max_hp = 10
    bal_max = 18
    dmg_base = 6
    stagger_base = 5
    parry = 2
    defense = 3
    strategy_class = st.Basic
    actions = [
        (actions.Smash, 60),
        (actions.Chop, 40),
        (actions.Block, 15)
    ]

class CaveTroll(bc.Enemy):
    name = 'Cave Troll'
    desc = 'Large, scary and blue!'
    max_hp = 45
    bal_max = 30
    dmg_base = 4
    stagger_base = 5
    parry = 3
    defense = 6
    strategy_class = st.Troll
    actions = [
        (actions.TrollKick, 50),
        (actions.TrollReady, 60)
    ]
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.attack_ready = False
        self.grant_effect(effects.BalanceHeal(rate = 0.1))
        self.grant_effect(effects.Stregth(5))