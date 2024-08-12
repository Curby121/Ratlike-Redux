'''File that contains the game state and logic.\n
Contains 'static' fields as well as the player character object instances'''

import asyncio
import baseclasses as bc
import actions as actn
import roomobjects as ro
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

        room2 = bc.Room(
            centerpiece = ro.Chest(
                contents = [
                    weapons.Dagger()
                ]
            )
        )
        room1 = bc.Room(
            conn_rooms = {
                'n':room2
            },
            enemies = [
                enemies.Goblin()
            ]
        )

        room2.add_exit('s', room1)

        self.room = room1

        enemy = enemies.Goblin()
        while True:
            while enemy is None:
                x = input('Wep (da/sp), Enemy (g/s/t):')
                if x == 'da':
                    weapons.Dagger().equip(self.plr)
                    weapons.WoodenShield().equip(self.plr)
                elif x == 'sp':
                    weapons.Spear().equip(self.plr)
                elif x == 'g':
                    enemy = enemies.Goblin()
                elif x == 's':
                    enemy = enemies.Skeleton()
                elif x == 't':
                    enemy = enemies.CaveTroll()
                else:
                    print('crimnge')

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
            actions: list[bc.Action] = []
            if self.plr.exhaust >= self.plr.max_exh:
                self.select_player_action(actn.Rest)
                GUI.log('YOU ARE EXHAUSTED!\n')
            await self.plr_event.wait()
            self.plr_event.clear()

            if isinstance(self.plr_action, bc.Attack):
                self.plr_action.tgt = room.enemies[0]
            actions.append(self.plr_action)

            for e in room.enemies:
                if e.exhaust >= e.max_exh:
                    actions.append(actn.Rest(e))
                else:
                    actions.append(e.take_turn(self.plr))

            actions.sort(key = lambda x: x.reach, reverse = True)
            for a in actions:
                # TODO: comprehensive death checks
                if a.src.hp <= 0:
                    continue
                a.resolve()
                await asyncio.sleep(.2) # animation delay

            i = 0
            self.plr.new_turn()
            while i < len(room.enemies):
                if room.enemies[i].hp <= 0:
                    room.enemies.remove(room.enemies[i])
                else:
                    e.new_turn()
                    i += 1
            
            GUI.log(' **\n')
            if self.plr.hp <= 0:
                input('You Lose!')
                quit()
        GUI.log('You Win!')
        return self._reload_room()

    def select_player_action(self, action:bc.Action):
        '''Sets player combat action and ticks turn fwd'''
        self.plr_action = action(
            source = self.plr
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