import baseclasses as bc
import GUI
import random
random.seed()

class Pause(bc.Action):
    name = 'Pause'
    desc = 'Stall one action'
    timer = 1
    balance_max = -1

class Slash(bc.Attack):
    '''Default attack for bladed weapons
    good defensive, but needs to win parry fights to build advantage'''
    name = 'Slash'
    desc = '''The simplest of blade techniques, its stance allows the user to keep their guard up against incoming attacks.'''
    use_msg = 'slashes.'
    dmg_mod = 0.75
    stagger_mod = 0.5
    parry = 7
    acc = 3
    bal_use_cost = 4
    reach = 5

class Chop(bc.Attack):
    name = 'Chop'
    desc = '''A harder swing applies more force, but leaves its user more vulnerable'''
    use_msg = 'chops!'
    timer = 5
    bal_resolve_cost = 4
    dmg_mod = 1.0
    stagger_mod = 1.5
    parry = 2
    acc = 6

class Stab(bc.Attack):
    '''Default attack for daggers and knives
    Short range, good acc, low stagger'''
    name = 'Stab'
    desc = 'A hard stab'
    use_msg = 'stabs quickly.'
    timer = 3
    bal_use_cost = 2
    bal_resolve_cost = 1
    dmg_mod = 1
    parry = 1
    acc = 4
    stagger_mod = 0.5
    reach = 3
    styles = ['quick']

class DaggerStab(bc.Attack):
    '''Signature finisher for daggers.'''
    name = 'Sink Blade'
    desc = 'A lethal stab'
    use_msg = 'throws their dagger forwards'
    dmg_mod = 1.2
    parry = 0
    acc = 3
    stagger_mod = 0.1
    reach = 3
    exh_cost = 10

class Lunge(bc.Attack):
    '''Aggressive Thrust. Spear signature attack.'''
    name = 'Lunge'
    desc = 'Poke their eyes out, kid!'
    use_msg = 'lunged with their spear!'
    dmg_mod = 2.0
    stagger_mod = 1.5
    timer = 5
    bal_use_cost = 4
    bal_resolve_cost = 3
    acc = 8
    parry = 0
    stagger_mod = 1.2
    
class Smash(bc.Attack):
    '''High stagger'''
    name = 'Smash!'
    desc = 'A powerful overhead slam!'
    use_msg = 'smashed viciously!'
    timer = 6
    dmg_mod = 1.0
    stagger_mod = 2.0
    acc = 6
    parry = 0
    bal_use_cost = 2
    bal_resolve_cost = 4
    styles = ['heavy']

class Bite(bc.Attack):
    name = 'Bite'
    desc = 'Chomp!'
    use_msg = 'bites ferociously!'
    dmg_mod = 0.5
    parry = 1
    acc = 10
    stagger_mod = 0.3

class RatJump(bc.Attack):
    name = 'Leap'
    desc = 'Munch'
    use_msg = 'leapt forward'

class Dodge(bc.CounterAttack):
    '''Standard Dodge action. Checks for a reaction_class on it\'s source.'''
    name = 'Dodge'
    desc = 'Dodge incoming attacks'
    use_msg = 'dodged!'
    timer = 3
    bal_use_cost = 2
    def __init__(self, source: bc.Entity, **kwargs):
        super().__init__(source.get_reaction(), source, **kwargs)
        self.used:bool = False

    def attack_me(self, atk: bc.Attack):
        self.silent = True
        if self._dodge_succeeds(atk):
            GUI.log(f'  {atk.tgt.name} dodged the attack!')
            if not self.used and self.reaction_class is not None:
                self.on_reaction(atk)
        else:
            GUI.log(f'  {atk.tgt.name} failed to dodge!')
            parry:bc.Attack = self.src.get_parry_class()(source = self.src)
            return parry.attack_me(atk)

    # TODO: quick/heavy adj.
    def on_reaction(self, atk:bc.Attack):
        '''Called when a reaction occurs'''
        GUI.log(f'   and reacts!')
        self.used = True
        return self.react(target = atk.src)
    
    def _dodge_succeeds(self, atk: bc.Attack) -> bool:
        if 'heavy' in atk.styles:
            return True
        roll = random.choice(range(10))
        if roll < 2: # 20% chance to fail
            return False
        if roll >= 4: # 60%
            return True
        if 'quick' in atk.styles: # quick is harder to dodge
            return False
        return True

class Block(bc.Action):
    name = 'Block'
    desc = 'Shields Up!'
    timer = 3
    def __init__(self, source: bc.Entity, **kwargs):
        super().__init__(source, **kwargs)
        self.efficacy = 0 # one tick happens before any chance to resolve -> minimum of 1
    def attack_me(self, atk:bc.Attack):
        GUI.log(' The attack is blocked!')
        dmg_m = 0
        stgr_m = 1
        reflected_stagger = 0.4 * atk.get_stagger()
        if 'heavy' in atk.styles:
            dmg_m = 0.25
            reflected_stagger = 0.7 * atk.get_stagger()
        if 'quick' in atk.styles:
            reflected_stagger = 5
        self.src.damage_me(atk,
                       dmg_mod = dmg_m,
                       stagger_mod = stgr_m
                       )
        atk.src._take_damage(0, int(reflected_stagger))
        self.timer = 0
    def tick(self):
        super().tick()
        self.efficacy += 1

class TrollReady(bc.Action):
    name = 'Troll smash prep'
    desc = ''
    use_msg = 'raises his club over his head!'

class Talk(bc.Attack):
    '''high stagger'''
    name = 'Talk'
    desc = 'Say it, dont spray it'
    use_msg = 'HELLO WORLD!'
    dmg_mod = 1
    stagger_mod = 2.5
    reach = 7
    exh_cost = 0
    styles = ['quick']