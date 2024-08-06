import baseclasses as bc
import random
random.seed()

class Rest(bc.Action):
    name = 'Rest'
    desc = 'Pause and recover your balance'
    use_msg = 'recovers their balance.'
    def resolve(self):
        # 3x recovery for this turn
        self.src.exhaust -= self.src.exh_rec *2
        return super().resolve()

class Stab(bc.Attack):
    '''Default attack for daggers and knives'''
    name = 'Stab'
    desc = 'A hard stab'
    use_msg = 'stabs quickly!'
    dmg_mod = 1
    stagger_mod = 1
    reach = 3
    exh_cost = 12
    styles = ['quick']

class Jab(bc.Attack):
    '''Default reaction for daggers. Goblin standard attack'''
    name = 'Jab'
    desc = 'A quick jab'
    use_msg = 'jabs at their opponent!'
    dmg_mod = 0.6
    stagger_mod = 0.5
    reach = 1
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
    exh_cost = 21
    
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
    name = 'Bite',
    desc = 'Chomp!',
    use_msg = 'bites viciously!'
    dmg = 6,
    reach = 3
    exh_cost = 3

class Dodge(bc.CounterAttack):
    '''Standard Dodge action. Checks for a reaction_class on it\'s source.'''
    name = 'Dodge'
    desc = 'Dodge incoming attacks this turn'
    reach = 0
    exh_cost = 25 # each dodge adds more stagger
    def __init__(self, source: bc.Entity, **kwargs):
        super().__init__(source.get_reaction(), source, **kwargs)
        self.used:bool = False

    def attack(self, atk: bc.Attack):
        if not self._can_dodge():
            print (f' {self.src.name} is too tired to dodge!')
            return super().attack(atk)
        if self._dodge_succeeds(atk):
            print(f'   {atk.tgt.name} dodged the attack!')
            if not self.used and self.reaction_class is not None:
                print(f'     and reacts!')
                self.react(target = atk.src)
                self.used = True
        else:
            return super().attack(atk)

    def _can_dodge(self) -> bool:
        if self.src.exhaust >= self.src.max_exh:
            print(f' {self.src.name} is too exhausted to dodge!')
            return False
        else:
            return True
    def _dodge_succeeds(self, atk: bc.Attack) -> bool:
        # TODO: implement skills
        if random.choice(range(4)) == 0: # 20% flat fail rate
            return False
        return True
        
class Block(bc.Action):
    name = 'Block'
    desc = 'Shields Up!'
    def attack(self, atk:bc.Attack):
        print(' The attack is blocked!')
        # TODO: dont call _take_damage here, probably create a block reflect
        super().attack(atk, dmg_mod=0.4, stagger_mod=0.6)
        atk.src._take_damage(0, int(atk.stagger() * 0.3))

