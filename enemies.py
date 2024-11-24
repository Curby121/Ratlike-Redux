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
    strategy_class = st.Basic
    actions = [
        (actions.Bite, 4),
        (actions.Dodge, 10)
    ]
    def gen_effects(self, effs: list = []) -> list:
        e = effects.BalanceHeal()
        effs.append(e)
        return super().gen_effects(effs)
    
class Goblin(bc.Enemy):
    name = 'Goblin'
    desc = 'A stinky goblin! Look out for it\'s pointy spear!'
    max_hp = 12
    bal_max = 16
    dmg_base = 3
    stagger_base = 4
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
    max_hp = 10
    bal_max = 18
    dmg_base = 6
    stagger_base = 5
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