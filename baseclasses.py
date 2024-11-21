'''Contains definitions of base classes and their behaviour.\n
None of these should be created by themselves, they should be derived from'''

import random
random.seed()
import GUI

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
        GUI.log(f"{self.name}. {self.desc}")

# might not be useful. All entities so far are damageables
# TODO:? Merge with damageable, have 'damageable' just as a bool
class Entity(Viewable):
    '''Base class for objects that can be placed in a scene\n
    Entity's have an action list and are targetable by actions'''
    max_hp:int
    hp:int
    balance:int
    bal_max:int
    bal_rec:int
    move:int
    def __init__(self, **kwargs) -> None:
        self.action_queue:list[Action] = []
        super().__init__(**kwargs)
        self.balance = self.bal_max
    def getset_distance(self, set = None) -> int:
        return NotImplementedError
    
    # doesnt do what it says, returns if balance > 0
    def off_balance(self, cost:int = 0) -> bool:
        '''Returns true if entity cannot spent cost in balance'''
        return self.balance < cost
    def get_reaction(self):
        return None
    def get_parry_class(self):
        return NotImplementedError
    def can_use_action(self, actn_class) -> True:
        '''Returns True if entity can currently use that action'''
        if self.off_balance(actn_class.bal_use_cost):
            return False
        return True
    def take_turn(self):
        raise Exception(f'No turn defined for {self.name}')
    def get_atk_source(self, atk) -> float:
        '''On the player this returns the weapon, on enemies it returns the enemy'''
        raise NotImplementedError

#TODO: deprecate and remove
class Damageable(Entity):
    '''Base Class for all entities capable of taking damage\n
    ALL damageables must be initialized with a max_hp stat'''
    damageable = True
    dmg_base:int
    stagger_base:int
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not hasattr(self, 'max_hp'):
            raise Exception(f'Damageable must be initialized with max_hp stat')
        self.hp:int = self.max_hp

    def attack_me(self, atk):
        if len(self.action_queue) == 0:
            self.damage_me(self, atk)
        else:
            self.action_queue[0].attack_me(atk = atk)

    def damage_me(self, atk,
                  dmg_mod:float = 1.0,
                  stagger_mod:float = 1.0
                  ):
        '''Attack this Damageable'''
        if not isinstance(atk, Attack):
            raise ValueError
        dmg = int(atk.get_dmg() * dmg_mod)
        stagger = int(atk.get_stagger() * stagger_mod)
        #print(f'attack_me stgr: {stagger} = {atk.get_stagger()} * {stagger_mod}')
        self._take_damage(dmg, stagger)
        
    def _take_damage(self, dmg:int, stgr:int):
        self.hp -= dmg
        self.balance -= stgr
        if dmg == 0:
            GUI.log(f'  {self.name} lost {stgr} balance!')
        else:
            GUI.log(f'  {self.name} took {dmg} dmg, {stgr} stgr!')

    def new_turn(self):
        '''Reset bookkeeping for next turn, also kills actions if at 0 balance'''
        self.balance = min(self.bal_max, self.balance + self.bal_rec)
        self.balance = max(0, self.balance)
        if self.balance == 0:
            self.action_queue.clear()

# an instance of this class is placed on the table when an action is selected
class Action(Viewable):
    '''Combat specific actions. All actions have a source and can be targetted
    by Attacks'''
    bal_use_cost:int = 0
    bal_resolve_cost:int = 0
    use_msg:str = None
    timer:int = 4
    balance_max:int = 0.5 # off balance is: exh > max_exh * balance_max
    def __init__(self, source:Entity, **kwargs):
        super().__init__(**kwargs)
        self.eff: float = 1.0
        self.silent:bool = False
        self.src:Damageable = source
        self.src.balance -= self.bal_use_cost
    def resolve(self) -> bool: # false it needs to cancel
        '''Perform this action'''
        if self.use_msg is not None and not self.silent:
            GUI.log(f'{self.src.name} {self.use_msg}')
        return True
    def attack_me(self, atk):
        self.src.damage_me(atk)
    def tick(self):
        self.timer -= 1
    def resolve_balance(self) -> None:
        '''Consumes the balance for resolving'''
        self.src.balance -= self.bal_resolve_cost

