'''Effects'''
from typing import Any
import baseclasses as bc

# TODO: proper effect examine
class Effect(bc.Viewable):
    def __call__(self, *args, **kwargs) -> Any:
        return NotImplementedError

class on_tick(Effect):
    '''Called when actions are decremented'''
    def __call__(self, parent:bc.Entity):
        return NotImplementedError
    
class mod_value(Effect):
    '''Base class for a specific numbers adjustment; see implementations'''
    add:int
    mult:float
    def __init__(self, add:int = 0, mult:float = 1.0) -> None:
        self.add = add
        self.mult = mult
    def __call__(self, atk: bc.Attack) -> tuple[int, float]:
        return self.add, self.mult
    def __add__(self, val):
        self.add += val.add
        self.mult += self.mult -1
        return self
    def examine(self) -> str:
        return super().examine() + f'\n  +{self.add} x{self.mult}'

class mod_damage(mod_value):
    '''Called when damage calculation is performed during attack resolution'''

class mod_accuracy(mod_value):
    '''Called when accuracy max roll calculation during attack resolution'''

class Stregth(mod_damage):
    '''Strength increases damage dealt by 1, double as effective on heavy attacks'''
    name = 'Strength'
    desc = 'Deals bonus damage!'
    def __call__(self, atk: bc.Attack) -> tuple[int, float]:
        if 'heavy' in atk.styles:
            print('strength x2')
            return self.value *2, 1.0
        elif 'quick' in atk.styles:
            print('no str bonus on quick attacks')
            return 0, 1.0
        return self.value, 1.0

class Accuracy(mod_accuracy):
    '''Increases accuracy by flat number'''
    name = 'Accuracy'
    desc = 'Attacks find their mark more often'

class BalanceHeal(on_tick):
    name = 'Balance Gain'
    desc = 'Regenerates balance every $ turns'
    def __init__(self, rate:float = 1.0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.healed = 0.0
        self.rate = rate
        x = self.desc.index('$')
        self.desc = self.desc[:x] + str(int(1/rate)) + self.desc[x+1:]
    def __call__(self, parent:bc.Entity):
        self.healed += self.rate
        if self.healed >= 1.0:
            self.healed -= 1
            parent.src.balance += 1