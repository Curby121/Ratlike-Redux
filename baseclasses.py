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
    def examine(self) -> str:
        return f"{self.name}:\n {self.desc}"

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
        import effects
        self.action_queue:list[Action] = []
        self.effects:list[effects.Effect] = []
        super().__init__(**kwargs)
        self.balance = self.bal_max

    def get_effects(self, effect_class) -> list:
        '''Returns a list of all effects of type effect_class'''
        lst = []
        for e in self.effects:
            if isinstance(e, effect_class):
                lst.append(e)
        return lst

    def grant_effect(self, eff):
        self.effects.append(eff)

    def off_balance(self, cost:int = 0) -> bool:
        '''Returns true if entity cannot spent cost in balance'''
        return self.balance <= cost
    
    def can_use_action(self, actn_class) -> True:
        '''Returns True if entity can currently use that action'''
        if self.off_balance(actn_class.bal_use_cost):
            return False
        return True
    def examine(self) -> None:
        res = super().examine()
        if len(self.effects) != 0:
            res+='\n  Effects:\n'
            for e in self.effects:
                res += e.examine()
                res += '\n'
        return res[:-1]
    def take_turn(self):
        raise Exception(f'No turn defined for {self.name}')
    def get_atk_source(self, *args):
        '''On the player this returns the weapon, on enemies it returns the enemy'''
        raise NotImplementedError
    def get_def(self) -> int:
        raise NotImplementedError

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
        self.balance = min(self.bal_max, self.balance)
        self.balance = max(0, self.balance)
        if self.balance == 0:
            self.action_queue.clear()
            import actions # gross
            self.action_queue.append(
                actions.Stagger(self)
            )

# an instance of this class is placed on the table when an action is selected
class Action(Viewable):
    '''Combat specific actions, all of which have a timer (actions to complete) a source, balance costs, and a parry mod'''
    timer:int = 4
    bal_use_cost:int = 0
    bal_resolve_cost:int = 0
    parry_mod:float = 1.0
    use_msg:str = None
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
    
    # parry checks / defense
    acc_base = 0.5 # accuracy modifier at 0 balance
    def attack_me(self, atk):
        off_roll = atk._roll_offense()
        if self.parry_check(atk, off_roll):
            GUI.log(' The attack is parried!')
            return
        if self.deflect_check(self, off_roll):
            GUI.log(' The attack is deflected!')
            return
        return self.src.damage_me(atk)
    
    def parry_check(self, atk, off_roll:int = None) -> bool:
        '''Check if this attack parries an attacker'''
        def_mod = self.src.balance / self.src.bal_max
        def_max = int(self.parry_mod * def_mod)
        def_roll = random.randint(1, def_max + 1)
        if off_roll is None:
            off_roll = atk._roll_offense()
        print(f'{self.src.name}\'s {self.name} pry: {def_roll}/{def_max+1}  x{def_mod}')
        if def_roll > off_roll:
            return True
        return False

    # this should probably live in Entity class
    def deflect_check(self, atk, off_roll:int = None) -> bool:
        '''Check if an attack is deflected by this actions source'''
        if off_roll is None:
            off_roll = atk._roll_offense()
        def_max = self.src.get_def()
        def_roll = random.randint(1, def_max +1)
        print(f'{self.src.name}\'s {self.name} def: {def_roll}/{def_max+1}')
        if def_roll >= off_roll:
            return True
        return False

    def tick(self):
        import effects
        self.timer -= 1
        for e in self.src.get_effects(effects.on_tick):
            e(self)
    def resolve_balance(self) -> None:
        '''Consumes the balance for resolving'''
        self.src.balance -= self.bal_resolve_cost

