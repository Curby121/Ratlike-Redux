import baseclasses as bc
import GUI
import random
random.seed()

class Pause(bc.Action):
    name = 'Steady'
    desc = 'Stall for a moment to regain some balance.'
    timer = 2
    balance_max = -1
    bal_use_cost = -1
    parry_mod = 2.0

class Stagger(bc.Action):
    name = 'Teetering'
    desc = 'This unit is recovering after being knocked off balance!'
    timer = 4
    bal_use_cost = -1
    def tick(self):
        print('stand tick')
        self.src.balance += 1
        return super().tick()

class Slash(bc.Attack):
    '''Default attack for bladed weapons
    good defensive, but needs to win parry fights to build advantage'''
    name = 'Slash'
    desc = '''The simplest of blade techniques, its stance allows the user to keep their guard up against incoming attacks.'''
    use_msg = 'slashes.'
    dmg_mod = 0.75
    stagger_mod = 0.5
    acc = 8
    parry_mod = 1.5
    bal_use_cost = 1
    bal_resolve_cost = -1

class Chop(bc.Attack):
    name = 'Chop'
    desc = '''A targeted swing will hurt, but leaves its user ssomewhat vulnerable'''
    use_msg = 'chops!'
    timer = 5
    dmg_mod = 1.0
    stagger_mod = 1.0
    acc = 10
    parry_mod = 0.5
    bal_use_cost = 1

class Stab(bc.Attack):
    '''Default attack for daggers and knives
    Short range, good acc, low stagger'''
    name = 'Stab'
    desc = 'A hard stab'
    use_msg = 'stabs quickly.'
    timer = 3
    bal_use_cost = 2
    bal_resolve_cost = -2
    dmg_mod = 1
    parry_mod = 0.5
    acc = 10
    stagger_mod = 0.5
    reach = 3
    styles = ['quick']

class Lunge(bc.Attack):
    '''Aggressive Thrust. Spear signature attack.'''
    name = 'Lunge'
    desc = 'Poke their eyes out, kid!'
    use_msg = 'lunged with their spear!'
    dmg_mod = 2.0
    stagger_mod = 1.5
    timer = 6
    bal_use_cost = 1
    bal_resolve_cost = 2
    acc = 22
    parry_mod = 0.5
    stagger_mod = 1.5
    
class Smash(bc.Attack):
    '''High stagger'''
    name = 'Smash!'
    desc = 'A powerful overhead slam!'
    use_msg = 'smashed viciously!'
    timer = 7
    dmg_mod = 1.0
    stagger_mod = 2.0
    acc = 24
    parry_mod = 0.25
    bal_use_cost = 5
    bal_resolve_cost = -2
    styles = ['heavy']

class DaggerStab(bc.Attack):
    '''Signature finisher for daggers.'''
    name = 'Sink Blade'
    desc = 'A lethal stab'
    use_msg = 'throws their dagger forwards!'
    timer = 4
    acc = 6
    dmg_mod = 2.0
    parry_mod = 0
    stagger_mod = 0
    bal_use_cost = 3
    bal_resolve_cost = -1

class Bite(bc.Attack):
    name = 'Bite'
    desc = 'Chomp!'
    use_msg = 'bites ferociously!'
    timer = 3
    dmg_mod = 0.5
    parry_mod = 1
    acc = 12
    stagger_mod = 0.5

class TrollKick(bc.Attack):
    name = 'Kick'
    desc = 'Whack!'
    use_msg = 'kicks!'
    timer = 3
    dmg_mod = 0.3
    parry_mod = 0
    acc = 20
    stagger_mod = 1.0
    bal_use_cost = 2

class Dodge(bc.Channel):
    '''Standard Dodge action. Checks for a reaction_class on it\'s source.'''
    name = 'Dodge'
    desc = 'Attempt to dodge. A dodge action takes 2 actions to prepare, and then dodges for the remainder.'
    use_msg = 'dodged!'
    timer = 4
    bal_use_cost = 3
    bal_resolve_cost = -1
    def __init__(self, source: bc.Entity, **kwargs):
        super().__init__(source, **kwargs)
        self.used:bool = False

    def attack_me(self, atk: bc.Attack):
        self.silent = True
        if self._dodge_succeeds(atk):
            GUI.log(f'  {atk.tgt.name} dodged the attack!')
        else:
            GUI.log(f'  {atk.tgt.name} failed to dodge!')
            return self.src.damage_me(atk)

    # TODO: quick/heavy adj.
    def on_reaction(self, atk:bc.Attack):
        '''Called when a reaction occurs'''
        GUI.log(f'   and reacts!')
        self.used = True
        return self.react(target = atk.src)
    
    def _dodge_succeeds(self, atk: bc.Attack) -> bool:
        if self.efficacy <= 2:
            return False
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

class Block(bc.Channel):
    name = 'Block'
    desc = 'Block the next attack. Block is more effective the longer it is held, up to 3'
    timer = 3
    bal_use_cost = -1
    reflect_mod = 0.5
    def __init__(self, source: bc.Entity, **kwargs):
        super().__init__(source, **kwargs)
    def attack_me(self, atk:bc.Attack):
        self.timer = 0
        if self.deflect_check(atk):
            dmg_m, stgr_m = 0, 0
            GUI.log(' The attack is deflected!')
        elif self.efficacy == 1:
            dmg_m, stgr_m = 0.25, 1
            GUI.log(' Some of the attack is blocked!')
        elif self.efficacy == 2:
            dmg_m, stgr_m = 0, 0.67
            GUI.log(' The attack is blocked!')
        else:
            dmg_m, stgr_m = 0, 0.5
            GUI.log(' The attack is blocked!')

        reflected_stagger = self.src.stagger_base * self.reflect_mod

        if 'heavy' in atk.styles:
            dmg_m *= 2.0
            reflected_stagger = 0
        if 'quick' in atk.styles:
            stgr_m = 0
        
        if self.efficacy == 1: # no reflection on 1 turn block
            reflected_stagger = 0
            
        if dmg_m > 0 or stgr_m > 0:
            self.src.damage_me(atk, dmg_m, stgr_m)
        reflected_stagger = int(reflected_stagger)
        if reflected_stagger > 0:
            atk.src._take_damage(0, reflected_stagger)

class TrollReady(bc.Action):
    name = 'Raise Club'
    desc = 'What goes up...'
    use_msg = 'raises his club over his head!'