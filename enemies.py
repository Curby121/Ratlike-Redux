'''Definitions for enemies.'''
import baseclasses as bc
import strategies as st
import actions

class Rat(bc.Enemy):
    name = 'Rat'
    desc = 'It thinks it\'s the main character'
    max_hp = 18
    bal_max = 50
    bal_rec = 8
    dmg_base = 8
    stagger_base = 4
    parry = 1
    strategy_class = st.Basic
    actions = [
        (actions.Bite, 3),
        (actions.RatJump, 10),
        (actions.Dodge, 10)
    ]
    def get_reaction(self):
        return actions.Bite
    
class Goblin(bc.Enemy):
    name = 'Goblin'
    desc = 'A stinky goblin! Look out for it\'s pointy spear!'
    max_hp = 12
    bal_max = 16
    dmg_base = 3
    stagger_base = 2
    parry = 3
    parry_class = actions.Stab
    strategy_class = st.Basic
    actions = [
        (actions.Lunge, 20),
        (actions.Stab, 50)
    ]

class Skeleton(bc.Enemy):
    name = 'Skeleton'
    desc = 'Rattling bones and a sturdy club.'
    max_hp = 22
    bal_max = 20
    dmg_base = 6
    stagger_base = 6
    parry = 2
    strategy_class = st.Basic
    actions = [
        (actions.Smash, 60),
        (actions.Chop, 40),
        (actions.Block, 15)
    ]

class CaveTroll(bc.Enemy):
    name = 'Cave Troll'
    desc = 'Large, scary and blue'
    max_hp = 99
    bal_max = 80
    bal_rec = 8
    dmg_base = 25
    stagger_base = 26
    strategy = st.Troll
    actions = [
        (actions.Bite, 40),
        (actions.TrollReady, 60)
    ]