# TODO: Damage calculation based on weapon / skills etc
# TODO: tie weapon to attack (as source)      i think this got done?
class Attack(Action):
    '''Attacks are an Action that have a target.\n
    All attacks have a damage, stagger, and reach'''
    tgt:Damageable
    reach:int
    acc:int
    parry:int
    stagger_mod:float
    dmg_mod:float
    styles:list[str] = []

    def __init__(self, source: Entity, **kwargs):
        self.parry = int(source.get_atk_source(self).parry_mod * self.parry)
        self.parry = max(1, self.parry)
        super().__init__(source, **kwargs)

    # TODO: cleanup
    def resolve(self, reaction:bool = False) -> bool:
        resolves = True
        if not super().resolve():
            return False
        if not resolves:
            return False
        self.tgt.attack_me(atk = self)
        return True

    # parry checks
    def attack_me(self, atk:Action):
        def_mod = self.src.balance / self.src.bal_max
        off_mod = (atk.src.balance / atk.src.bal_max) / 2
        def_max = int(self.parry * def_mod)
        off_max = int(atk.acc * (0.5 + off_mod))
        if off_max <= 0:
            print(f'offmax: {off_max} |{atk}')
        def_roll = random.randint(1, def_max + 1)
        off_roll = random.randint(1, off_max + 1)
        print(f'PARRY CHECK: off/def: {off_roll} / {def_roll} || {off_max+1} / {def_max+1}   mods:{off_mod} / {def_mod}')
        if def_roll >= off_roll:
            GUI.log(' The attack is parried!')
            return
            return self.src.damage_me(
                atk,
                dmg_mod = 0,
                stagger_mod = 0.5
                )
        return self.src.damage_me(atk)

    def in_range(self, bonus:int = 0):
        if self.reach + bonus >= self.src.getset_distance():
            return True
        else:
            return False

    def get_dmg(self) -> int:
        self.src: Enemy
        return self.src.get_atk_source(self).dmg_base * self.dmg_mod * self.eff
    # stagger not effected by eff ?
    def get_stagger(self) -> int:
        #print(f'attack stgr: {self.src.stagger_base} * {self.stagger_mod}')
        return self.src.stagger_base * self.stagger_mod

class Strategy:
    '''Base Class for enemy attack AI.'''
    def __init__(self, parent:Damageable) -> None:
        self.parent:Damageable = parent
    def get_action(self) -> Action:
        '''Should always be overwritten by inhereted members'''
        return random.choice(self.parent.actions)[0](source = self.parent)
    
class Enemy(Damageable):
    '''Base Class for enemies that the player will fight.\n
    These will show up in the enemy section of GUI,
    and will be given chances to attack'''
    actions:list[Action]
    weights:list[int]
    parry_mod:float = 1.0
    strategy_class:Strategy
    parry_class:Attack
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.strategy:Strategy = self.strategy_class(parent = self)
        self.distance:int = 13
    def take_turn(self, player) -> None:
        if len(self.action_queue) != 0:
            return
        new_action = self.strategy.get_action()
        if isinstance(new_action, Attack):
            new_action.tgt = player
        self.action_queue.append(new_action)
    def get_parry_class(self):
        return self.parry_class
    def get_atk_source(self, *args):
        return self
    # deprecated
    def getset_distance(self, set = None) -> int:
        if set is not None:
            self.distance = set
        return self.distance

