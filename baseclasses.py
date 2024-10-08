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
    move:int
    def __init__(self, **kwargs) -> None:
        self.action:Action = None
        super().__init__(**kwargs)
    def getset_distance(self, set = None) -> int:
        return NotImplementedError
    def off_balance(self, threshold:float = None) -> bool:
        '''Returns true if entity is off balance by the given threshold.\n
        Negative threshold returns False'''
        if threshold is None:
            threshold = 0.5
        if threshold < 0:
            return False
        return self.exhaust > self.max_exh * threshold
    def get_reaction(self):
        return None
    def get_parry_class(self):
        return NotImplementedError
    def can_use_action(self, actn_class) -> True:
        '''Returns True if entity can currently use that action'''
        if self.getset_distance() < actn_class.min_dist:
            #print(f'{self.name}:{actn_class.name} under min dist')
            return False
        if self.off_balance(actn_class.balance_max):
            #print(f'{self.name}:{actn_class.name} off balance')
            return False
        return True
    def in_range(self, actn) -> bool:
        '''Returns true if an attack will land, False otherwise\n
        non attacks will always return true'''
        if isinstance(actn, Attack):
            if self.getset_distance() > actn.reach - actn.pre_move:
                print(f'{actn.name} out of range')
                return False
        else:
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
        self.exhaust = 0

    def _take_damage(self, dmg:int, stgr:int):
        self.hp -= dmg
        self.exhaust += stgr
        if dmg == 0:
            GUI.log(f'  {self.name} lost {stgr} balance!')
        else:
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
    balance_max:int = 0.5 # off balance is: exh > max_exh * balance_max
    min_dist:int = 0 # minimum distance this atk can be used
    pre_move:int = 0 # pre moves all happen before the turn starts
    def __init__(self, source:Entity, **kwargs):
        super().__init__(**kwargs)
        self.eff: float = 1.0
        self.silent:bool = False
        self.src:Damageable = source
        if self.src.getset_distance() < self.min_dist:
            raise Exception(f'min distance exception on {self.name}, dist = {self.src.getset_distance()}')
    def pre_turn(self):
        if self.pre_move != 0:
            self.mod_distance(change = self.pre_move)
    def resolve(self) -> bool: # false it needs to cancel
        '''Perform this action'''
        self.src.exhaust += self.exh_cost
        if self.use_msg is not None and not self.silent:
            GUI.log(f'{self.src.name} {self.use_msg}')
        return True
    
    def attack_me(self, **kwargs):
        self.damage_me(**kwargs)

    #TODO: simplify args
    def damage_me(self, atk,
               dmg_mod:float = 1.0,
               stagger_mod:float = 1.0,
               move_in_range:bool = False # force a move to the atks range
               ):
        '''Attack the source of this action. This function can be overridden
        on actions that interrupt incoming attacks'''
        if not isinstance(atk, Attack):
            raise ValueError
        dmg = int(atk.get_dmg() * dmg_mod)
        stagger = int(atk.get_stagger() * stagger_mod)
        print(f'damage_me stgr: {stagger} = {atk.get_stagger()} * {stagger_mod}')
        self.src._take_damage(dmg, stagger)
        self.eff *= 1 -(dmg / self.src.max_hp)
        self.eff *= 1 -(stagger / self.src.max_exh)
        if move_in_range:
            self.mod_distance(dist_max = atk.reach)

    # change the distance of this action
    # TODO: move this to entity and override in enemy and plr
    def mod_distance(
            self,
            change:int = 0,
            dist_min:int = 0,
            dist_max:int = -1
            ):
        dist = self.src.getset_distance()
        dist += change
        dist = max(dist, dist_min)
        if dist_max > -1:
            dist = min(dist, dist_max)
        print(f'mod_dist(self={self.name}, change={change}, min={dist_min}, max={dist_max}) = {dist}')
        self.src.getset_distance(set = dist)

# TODO: Damage calculation based on weapon / skills etc
# TODO: tie weapon to attack (as source)
class Attack(Action):
    '''Attacks are an Action that have a target.\n
    All attacks have a damage, stagger, and reach'''
    tgt:Entity
    reach:int
    acc:int
    parry:int
    parry_push:bool = 0 # on a successful parry push the parried attack back this much (to reach)
    stagger_mod:float
    dmg_mod:float
    move:int = 0
    styles:list[str] = []

    def __init__(self, source: Entity, **kwargs):
        self.parry = int(source.get_atk_source(self).parry_mod * self.parry)
        self.parry = max(1, self.parry)
        super().__init__(source, **kwargs)

    # TODO: cleanup
    def resolve(self, reaction:bool = False) -> bool:
        resolves = True
        if self.reach < self.get_distance() - self.src.move: # out of range
            GUI.log(f'{self.src.name}\'s {self.name} couldn\'t reach!')
            resolves = False
            # CAN YOU MOVE ON A ATTACK NOT IN RANGE?
            if not reaction:
                pass
                #GUI.log(f'{self.src.name} moved {self.src.move} step closer.')
                #self.mod_distance(change = -1 * self.src.move)
            return False

        if not super().resolve():
            return False

        if not resolves:
            return False

        # if i CAN move into atk range this turn
        self.mod_distance(dist_max = self.reach)
        if self.move != 0 and not reaction: # no moves on reaction unless it puts u in range
            self.mod_distance(change = self.move)
        self.tgt.action.attack_me(atk = self)
        return True

    # parry checks
    def attack_me(self, atk):
        p_mod = 1.0
        if self.src.off_balance():
            p_mod = 0.75
        def_roll = random.randint(1, int(self.parry * p_mod) + 1)
        off_roll = random.randint(1, int(atk.acc * atk.eff) + 1)
        print(f'stgr mod off/def: {off_roll} / {def_roll}')
        if def_roll >= off_roll / 2:
            if def_roll > off_roll:
                GUI.log(' The attack is parried!')
                stgr_mod = 0.75
            else:
                GUI.log(' The attack is blocked.')
                stgr_mod = 1
                
            # parry pushing
            if self.reach > self.get_distance() and self.parry_push != 0:
                GUI.log(f'  {self.name} pushed back {atk.src.name}!')
                self.mod_distance(change = self.parry_push, dist_max = self.reach)

            return self.damage_me(
                atk,
                dmg_mod = 0,
                stagger_mod = stgr_mod
                )
        else:
            GUI.log(' The attack slips though!')
        return self.damage_me(atk)

    def in_range(self, bonus:int = 0):
        if self.reach + bonus >= self.src.getset_distance():
            return True
        else:
            return False

    def get_distance(self) -> int:
        return self.src.getset_distance()
        
    def get_eff_reach(self) -> int:
        return min(self.reach, self.get_distance())

    def get_dmg(self) -> int:
        self.src: Enemy
        return self.src.get_atk_source(self).dmg_base * self.dmg_mod * self.eff
    # stagger not effected by eff ?
    def get_stagger(self) -> int:
        print(f'attack stgr: {self.src.stagger_base} * {self.stagger_mod}')
        return self.src.stagger_base * self.stagger_mod
    
    def __gt__(self, other):
        if not isinstance(other, Attack):
            raise ValueError
        my_r = self.get_eff_reach()
        other_r = other.get_eff_reach()
        if my_r > other_r:
            return True
        elif my_r == other_r:
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
    def take_turn(self, player):
        self.action = self.strategy.get_action()
        if isinstance(self.action, Attack):
            self.action.tgt = player
        return self.action
    def get_parry_class(self):
        return self.parry_class
    def get_atk_source(self, *args):
        return self
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
    