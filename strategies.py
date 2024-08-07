'''Enemy intelligence'''
import baseclasses as bc
import actions
import random
random.seed()

class Basic(bc.Strategy):
    '''Very simple strategy that tries to not over exhaust'''
    parent:bc.Enemy
    def get_action(self) -> bc.Action:
        actns,w = zip(*self.parent.actions)
        wgts = []
        wgts.extend(w)
        if self.parent.exhaust >= self.parent.max_exh:
            return actions.Rest
        for i,a in enumerate(actns):
            # percentage of exhaust meter filled after using attack
            x = (a.exh_cost + self.parent.exhaust - self.parent.exh_rec) / self.parent.max_exh
            wgts[i] = int(wgts[i] * (1 - x**4))
            if wgts[i] < 1:
                wgts[i] = 1
        #print(f'          Enemy weights:{wgts}')
        return random.choices(actns, wgts)[0]
    
class Troll(Basic):
    def __init__(self, parent: bc.Damageable) -> None:
        super().__init__(parent)
        self.attack_ready = False
    def get_action(self) -> bc.Action:
        if self.attack_ready:
            self.attack_ready = False
            if self.parent.exhaust >= self.parent.max_exh:
                return actions.Rest
            return actions.Smash
        actn = super().get_action()
        if actn is actions.TrollReady:
            self.attack_ready = True
        return actn
        