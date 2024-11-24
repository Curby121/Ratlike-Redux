'''Effects'''
from typing import Any
import baseclasses as bc

class Effect(bc.Viewable):
    pass

class on_tick(Effect):
    '''Called when actions are decremented'''
    id = 'on_tick'
    def __call__(self, parent:bc.Entity):
        return NotImplementedError
    
class BalanceHeal(on_tick):
    name = 'Balance Gain'
    desc = 'Regenerates balance every few turns'
    rate:float = 0.5
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.healed = 0.0
    def __call__(self, parent:bc.Entity):
        self.healed += 1
        if self.healed >= 1.0:
            self.healed -= 1
            parent.balance += 1