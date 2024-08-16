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
    def set_action(self, action_class, **kwargs):
        self.action = action_class(
            source = self,
            **kwargs
        )
        return self.action
    def get_dmg(self, atk) -> float:
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
        self.exhaust = 0
    def _take_damage(self, dmg:int, stgr:int):
        self.hp -= dmg
        self.exhaust += stgr
        GUI.log(f'  {self.name} took {dmg} dmg, {stgr} stgr!')
    def new_turn(self):
        '''Reset bookkeeping for next turn'''
        self.exhaust = max(0, self.exhaust - self.exh_rec)

# an instance of this class is placed on the table when an action is selected
class Action(Viewable):
    '''Combat specific actions. All actions have a source and can be targetted
    by Attacks'''
    exh_cost:int = 0
    use_msg:str = None
    reach:int = 0
    def __init__(self, source:Entity, **kwargs):
        self.eff: float = 1.0
        self.silent:bool = False
        super().__init__(**kwargs)
        self.src:Damageable = source
    def resolve(self):
        '''Perform this action'''
        self.src.exhaust += self.exh_cost
        if self.use_msg is not None and not self.silent:
            GUI.log(f'{self.src.name} {self.use_msg}')
    def attack(self, atk,
               dmg_mod:float = 1.0,
               stagger_mod:float = 1.0,
               mod_dist:bool = True,
               dist_max:int = -1,
               dist_min:int = -1,
               move:int = 0
               ):
        '''Attack the source of this action. This function can be overridden
        on actions that interrupt incoming attacks'''
        dmg = int(atk.dmg() * dmg_mod)
        stagger = int(atk.stagger() * stagger_mod)
        self.src._take_damage(dmg, stagger)
        self.eff *= 1 -(dmg / self.src.max_hp)
        self.eff *= 1 -(stagger / self.src.max_exh)
        if mod_dist:
            self.mod_distance(atk,
                              change = move,
                              dist_min = dist_min,
                              dist_max = dist_max)

    def mod_distance(
            self,
            atk,
            atk_mod:bool = True, # stops the atk.reach from modifying the distance
            change:int = 0,
            dist_min:int = 0,
            dist_max:int = -1
            ):
        if self is atk:
            raise Exception('mod_distance called with atk as self')
        if isinstance(self.src, Enemy):
            enemy = self.src
        elif isinstance(atk.src, Enemy):
            enemy = atk.src
        try:
            enemy.distance += change
            dist = enemy.distance
            if atk_mod:
                dist = min(enemy.distance, atk.reach)
        except Exception as e:
            print(f'Atks: atk:{atk}, tgt:{self}')
            print(f'Sources: atk:{atk.src}, tgt:{self.src}')
            raise e
        dist = max(dist, dist_min)
        if dist_max != -1:
            dist = min(dist, dist_max)
        enemy.distance = dist

# TODO: Damage calculation based on weapon / skills etc
# TODO: tie weapon to attack (as source)
class Attack(Action):
    '''Attacks are an Action that have a target.\n
    All attacks have a damage, stagger, and reach'''
    reach:int
    stagger_mod:float
    dmg_mod:float
    move:int = 0 # amount it moves forward after resolving
    styles:list[str] = []
    def __init__(self, source:Entity, target:Damageable = None, **kwargs):
        self.tgt:Damageable = target
        super().__init__(source = source, **kwargs)
        self.eff_r = self._get_eff_reach()

    def resolve(self):
        super().resolve()
        self.tgt.action.mod_distance(self, change = self.move)
        if self.tgt is not None:
            self.tgt.action.attack(atk = self)

    def get_distance(self) -> int:
        if isinstance(self.tgt, Enemy):
            return self.tgt.distance
        elif isinstance(self.src, Enemy):
            return self.src.distance
        else:
            print(f'err, src {self.src}, tgt: {self.tgt}')
            raise NotImplementedError
        
    def _get_eff_reach(self) -> int:
        return min(self.reach, self.get_distance())

    def dmg(self) -> int:
        print(f' Dmg(): {self.src} deals {self.src.get_dmg(self)} x{self.dmg_mod} x{self.eff}')
        return self.src.get_dmg(self) * self.dmg_mod * self.eff
    def stagger(self) -> int:
        return self.src.stagger_base * self.stagger_mod * self.eff
    
    def __gt__(self, other):
        if not isinstance(other, Attack):
            raise ValueError
        if self.eff_r > other.eff_r:
            return True
        elif self.eff_r == other.eff_r:
            if 'quick' in self.styles and 'quick' not in other.styles:
                return True
        else:
            return False

class Strategy:
    '''Base Class for enemy attack AI.'''
    def __init__(self, parent:Damageable) -> None:
        self.parent:Damageable = parent
    def get_action(self) -> Action:
        '''Should always be overwritten by inhereted members'''
        return random.choice(self.parent.actions)[0]
    
class Enemy(Damageable):
    '''Base Class for enemies that the player will fight.\n
    These will show up in the enemy section of GUI,
    and will be given chances to attack'''
    actions:list[Action]
    weights:list[int]
    distance:int
    strategy_class:Strategy
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.strategy:Strategy = self.strategy_class(parent = self)
        self.distance = 30
    def take_turn(self, player, action_class = None):
        if action_class is None:
            action_class = self.strategy.get_action()
        return self.set_action(target = player, action_class = action_class)
    def get_dmg(self, atk:Attack = None) -> float:
        print(f'get_dmg enemy : {self.dmg_base}')
        return self.dmg_base

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
            return self.reaction_class(
                target = target,
                source = self.src
                ).resolve()

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
    