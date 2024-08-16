'''File that contains the game state and logic.\n
Contains 'static' fields as well as the player character object instances'''

import asyncio
import baseclasses as bc
import actions as actn
import roomobjects as ro
import rooms
import player
import enemies
import weapons
import GUI

class Game:
    def __init__(self):
        self.plr = player.Player()
        self.plr_action:bc.Action = None
        self.room = None

        # for holding execution for when a player descision needs to be made
        self.plr_event = asyncio.Event()

        #testing
        weapons.Dagger().equip(self.plr)
        weapons.WoodenShield().equip(self.plr)

    async def Start(self):
        '''Start and run game'''
        GUI.init(self)
        t1 = asyncio.create_task( GUI.run() )

        room = rooms.LabyrinthRoom()
        room.enter(self)

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
        GUI.EnterRoom(room)
        self.plr.exhaust = 0
        while len(room.enemies) > 0:
            # get action list
            actions = await self.get_turn_actions(room)
            
            # Action resolution
            for a in actions:
                # TODO: comprehensive death checks
                if a.src.hp <= 0:
                    continue
                a.resolve()
                await asyncio.sleep(.2) # animation delay
                
            # new turn bookkeeping
            i = 0
            self.plr.new_turn()
            while i < len(room.enemies): # kill checks
                if room.enemies[i].hp <= 0:
                    room.enemies.remove(room.enemies[i])
                else:
                    room.enemies[i].new_turn()
                    i += 1
            
            GUI.log(' **\n')
            if self.plr.hp <= 0:
                input('You Lose!')
                quit()
        GUI.log('You Win!')
        return self._reload_room()

    async def get_turn_actions(self, room:bc.Room) -> list[bc.Action]:
        actions = []
        self.plr_event.clear() # ensure entering room set() doesnt stick
        if self.plr.exhaust >= self.plr.max_exh:
            self.select_player_action(actn.Rest)
            GUI.log('YOU ARE EXHAUSTED!\n')
        await self.plr_event.wait() # wait for plr input

        # enemy actions
        for e in room.enemies:
            if e.exhaust >= e.max_exh:
                actions.append(actn.Rest(e))
            else:
                actions.append(e.take_turn(self.plr))
        actions = sort_actions(self.plr_action, actions)
        return actions

    def select_player_action(self, action:bc.Action):
        '''Sets player combat action.'''
        self.plr_action = action(
            source = self.plr,
            target = self.room.enemies[0]
        )
        self.plr.action = self.plr_action
        self.plr_event.set()

    def on_object_action(self, obj:bc.RoomObject, index:int):
        print('on_object_action')

    def try_move_room(self, room:bc.Room):
        self.room = room
        self.plr_event.set()

    # TODO: remove this and find a clever way to do it in GUI, the flashing sucks
    def _reload_room(self):
        '''Called to refresh the GUI'''
        return self.try_move_room(self.room)
    
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
