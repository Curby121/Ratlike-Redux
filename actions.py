import baseclasses as bc
import GUI
import random
random.seed()

class Pause(bc.Action):
    name = 'Pause'
    desc = 'Pause and recover your balance'
    use_msg = 'recovers their balance.'
    balance_max = -1
    def resolve(self):
        self.src.exhaust -= self.src.exh_rec
        return super().resolve()

class Slash(bc.Attack):
    '''Default attack for bladed weapons
    Med range, low damage, med stagger'''
    name = 'Slash'
    desc = 'The simplest of blade techniques'
    use_msg = 'slashes.'
    dmg_mod = 0.8
    stagger_mod = 1.0
    parry = 5
    acc = 3
    reach = 5
    exh_cost = 10

class Stab(bc.Attack):
    '''Default attack for daggers and knives
    Short range, good acc, low stagger'''
    name = 'Stab'
    desc = 'A hard stab'
    use_msg = 'stabs quickly.'
    dmg_mod = 1.0
    parry = 3
    acc = 7
    stagger_mod = 0.5
    reach = 3
    exh_cost = 7
    styles = ['quick']

class DaggerStab(bc.Attack):
    '''Signature finisher for daggers.'''
    name = 'Sink Blade'
    desc = 'A lethal stab'
    use_msg = 'throws their dagger forwards'
    dmg_mod = 1.2
    parry = 1
    acc = 3
    stagger_mod = 0.1
    reach = 3
    exh_cost = 12

class Lunge(bc.Attack):
    '''High range high stagger spear attack'''
    name = 'Lunge'
    desc = 'Poke their eyes out, kid!'
    use_msg = 'lunged with their spear!'
    dmg_mod = 1.5
    parry = 2
    acc = 8
    stagger_mod = 1.2
    reach = 10
    exh_cost = 17
    move = -1
    min_dist = 4
    
class Smash(bc.Attack):
    '''Med range high stagger'''
    name = 'Smash!'
    desc = 'A powerful overhead slam!'
    use_msg = 'smashed viciously!'
    dmg_mod = 1
    parry = 2
    acc = 10
    stagger_mod = 1.5
    reach = 7
    exh_cost = 17
    styles = ['heavy']

class Bite(bc.Attack):
    name = 'Bite'
    desc = 'Chomp!'
    use_msg = 'bites ferociously!'
    dmg_mod = 0.5
    parry = 1
    acc = 10
    stagger_mod = 0.3
    reach = 3
    exh_cost = 3

class RatJump(bc.Attack):
    name = 'Leap'
    desc = 'Munch'
    use_msg = 'leapt forward'
    dmg_mod = 1.0
    parry = 5
    acc = 10
    stagger_mod = 2.0
    reach = 4
    move = -1
    exh_cost = 18

class Dodge(bc.CounterAttack):
    '''Standard Dodge action. Checks for a reaction_class on it\'s source.'''
    name = 'Dodge'
    desc = 'Dodge incoming attacks without changing distance'
    use_msg = 'steps to the side!'
    exh_cost = 15
    balance_max = 1
    def __init__(self, source: bc.Entity, **kwargs):
        super().__init__(source.get_reaction(), source, **kwargs)
        self.used:bool = False

    def attack_me(self, atk: bc.Attack):
        self.silent = True
        if not self._can_dodge():
            self.use_msg = 'was too tired to dodge!'
            return self.damage_me(atk)
        if self._dodge_succeeds(atk):
            GUI.log(f'  {atk.tgt.name} dodged the attack!')
            self.mod_distance()
            if not self.used and self.reaction_class is not None:
                self.on_reaction(atk)
        else:
            GUI.log(f'  {atk.tgt.name} failed to dodge!')
            return self.damage_me(atk)

    # TODO: quick/heavy adj.
    def on_reaction(self, atk:bc.Attack):
        '''Called when a reaction occurs'''
        GUI.log(f'   and reacts!')
        self.used = True
        return self.react(target = atk.src)
    
    def _can_dodge(self) -> bool:
        if self.src.exhaust >= self.src.max_exh:
            GUI.log(f' {self.src.name} is too exhausted to dodge!')
            return False
        else:
            return True
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

class Jump(Dodge):
    name = 'Jump Back'
    desc = 'leap away from your opponent'
    use_msg = 'jumps back!'
    exh_cost = 15
    pre_move = 2

class SideStep(Dodge):
    name = 'Side Step'
    desc = 'Dodge and try to close in'
    use_msg = 'steps to the side...'
    exh_cost = 12
    pre_move = -1
    min_dist = 4

class Block(bc.Action):
    name = 'Block'
    desc = 'Shields Up!'
    balance_max = 1
    def attack_me(self, atk:bc.Attack):
        GUI.log(' The attack is blocked!')
        dmg_m = 0
        stgr_m = 0.5
        mod_dist = True
        min_dist = 5
        reflected_stagger = 0.4 * atk.get_stagger()
        if 'heavy' in atk.styles:
            dmg_m *= 1.75
            stgr_m *= 1.8
            reflected_stagger = 0.7 * atk.get_stagger()
            mod_dist = True
            min_dist = atk.reach # push back to 
        if 'quick' in atk.styles:
            dmg_m *= 0.8
            reflected_stagger = 10
        self.damage_me(atk,
                       dmg_mod = dmg_m,
                       stagger_mod = stgr_m,
                       move_in_range = mod_dist,
                       dist_min = min_dist
                       )
        atk.src._take_damage(0, int(reflected_stagger))

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