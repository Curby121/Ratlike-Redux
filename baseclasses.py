'''Contains definitions of base classes and their behaviour.\n
None of these should be created by themselves, they should be derived from'''

import random
random.seed()

class Viewable:
    '''Base class for all game objects that the player can know about\n
    All Viewables must have a name and description.\n
    Viewables inclues all enemies, items, and actions'''
    damageable = False
    name:str = None
    desc:str = None
    def __init__(self, **kwargs) -> None:
        for key, val in kwargs.items():
            setattr(self, key, val)
    def examine(self):
        print(f"{self.name}. {self.desc}")

# might not be useful. All entities so far are damageables
# TODO:? Merge with damageable, have 'damageable' just as a bool
class Entity(Viewable):
    '''Base class for objects that can be placed in a scene\n
    Entity's can have an action and are targetable by actions'''
    max_hp:int
    hp:int
    exhaust:int
    max_exh:int
    exh_rec:int
    def __init__(self, **kwargs) -> None:
        self.action:Action = None
        super().__init__(**kwargs)
    def get_reaction(self):
        return None
    def take_turn(self):
        raise Exception(f'No turn defined for {self.name}')
    def take_turn(self, action_class, **kwargs):
        self.action = action_class(
            source = self,
            **kwargs
        )
        return self.action

class Damageable(Entity):
    '''Base Class for all entities capable of taking damage\n
    ALL damageables must be initialized with a max_hp stat'''
    damageable = True
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not hasattr(self, 'max_hp'):
            raise Exception(f'Damageable must be initialized with max_hp stat')
        self.hp:int = self.max_hp
        self.exhaust = 0
    def _take_damage(self, dmg:int, stgr:int):
        self.hp -= dmg
        self.exhaust += stgr
        print(f'  {self.name} took {dmg} damage and {stgr} stagger!')
    def new_turn(self):
        '''Reset bookkeeping for next turn'''
        self.exhaust = max(0, self.exhaust - self.exh_rec)

class Enemy(Damageable):
    '''Base Class for enemies that the player will fight.\n
    These will show up in the enemy section of GUI,
    and will be given chances to attack\n
    Enemy's must have a list of attack classes, these are
    a list of tuples of attack classes and weights. e.g:\n
    [(actions.Stab, 2),\n
        (actions.Dodge, 1)]'''
    atks:list
    def take_turn(self, player):
        classes, weights = zip(*self.atks)
        atk = random.choices(classes, weights = weights)[0]
        return super().take_turn(target = player, action_class = atk)

class Item(Entity):
    '''Base Class for entities that can be placed in players inventory\n
    Items should have a value'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'value'):
            print(f'{self.name} has no value')

# an instance of this class is placed on the table when an action is selected
class Action(Viewable):
    src:Damageable
    exh_cost:int
    use_msg:str = None
    def __init__(self, source:Entity, **kwargs):
        self.eff: float = 1.0
        self.silent:bool = False
        super().__init__(**kwargs)
        self.src = source
    def resolve(self, silent:bool = False):
        '''Perform this action'''
        self.src.exhaust += self.exh_cost

        if self.use_msg is not None and not self.silent:
            print(f'  {self.src.name} {self.use_msg}')
    def attack(self, atk):
        '''Attack the source of this action. This function can be overridden
        on actions that interrupt incoming attacks'''
        dmg = int(atk.dmg * atk.eff)
        stagger = int(atk.stagger * atk.eff)
        self.src._take_damage(dmg, stagger)
        self.eff *= 1 -(stagger / self.src.max_exh)

# TODO: Damage calculation based on weapon / skills etc
class Attack(Action):
    reach: int
    tgt:Entity
    stagger:int
    def __init__(self, source:Entity, target:Damageable = None, **kwargs):
        self.tgt = target
        super().__init__(source = source, **kwargs)
    def resolve(self):
        super().resolve()
        self.tgt.action.attack(atk = self)
    
class CounterAttack(Attack):
    '''Base class that stores an attack that is performed against the
    first enemy that acted upon it. When a CounterAttack is resolved,
    it\'s stored attack is used'''
    def __init__(self, reaction:Attack, source: Entity, **kwargs):
        self.reaction_class = reaction
        if 'target' in kwargs:
            kwargs['target'] = None
        super().__init__(source, **kwargs)

    def resolve(self):
        if self.tgt is not None and self.reaction_class is not None:
            return self.reaction_class(
                target = self.tgt,
                source = self.src).resolve()
    def attack(self, atk:Attack, dmg_mod:float = 1.0):
        if self.tgt == None:
            self.tgt = atk.src
        if dmg_mod != 0:
            atk.eff *= dmg_mod
            return super().attack(atk)

class Weapon(Item):
    '''Base class for all weapons.\n
    Weapons must have a style. Paradigm is melee by default'''
    def __init__(self, **kwargs):
        self.paradigm = 'melee'
        self.dodge_class:CounterAttack = None
        super().__init__(**kwargs)
        if not hasattr(self, 'style'):
            raise Exception('weapon created with no style attribute')
    def get_actions(self) -> list[Attack]:
        # TODO: player talents / abilities
        return self.attacks

