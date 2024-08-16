'''Definitions for enemies.'''
import baseclasses as bc
import strategies as st
import actions

class Rat(bc.Enemy):
    name = 'Rat'
    desc = 'It thinks it\'s the main character'
    max_hp = 18
    max_exh = 50
    exh_rec = 15
    dmg_base = 8
    stagger_base = 4
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
    max_hp = 22
    max_exh = 35
    exh_rec = 7
    dmg_base = 4
    stagger_base = 10
    strategy_class = st.Basic
    actions = [
        (actions.Poke, 60),
        (actions.Stab, 30),
        (actions.Dodge, 50)
    ]
    
class Skeleton(bc.Enemy):
    name = 'Skeleton'
    desc = 'Rattling bones and a sturdy club.'
    max_hp = 30
    max_exh = 75
    exh_rec = 6
    dmg_base = 6
    stagger_base = 16
    strategy_class = st.Basic
    actions = [
        (actions.Smash, 60),
        (actions.Stab, 40),
        (actions.Block, 35)
    ]

class CaveTroll(bc.Enemy):
    name = 'Cave Troll'
    desc = 'Large, scary and blue'
    max_hp = 99
    max_exh = 80
    exh_rec = 8
    dmg_base = 25
    stagger_base = 26
    strategy = st.Troll
    actions = [
        (actions.Bite, 40),
        (actions.TrollReady, 60)
    ]

class StaggerChild(bc.Enemy):
    name = 'Talker Child'
    desc = "This annoying child want's you to enjoy prison"
    max_hp = 20
    max_exh = 50
    exh_rec = 6
    dmg_base = 6
    stagger_base = 16
    strategy = st.Basic
    actions = [
        (actions.Talk, 60),
        (actions.Stab, 40),
        (actions.Block, 35)
    ]