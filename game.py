'''File that contains the game state and logic.\n
Contains 'static' fields as well as the player character object instances'''

import asyncio
import baseclasses as bc
import actions as actn
import roomobjects as ro
import rooms
import player
import weapons
import GUI
import items

plr:player.Player = None # for access externally
current_room = None

class Game:
    def __init__(self):
        self.plr = player.Player()
        global plr
        plr = self.plr

        # for holding execution for when a player decision needs to be made
        self.plr_event = asyncio.Event()

        GUI.log('Welcome to Rat Game!\n'+
                'The game is over when your hp reaches 0. Choose actions carefully! Actions are mediated by '+
                'the balance of the creature using it. Before an attack lands the defender has a chance to parry it. '+
                'Parry chance is affected much more by balance than accuracy. Try to knock your opponent off balance and then go for the killing blow!'
                )

        #testing
        weapons.Sword()._prim_e()
        #weapons.Spear()._prim_e()
        #weapons.Mace()._prim_e()

        weapons.WoodenShield()._sec_e()
        #weapons.Dagger()._sec_e()

        #items.Ring(gem_class=items.Opal).equip()

        #for i in range(4): plr.inv.append(weapons.WoodenShield())
        #plr.inv.append(weapons.WoodenShield())
        #plr.inv.append(weapons.LeatherCap())

    async def Start(self):
        '''Start and run game'''
        GUI.init(self)
        t1 = asyncio.create_task( GUI.run() )

        self.room = rooms.LabyrinthRoom()
        self.room.enter(self)

        while True:
            await self.EnterRoom()
            await self.plr_event.wait()
            self.plr_event.clear()

    async def EnterRoom(self):
        if len(self.room.enemies) != 0:
            await self.StartCombat(self.room)
        else:
            GUI.EnterRoom(self.room)

    async def StartCombat(self, room:bc.Room):
        plr.generate_effects() # create all player effects from equipment
        self.plr.balance = self.plr.bal_max

        GUI.EnterCombatRoom(room)

        while len(room.enemies) > 0:
            # update gui
            update_gui()

            # TODO: initiative, currently player always has

            # GET PLAYER ACTION IF NONE
            if len(self.plr.action_queue) == 0:
                self.plr_event.clear() # ensure entering room set() doesnt stick
                if self.plr.balance <= 0:
                    self.select_player_action(actn.Pause)
                    GUI.log('YOU LOSE YOUR BALANCE!\n')
                    await asyncio.sleep(1)
                await self.plr_event.wait() # wait for plr input
                await asyncio.sleep(.4)

            # GET ENEMY ACTION IF NONE
            if len(self.room.enemies[0].action_queue) == 0:
                self.room.enemies[0].take_turn(self.plr)
                if not isinstance(self.room.enemies[0].action_queue[0], actn.Pause):
                    await asyncio.sleep(.8)

            # increment all current action timers
            self.plr.action_queue[0].tick()
            self.room.enemies[0].action_queue[0].tick()

            # resolve actions
            if self.plr.action_queue[0].timer <= 0:
                self.plr.action_queue[0].resolve()
                await asyncio.sleep(0.4)
            if self.room.enemies[0].action_queue[0].timer == 0:
                self.room.enemies[0].action_queue[0].resolve()
                await asyncio.sleep(0.4)

            # kill resolved actions
            if self.plr.action_queue[0].timer <= 0:
                self.plr.action_queue[0].resolve_balance()
                self.plr.action_queue.pop(0)
            if self.room.enemies[0].action_queue[0].timer <= 0:
                self.room.enemies[0].action_queue[0].resolve_balance()
                self.room.enemies[0].action_queue.pop(0)
                
            # new turn bookkeeping
            i = 0
            self.plr.new_turn()
            if room.enemies[0].hp <= 0:
                room.enemies.remove(room.enemies[0])
            else:
                room.enemies[0].new_turn()
            
            await asyncio.sleep(0.2)
            if self.plr.hp <= 0:
                input('You Lose!')
                quit()
        GUI.log('You Win!')
        return self._reload_room()

    def get_enemy_action(self) -> bc.Action:
        try:
            return self.room.enemies[0].action_queue[0]
        except IndexError:
            pass
    
    def get_player_action(self) -> bc.Action:
        try:
            return self.plr.action_queue[0]
        except IndexError:
            pass

# DEPRECATED -> TODO: remove
    async def get_turn_actions(self, room:bc.Room) -> list[bc.Action]:
        actions = []
        self.plr_event.clear() # ensure entering room set() doesnt stick
        if self.plr.balance >= self.plr.bal_max:
            self.select_player_action(actn.Pause)
            GUI.log('YOU LOSE YOUR BALANCE!\n')
            await asyncio.sleep(1)
        await self.plr_event.wait() # wait for plr input

        # enemy actions
        for e in room.enemies:
            actions.append(e.take_turn(self.plr))

        #actions = sort_actions(self.plr_action, actions)
        lst = [self.plr_action]
        lst.append(actions)
        return lst

    def select_player_action(self, action:bc.Action):
        '''Sets player combat action.'''
        new_action = action(
            source = self.plr
        )
        if isinstance(new_action, bc.Attack):
            new_action.tgt = self.room.enemies[0]
        self.plr.action_queue.append(new_action)
        self.plr_event.set()

    def on_object_action(self, obj:bc.RoomObject, index:int):
        print('on_object_action')

    def try_move_room(self, room:bc.Room):
        print(f'enter room: {room} with floor: {room.floor_items}')
        self.room = room
        self.plr_event.set()

    # TODO: remove this and find a clever way to do it in GUI, the flashing sucks
    def _reload_room(self):
        '''Called to refresh the GUI'''
        return GUI.current_frame.Refresh()
    
# DEPRECATED -> TODO: remove
def sort_actions(plr_action:bc.Action, actions:list[bc.Action]) -> list[bc.Action]:
    non_atks = []
    a_sorted = []
    if isinstance(plr_action, bc.Attack):
        a_sorted.append(plr_action)
    else:
        non_atks.append(plr_action)

    for a in actions:
        if isinstance(a, bc.Attack):
            for i,s in enumerate(a_sorted):
                if a > s: # see Attack.__gt__()
                    a_sorted.insert(i, a)
                    break
            else:
                a_sorted.append(a)
        else:
            non_atks.append(a)

    a_sorted.extend(non_atks)
    return a_sorted

def update_gui():
    p_acts = plr.get_combat_actions()
    GUI.current_frame.make_plr_actions(p_acts, plr.get_availables(p_acts))