class Item(Viewable):
    '''Base Class for entities that can be placed in players inventory\n
    Items should have a value'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'value'):
            print(f'{self.name} has no value')
    def take(self):
        print(f'take(): {self}')
 
class CounterAttack(Action):
    '''Base class that stores an attack that is performed later'''
    def __init__(self, reaction:Attack, source: Entity, **kwargs):
        self.reaction_class = reaction
        if 'target' in kwargs:
            kwargs['target'] = None
        super().__init__(source, **kwargs)

    def react(self, target:Damageable = None):
        '''Perform the saved action'''
        if self.reaction_class is not None:
            rxn = self.reaction_class(source = self.src)
            if isinstance(rxn, Attack):
                rxn.tgt = target
            rxn.resolve(reaction = True)

class Equippable(Item):
    '''Anything that can be worn or held'''
    slot:str = None
    twohanded:bool = False
    def equip(self, plr):
        #TODO: uneqip that slot!
        plr.equipment[self.slot] = self
        if self.twohanded:
            plr.equipment['Secondary'] = None
        GUI.log(f'You equipped a {self.name}.')

class Weapon(Equippable):
    '''Base class for all weapons.\n
    Weapons must have a style. Paradigm is melee by default'''
    attacks:list[Action]
    dmg_base:int
    parry_mod:float = 1.0
    parry_class:Attack
    dodge_class:Attack = None
    def __init__(self, **kwargs):
        self.paradigm = 'melee'
        super().__init__(**kwargs)
    def get_actions(self) -> list[Attack]:
        # TODO: player talents / abilities
        return self.attacks

class ObjectAction:
    '''Class for interactable actions on objects. It should be noted that 
    ObjectActions are distinct from Actions, which are combat specific'''
    name:str
    def __init__(self, parent) -> None:
        self.parent = parent
    def resolve(self, game):
        '''Perform the action.\n
        Must be overridden by inhereted members'''
        raise NotImplementedError(self)

class RoomObject(Viewable):
    '''Objects that appear in a room. RoomObjects are interactable'''
    actions:list[ObjectAction] = None
    def __init__(self) -> None:
        super().__init__()
        if self.actions is not None:
            self.actions.append(self.Examine(self))
    class Examine(ObjectAction):
        name = 'Examine'
        def resolve(self, *args):
            GUI.log(f'{self.parent.desc}')

# TODO: door traps?
class Exit(RoomObject):
    '''Doors that connect rooms'''
    direction:str = None
    def __init__(self, room, dir:str) -> None:
        super().__init__()
        assert(dir is not None)
        self.direction = dir
        self.dest_room = room

class Room:
    '''Rooms have exits, and may contain a centerpiece and/or ground objects\n
    centerpieces and exits are just RoomObjects that are drawn in different spots.\n
    floor_objects are RoomObjects and floor_items are Items.'''
    centerpiece:RoomObject
    enemies:list[Enemy]
    _dir_opposites:dict[str, str] = {
        'n' : 's',
        's' : 'n',
        'e' : 'w',
        'w' : 'e'
    }
    def __init__(self,
                 conn_rooms:dict[str,] = {}, # e.g. 'n' : room obj
                 enemies:list[Enemy] = [],
                 centerpiece:RoomObject = None
                 ):
        self.exits:list[Exit] = []
        self.floor_objects:list[RoomObject] = []
        self.floor_items:list[Item] = []
        self.enemies = enemies
        self.centerpiece = centerpiece
        assert isinstance(conn_rooms, dict)
        self.conn_rooms = conn_rooms
        if self.conn_rooms is not None:
            for key,val in conn_rooms.items():
                self.add_exit(key, val)

    def add_exit(self, dir:str, room):
        '''Creates an exit object and sets it to a direction.\n
        directions that already exist are overwritten'''
        for e in self.exits:
            if e.direction == dir:
                self.exits.remove(e)
                break
        self.exits.append(
            Exit(room, dir)
        )
    def rand_choice(self, tuple:tuple) -> object:
        pop, wgts = zip(*tuple)
        return random.choices(pop, weights = wgts)[0]
            
    def add_to_floor(self, obj:Viewable):
        if isinstance(obj, RoomObject):
            return self.floor_objects.append(obj)
        elif isinstance(obj, Item):
            return self.floor_items.append(obj)
        else:
            raise TypeError(obj)
    
    def enter(self, game):
        game.try_move_room(self)

class Dungeon:
    '''Base class'''
    room_class:Room
    encounters:tuple
    def get_room() -> Room:
        raise NotImplementedError
    