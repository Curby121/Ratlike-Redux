import baseclasses as bc

class Rest(bc.Action):
    name = 'Rest'
    desc = 'Pause and recover your balance'
    use_msg = 'recovers their balance.'

class Stab(bc.Attack):
    name = 'Stab'
    desc = 'A hard stab'
    use_msg = 'stabs quickly!'
    dmg = 8
    reach = 3
    exh_cost = 12
    stagger = 17
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
    def DodgeSucceeds(self, atk: bc.Attack) -> bool:
        # TODO: chance to fail
        return True
    def attack(self, atk: bc.Attack):
        self.src.exhaust += self.exh_cost_each
        if self.DodgeSucceeds(atk):
            return super().attack(atk, dmg_mod=0)
        else:
            return super().attack(atk)