'''Enemy intelligence'''
import baseclasses as bc
import actions
import random
import game
random.seed()

class Basic(bc.Strategy):
    parent:bc.Enemy
    def get_action(self, actin_ls = None) -> bc.Action:
        actns:list[bc.Action]
        if actin_ls is not None:
            actns,w = zip(*actin_ls)
        else:
            actns,w = zip(*self.parent.actions)
        wgts = []
        wgts.extend(w)

        for i,a in enumerate(actns):
            if not self.parent.can_use_action(a):
                wgts[i] = 0
        
        for i,a in enumerate(actns):
            # percentage of exhaust meter filled after using attack
            x = (self.parent.balance\
                 - a.bal_use_cost - a.bal_resolve_cost\
                    + self.parent.bal_rec) / self.parent.bal_max
            wgts[i] = int(wgts[i] * (x**2))
        if sum(wgts) <= 0:
            print(f'{self.parent.name} has no actions avail: wgts: {wgts}')
            return actions.Pause(source = self.parent)
        return random.choices(actns, wgts)[0](source = self.parent)

class Troll(Basic):
    def __init__(self, parent: bc.Damageable) -> None:
        super().__init__(parent)
        self.attack_ready = False
    def get_action(self) -> bc.Action:
        if self.parent.balance >= self.parent.bal_max:
            self.attack_ready = False
            return actions.Pause
        elif self.attack_ready:
            self.attack_ready = False
            return actions.Smash
        actn = super().get_action()
        if actn is actions.TrollReady:
            self.attack_ready = True
        return actn
