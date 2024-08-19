'''Enemy intelligence'''
import baseclasses as bc
import actions
import random
random.seed()

class Basic(bc.Strategy):
    '''Very simple strategy that tries to not over exhaust'''
    parent:bc.Enemy
    def get_action(self, actin_ls = None) -> bc.Action:
        actns:list[bc.Action]
        if actin_ls is not None:
            actns,w = zip(*actin_ls)
        else:
            actns,w = zip(*self.parent.actions)
        wgts = []
        wgts.extend(w)

        available = False
        for i,a in enumerate(actns):
            if self.parent.off_balance(a.balance_max) or\
                self.parent.getset_distance() < a.min_dist:
                    wgts[i] = 0
            else:
                available = True

        if not available:
            return actions.Pause(source = self.parent)
        
        for i,a in enumerate(actns):
            # percentage of exhaust meter filled after using attack
            x = (a.exh_cost + self.parent.exhaust - self.parent.exh_rec) / self.parent.max_exh
            wgts[i] = int(wgts[i] * (1 - x**4))
            if wgts[i] < 1:
                wgts[i] = 1
        #print(f'          Enemy weights:{wgts}')
        return random.choices(actns, wgts)[0](source = self.parent)

class Troll(Basic):
    def __init__(self, parent: bc.Damageable) -> None:
        super().__init__(parent)
        self.attack_ready = False
    def get_action(self) -> bc.Action:
        if self.parent.exhaust >= self.parent.max_exh:
            self.attack_ready = False
            return actions.Pause
        elif self.attack_ready:
            self.attack_ready = False
            return actions.Smash
        actn = super().get_action()
        if actn is actions.TrollReady:
            self.attack_ready = True
        return actn
