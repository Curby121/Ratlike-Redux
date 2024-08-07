'''Definitions for enemies.'''
import baseclasses as bc
import strategies as st
import actions

# Currently unusable -- uppdate strategies
class Rat(bc.Enemy):
    name = 'Rat'
    desc = 'It thinks it\'s the main character'
    max_hp = 6
    max_exh = 70
    exh_rec = 9
    dmg_base = 3
    stagger_base = 4
    strategy = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
class Goblin(bc.Enemy):
    name = 'Goblin'
    desc = 'A Stinky Goblin! Look out for it\'s pointy spear!'
    max_hp = 26
    max_exh = 45
    exh_rec = 7
    dmg_base = 4
    stagger_base = 10
    strategy = st.Basic
    actions = [
        (actions.Lunge, 60),
        (actions.Jab, 30),
        (actions.Dodge, 50)
    ]
    
class Skeleton(bc.Enemy):
    name = 'Skeleton'
    desc = 'Rattling bones and a heavy club.'
    max_hp = 22
    max_exh = 75
    exh_rec = 6
    dmg_base = 6
    stagger_base = 16
    strategy = st.Basic
    actions = [
        (actions.Smash, 60),
        (actions.Stab, 40),
        (actions.Block, 35)
    ]