import baseclasses as bc
import actions

class Dagger(bc.Weapon):
    name = 'Dagger'
    desc = 'Stick em with the pointy end!'
    slot = 'Primary'
    value = 5
    dmg_base = 10
    parry_mod = 0.2
    attacks = [
        actions.Stab,
        actions.DaggerStab
    ]
    parry_class = actions.Stab
    dodge_class = actions.Stab

class Sword(bc.Weapon):
    name = 'Iron Sword'
    desc = 'Swordsman\'s best friend.'
    slot = 'Primary'
    value = 15
    dmg_base = 8
    attacks = [
        actions.Slash,
        actions.Chop
    ]
    parry_class = actions.Slash

class Spear(bc.Weapon):
    name = 'Wooden Spear'
    desc = 'A long wooden sshaft with a sharp piece of iron lashed on top.'
    slot = 'Primary'
    dmg_base = 5
    twohanded = True
    value = 15
    parry_mod = 0.5
    attacks = [
        actions.Lunge,
        actions.Stab
    ]
    parry_class = actions.Stab

class WoodenShield(bc.Weapon):
    name = 'Wooden Shield'
    desc = 'A small round wooden shield.'
    slot = 'Secondary'
    value = 50
    parry_mod = 1.5
    attacks = [
        actions.Block
    ]
