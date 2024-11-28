'''Enemy intelligence'''
import baseclasses as bc
import actions
import random
import player
random.seed()

class Basic(bc.Strategy):
    parent:bc.Enemy
    def get_action(self, target:bc.Entity) -> bc.Action:
        if self._should_dodge(target):
            return actions.Dodge(source = self.parent, target = target)
        actns:list[bc.Action]
        actns,w = zip(*self.parent.actions)
        wgts = []
        wgts.extend(w)

        for i,a in enumerate(actns):
            if not self.parent.can_use_action(a):
                wgts[i] = 0

        for i,a in enumerate(actns):
            # percentage of exhaust meter filled after using attack
            x = (self.parent.balance\
                 - a.bal_use_cost - a.bal_resolve_cost)\
                     / self.parent.bal_max
            wgts[i] = int(wgts[i] * (x**2))
        if sum(wgts) <= 0:
            print(f'{self.parent.name} has no actions avail: wgts: {wgts}')
            return actions.Pause(source = self.parent)
        return random.choices(actns, wgts)[0](source = self.parent, target = target)

class Troll(Basic):
    def get_action(self, target:bc.Entity) -> bc.Action:
        print('trollstrat 1')
        if self.parent.balance <= 0:
            self.parent.attack_ready = False
            return actions.Pause(self.parent)
        elif self.parent.attack_ready:
            print('troll strat')
            self.parent.attack_ready = False
            return actions.Smash(self.parent)
        actn = super().get_action()
        if isinstance(actn, actions.TrollReady):
            print('3')
            self.parent.attack_ready = True
        return actn
