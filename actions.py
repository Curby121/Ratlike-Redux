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
    name = 'Stab'
    desc = 'A hard stab'
    use_msg = 'stabs quickly!'
    dmg = 8
    reach = 3
    exh_cost = 12
    stagger = 15
    styles = ['quick']

class Jab(bc.Attack):
    name = 'Jab'
    desc = 'A quick jab'
    use_msg = 'used Jab'
    dmg = 4
    reach = 1
    exh_cost = 6
    stagger = 6
    styles = ['quick']

class Bite(bc.Attack):
    name = 'rat attack',
    desc = 'burr',
    use_msg = 'bites viciously!'
    dmg = 6,
    reach = 3
    exh_cost = 3

class Dodge(bc.CounterAttack):
    '''Standard Dodge action. Checks for a reaction_class on it\'s source.'''
    name = 'Dodge'
    desc = 'Dodge incoming attacks this turn'
    reach = 0
    exh_cost_each = 16 # each dodge adds more stagger
    def __init__(self, source: bc.Entity, **kwargs):
        super().__init__(source.get_reaction(), source, **kwargs)
        self.used:bool = False

    def can_dodge(self) -> bool:
        if self.src.exhaust >= self.src.max_exh:
            print(f' {self.src.name} is too exhausted to dodge!')
            return False
        else:
            return True

    def dodge_succeeds(self, atk: bc.Attack) -> bool:
        # TODO: implement skills
        if random.choice(range(4)) == 0: # 20% flat fail rate
            return False
        return True
    
    def attack(self, atk: bc.Attack):
        if not self.can_dodge():
            print (f' {self.src.name} is too tired to dodge!')
            return super().attack(atk)
        self.src.exhaust += self.exh_cost_each
        if self.dodge_succeeds(atk):
            print(f'   {atk.tgt.name} dodged the attack!')
            if not self.used and self.reaction_class is not None:
                print(f'     and reacts!')
                self.react(target = atk.src)
                self.used = True
        else:
            return super().attack(atk)