'''File that contains the game state and logic.\n
Contains 'static' fields as well as the player character object instances'''

import asyncio
import baseclasses as bc
import player
import enemies
import actions as actn
import weapons
import GUI

class Game:
    def __init__(self):
        self.plr = player.Player()
        self.plr_action:bc.Action = None
        weapons.Dagger().equip(self.plr)
        weapons.WoodenShield().equip(self.plr)

    async def Start(self):
        '''Start and run game'''
        GUI.init(self)
        t1 = asyncio.create_task( GUI.run() )
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
                    print('enter only single lower case letter for choice')
            await self.StartCombat([enemy])
            enemy = None

    # TODO: encounters should take place in a 'room'
    # this function mainly exists for testing currently
    async def StartCombat(self, enemies:list[bc.Enemy]):
        self.plr_lock = asyncio.Event()
        GUI.EnterCombat(enemies)
        self.plr.exhaust = 0
        while len(enemies) > 0:
            actions: list[bc.Action] = []
            if self.plr.exhaust >= self.plr.max_exh:
                self.select_player_action(actn.Rest)
                GUI.log('YOU ARE EXHAUSTED!\n')
            await self.plr_lock.wait()
            self.plr_lock.clear()

            if isinstance(self.plr_action, bc.Attack):
                self.plr_action.tgt = enemies[0]
            actions.append(self.plr_action)

            for e in enemies:
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
            while i < len(enemies):
                if enemies[i].hp <= 0:
                    enemies.remove(enemies[i])
                else:
                    e.new_turn()
                    i += 1
            
            GUI.log(' **\n')
            if self.plr.hp <= 0:
                input('You Lose!')
                quit()
        GUI.log('You Win!')

    def select_player_action(self, action:bc.Action):
        self.plr_action = action(
            source = self.plr
        )
        self.plr.action = self.plr_action
        self.plr_lock.set()
        