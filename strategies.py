'''Enemy intellegences'''
import baseclasses as bc
import actions
import random
random.seed()

class Goblin(bc.Strategy):
    actions = [
        actions.Lunge,
        actions.Stab,
        actions.Dodge
    ]
    def get_action(self) -> bc.Action:
        if self.parent.exhaust >= self.parent.max_exh:
            return actions.Rest
        wgts = [75,5,20]
        for i,a in enumerate(self.actions):
            x = (a.exh_cost + self.parent.exhaust) / self.parent.max_exh
            if x > 0.5:
                wgts[i] -= int(x * 15)
            if wgts[i] < 1:
                wgts[i] = 1
        print(f'Gob:{wgts}')
        return super().get_action(wgts)

            