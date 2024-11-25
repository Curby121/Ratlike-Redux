'''Effects'''
import baseclasses as bc

class Effect(bc.Viewable):
    pass

class on_tick(Effect):
    '''Called when actions are decremented'''
    def __call__(self, parent:bc.Action):
        return NotImplementedError
    
class mod_damage(Effect):
    def __call__(self, atk:bc.Attack) -> tuple[int, float]:
        return NotImplementedError

class Stregth(mod_damage):
    name = 'Strength'
    desc = 'Deals bonus damage!'
    def __init__(self, strength:int = 1) -> None:
        self.value = strength
    def __call__(self, atk: bc.Attack) -> tuple[int, float]:
        return self.value, 1.0

class BalanceHeal(on_tick):
    name = 'Balance Gain'
    desc = 'Regenerates balance every few turns'
    def __init__(self, rate:float = 1.0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.healed = 0.0
        self.rate = rate
    def __call__(self, parent:bc.Action):
        self.healed += 1
        if self.healed >= 1.0:
            self.healed -= 1
            parent.src.balance += 1