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
    
class mod_damage(Effect):
    '''Modifies all damage dealt by the return value -> (add, mult)'''
    def __call__(self, atk:bc.Attack) -> tuple[int, float]:
        return NotImplementedError

class mod_accuracy(Effect):
    '''Modifies accuracy by the return value -> (add, mult)'''
    def __call__(self, atk:bc.Attack) -> tuple[int, float]:
        return NotImplementedError

class Stregth(mod_damage):
    '''Strength increases damage dealt by 1, double as effective on heavy attacks'''
    name = 'Strength'
    desc = 'Deals bonus damage!'
    def __init__(self, strength:int = 1) -> None:
        self.value = strength
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
    def __init__(self, acc_buff:int = 1.5) -> None:
        self.value = acc_buff
    def __call__(self, atk: bc.Attack) -> tuple[int, float]:
        return 0, self.value

class BalanceHeal(on_tick):
    name = 'Balance Gain'
    desc = 'Regenerates balance every few turns'
    def __init__(self, rate:float = 1.0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.healed = 0.0
        self.rate = rate
    def __call__(self, parent:bc.Entity):
        self.healed += 1
        if self.healed >= 1.0:
            self.healed -= 1
            parent.src.balance += 1