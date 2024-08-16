import baseclasses as bc
import GUI
import random
random.seed()

class Rest(bc.Action):
    name = 'Rest'
    desc = 'Pause and recover your balance'
    use_msg = 'recovers their balance.'
    def resolve(self):
        self.src.exhaust -= self.src.exh_rec
        return super().resolve() # exhaust is taken off once in here too

class Stab(bc.Attack):
    '''Default attack for daggers and knives'''
    name = 'Stab'
    desc = 'A hard stab'
    use_msg = 'stabs quickly!'
    dmg_mod = 0.8
    stagger_mod = 0.8
    reach = 4
    exh_cost = 12
    styles = ['quick']

class Jab(bc.Attack):
    '''Default reaction for daggers. Goblin standard attack'''
    name = 'Jab'
    desc = 'A quick jab'
    use_msg = 'jabs at their opponent!'
    dmg_mod = 0.6
    stagger_mod = 0.5
    reach = 3
    exh_cost = 6
    styles = ['quick']

class Lunge(bc.Attack):
    '''High range high stagger spear attack'''
    name = 'Lunge'
    desc = 'An aggressive lunge!'
    use_msg = 'lunged forwards!'
    dmg_mod = 1.5
    stagger_mod = 1.2
    reach = 10
    exh_cost = 17
    
class Smash(bc.Attack):
    '''Med range high stagger'''
    name = 'Smash!'
    desc = 'A powerful overhead slam!'
    use_msg = 'smashed viciously!'
    dmg_mod = 1
    stagger_mod = 1.5
    reach = 7
    exh_cost = 17
    styles = ['heavy']

class Bite(bc.Attack):
    name = 'Bite'
    desc = 'Chomp!'
    use_msg = 'bites viciously!'
    dmg_mod = 0.3
    stagger_mod = 0.3
    reach = 3
    exh_cost = 3

class Dodge(bc.CounterAttack):
    '''Standard Dodge action. Checks for a reaction_class on it\'s source.'''
    name = 'Dodge'
    desc = 'Dodge incoming attacks this turn'
    use_msg = 'jumps back!'
    reach = 0
    exh_cost = 25 # each dodge adds more stagger
    def __init__(self, source: bc.Entity, **kwargs):
        super().__init__(source.get_reaction(), source, **kwargs)
        self.used:bool = False

    def attack(self, atk: bc.Attack):
        self.silent = True
        if not self._can_dodge():
            self.use_msg = 'was too tired to dodge!'
            return super().attack(atk)
        if self._dodge_succeeds(atk):
            GUI.log(f'  {atk.tgt.name} dodged the attack!')
            if not self.used and self.reaction_class is not None:
                GUI.log(f'   and reacts!')
                self.on_dodge(atk)
        else:
            return super().attack(atk)

    def on_dodge(self, atk:bc.Attack):
        react:bool = True
        atk.mod_distance(atk, dist_min = atk.reach + 1)
        if 'quick' in atk.styles:
            react = False
        elif 'heavy' in atk.styles:
            atk.mod_distance(atk,
                             self.reaction_class.reach,
                             self.reaction_class.reach)
        if react:
            if self.reaction_class.reach >= atk.get_distance():
                self.used = True
                self.react(target = atk.src)
            else:
                GUI.log(f'Enemy was out of your reaction\'s reach!')

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
        if 'quick' in atk.styles and roll < 4: # quick is harder to dodge
            return False
        else:
            return True
     
class Block(bc.Action):
    name = 'Block'
    desc = 'Shields Up!'
    def attack(self, atk:bc.Attack):
        GUI.log(' The attack is blocked!')
        dmg_m = 0.5
        stgr_m = 0.5
        mod_dist = True
        min_dist = 5
        reflected_stagger = 0.4 * atk.stagger()
        if 'heavy' in atk.styles:
            dmg_m *= 1.5
            stgr_m *= 1.8
            reflected_stagger = 0.7 * atk.stagger()
            mod_dist = True
            min_dist = atk.reach # push back to 
        if 'quick' in atk.styles:
            dmg_m *= 0.8
            reflected_stagger = 10
        super().attack(atk,
                       dmg_mod = dmg_m,
                       stagger_mod = stgr_m,
                       mod_dist = mod_dist,
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