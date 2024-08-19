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
        no_avail_actn = True
        for i,a in enumerate(actns):
            if not self.parent.can_use_action(a):
                wgts[i] = 0
            else:
                no_avail_actn = False
        if no_avail_actn:
            return actions.Pause(source = self.parent)
        
        # find which atks are in range
        not_in_range_indices = []
        for i,a in enumerate(actns):
            if not self.parent.in_range(a):
                not_in_range_indices.append(i)
        any_in_range = len(not_in_range_indices) > 0

        iamsafe = game.plr.off_balance()

        for i,a in enumerate(actns):
            # percentage of exhaust meter filled after using attack
            x = (a.exh_cost + self.parent.exhaust - self.parent.exh_rec) / self.parent.max_exh
            wgts[i] = int(wgts[i] * (1 - x**2))

            # hacky
            if iamsafe and isinstance(a, actions.Dodge):
                wgts[i] = 0

            # prevents backing up when no atks in range
            # add cowardice effect?
            if not any_in_range and a.pre_move > 0:
                wgts[i] = 0

            if any_in_range and i in not_in_range_indices:
                wgts[i] = int(wgts[i] * 0.25)

            # mainly prevents crashing. should be fine when numbers are big to start
            #if wgts[i] < 1:
            #    wgts[i] = 1
        if sum(wgts) <= 0:
            print(f'{self.parent.name} has no actions avail: wgts: {wgts}')
            return actions.Pause(source = self.parent)
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
