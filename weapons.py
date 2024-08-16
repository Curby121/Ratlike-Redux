import baseclasses as bc
import actions

class Dagger(bc.Weapon):
    name = 'Dagger'
    desc = 'Stick em with the pointy end!'
    slot = 'Primary'
    value = 5
    dmg_base = 8
    attacks = [
        actions.Slash,
        actions.Stab
    ]
    dodge_class = actions.Jab

class Spear(bc.Weapon):
    name = 'Wooden Spear'
    desc = 'A long wooden sshaft with a sharp piece of iron lashed on top.'
    slot = 'Primary'
    dmg_base = 8
    twohanded = True
    value = 15
    attacks = [
        actions.Poke,
        actions.Stab
    ]
    dodge_class = actions.Stab

class WoodenShield(bc.Weapon):
    name = 'Wooden Shield'
    desc = 'A small round wooden shield.'
    slot = 'Secondary'
    value = 50
    attacks = [
        actions.Block
    ]
