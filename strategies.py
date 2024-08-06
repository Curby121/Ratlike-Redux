'''Enemy intellegences'''
import baseclasses as bc
import actions
import random
random.seed()

class Goblin(bc.Strategy):
    actions = [
        actions.Lunge,
        actions.Jab,
        actions.Dodge
    ]
    def get_action(self) -> bc.Action:
        if self.parent.exhaust >= self.parent.max_exh:
            return actions.Rest
        wgts = [60,40,50]
        for i,a in enumerate(self.actions):
            # percentage of exhaust meter filled after using attack
            x = (a.exh_cost + self.parent.exhaust - self.parent.exh_rec) / self.parent.max_exh
            if x > 0.5:
                wgts[i] = int(wgts[i] * (1.2 - x**2))
            if wgts[i] < 1:
                wgts[i] = 1
        print(f'Gob:{wgts}')
        return super().get_action(wgts)
