'''Weapons and Equipment'''

import baseclasses as bc
import actions
import effects

class Dagger(bc.Weapon):
    name = 'Dagger'
    desc = 'Stick em with the pointy end!'
    value = 5
    dmg_base = 5
    parry = 4
    attacks = [
        actions.Stab,
        actions.DaggerStab
    ]

class Sword(bc.Weapon):
    name = 'Iron Sword'
    desc = 'Swordsman\'s best friend.'
    value = 15
    dmg_base = 5
    parry = 8
    attacks = [
        actions.Slash,
        actions.Chop
    ]

class Spear(bc.Weapon):
    name = 'Wooden Spear'
    desc = 'A long wooden shaft with a sharp piece of iron lashed on top.'
    dmg_base = 5
    twohanded = True
    value = 15
    parry = 5
    attacks = [
        actions.Lunge,
        actions.Stab
    ]

class Mace(bc.Weapon):
    name = 'Mace'
    desc = 'A lethal ball on the end of a sturdy handle.'
    value = 15
    dmg_base = 8
    parry = 4
    attacks = [
        actions.Chop,
        actions.Smash
    ]

class WoodenShield(bc.Weapon):
    name = 'Wooden Shield'
    desc = 'A small round wooden shield.'
    value = 50
    parry_mod = 1.5 # no effect on block currently ?
    attacks = [
        actions.Block
    ]

class LeatherCap(bc.Equippable):
    name = 'Leather Cap'
    desc = 'A tough leather cap.'
    slot = 'Head'
    value = 25
    defense = 1

class LeatherTunic(bc.Equippable):
    name = 'Leather Tunic'
    desc = 'A modest tunic made from boiled leather.'
    slot = 'Chest'
    value = 25
    defense = 1