# TODO: Damage calculation based on weapon / skills etc
class Attack(Action):
    '''Attacks are an Action that have a target.\n
    All attacks have damage and stagger mods'''
    tgt:Damageable
    acc:int
    src:Entity
    stagger_mod:float
    dmg_mod:float
    styles:list[str] = []

    def __init__(self, source: Entity, **kwargs):
        self.parry_mod = int(source.get_atk_source(self).parry * self.parry_mod)
        self.parry_mod = max(1, self.parry_mod)
        super().__init__(source, **kwargs)

    # TODO: cleanup
    def resolve(self) -> bool:
        if not super().resolve():
            return False
        self.tgt.attack_me(atk = self)
        return True

    def in_range(self, bonus:int = 0):
        if self.reach + bonus >= self.src.getset_distance():
            return True
        else:
            return False
    def get_dmg(self) -> int:
        import effects
        base = self.src.get_atk_source(self).dmg_base
        mod = self.dmg_mod
        for e in self.src.get_effects(effects.mod_damage):
            a,m = e(self)
            base += a
            mod *= m
        return base * mod
    def get_stagger(self) -> int:
        return self.src.stagger_base * self.stagger_mod

    def _roll_offense(self) -> int:
        '''Roll this attacks offense'''
        off_mod = (self.src.balance / self.src.bal_max) * self.acc_base
        off_base = self.acc

        import effects
        for e in self.src.get_effects(effects.mod_accuracy):
            a,m = e(self)
            off_base += a
            off_mod *= m

        off_max = int(off_base * (self.acc_base + off_mod))
        roll = random.randint(1, off_max + 1)
        print(f'{self.src.name}\'s {self.name} atk: {roll}/{off_max+1}  x{off_mod+self.acc_base}')
        return roll

class Channel(Action):
    '''Actions that perform differently the longer they are in use'''
    efficacy = 0 # one tick happens before any chance to resolve -> minimum of 1
    def tick(self):
        self.efficacy += 1
        return super().tick()

class Strategy:
    '''Base Class for enemy attack AI.'''
    def __init__(self, parent:Damageable) -> None:
        self.parent:Damageable = parent
        import game
        self.player = game.plr
    def get_action(self) -> Action:
        '''Should always be overwritten by inhereted members'''
        return random.choice(self.parent.actions)[0](source = self.parent)
    
class Enemy(Damageable):
    '''Base Class for enemies that the player will fight.\n
    These will show up in the enemy section of GUI,
    and will be given chances to attack'''
    actions:list[Action]
    weights:list[int]
    parry:int = 4
    strategy_class:Strategy
    defense:int = 5
    
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
    def get_atk_source(self, *args):
        return self
    def get_def(self) -> int:
        return self.defense

class Item(Viewable):
    '''Base Class for entities that can be placed in players inventory\n
    Items should have a value'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'value'):
            print(f'{self.name} has no value')
    def take(self, room):
        import game
        game.plr.inv.append(self)
        room.floor_items.remove(self)
    def drop(self, room):
        room.floor_items.append(self)
        import game
        game.plr.inv.remove(self)
        GUI.log(f'Dropped {self.name}.')
    def inventory_actions(self) -> tuple[str,]:
        return []

class Equippable(Item):
    '''Anything that can be worn or held'''
    slot:str = None
    effects:list
    defense:int = 0
    def equip(self, slot:str = None):
        #TODO: uneqip that slot!
        import game
        if slot is None:
            slot = self.slot
        if game.plr.equipment[slot] is not None:
            game.plr.inv.append(game.plr.equipment[slot])
        game.plr.equipment[slot] = self
        if self in game.plr.inv:
            game.plr.inv.remove(self)
        GUI.log(f'You equipped a {self.name}.')
    def inventory_actions(self) -> list[tuple[str,]]:
        return [
            ('Equip',self.equip)
        ]
    def get_actions(self) -> list[Attack]:
        return []
    def examine(self) -> str:
        res = super().examine()
        if self.defense > 0:
            res += f'\n  Def: {self.defense}'
        return res
    
class Weapon(Equippable):
    '''Base class for all weapons.\n
    Weapons must have a style. Paradigm is melee by default'''
    attacks:list[Action]
    dmg_base:int
    parry:int = 1
    def __init__(self, **kwargs):
        self.paradigm = 'melee'
        super().__init__(**kwargs)
    def get_actions(self) -> list[Attack]:
        # TODO: player talents / abilities
        return self.attacks
    def inventory_actions(self) -> list[tuple[str,]]:
        return [
            ('Primary',self._prim_e),
            ('Secondary',self._sec_e)
        ]
    def _prim_e(self):
        return self.equip('Primary')
    def _sec_e(self):
        return self.equip('Secondary')

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
    def rand_choice(self, tuple:tuple) -> Enemy:
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
    