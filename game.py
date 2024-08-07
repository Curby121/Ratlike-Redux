'''File that contains the game state and logic.\n
Contains 'static' fields as well as the player character object instances'''

import baseclasses as bc
import player
import enemies
import actions  as actn
import weapons

class Game:
    def __init__(self):
        self.plr = player.Player()
        weapons.Dagger().equip(self.plr)
        weapons.WoodenShield().equip(self.plr)

    def Start(self):
        '''Start and run game'''
        while True:
            enemy = None
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
            self.StartCombat([enemy])

    # TODO: encounters should take place in a 'room'
    # this function mainly exists for testing currently
    def StartCombat(self, enemies:list[bc.Enemy]):
        self.plr.exhaust = 0
        while len(enemies) > 0:
            actions: list[bc.Action] = []
            actions.append(self.plr.take_turn(enemies))

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

            i = 0
            self.plr.new_turn()
            while i < len(enemies):
                if enemies[i].hp <= 0:
                    enemies.remove(enemies[i])
                else:
                    e.new_turn()
                    i += 1
            
            print (' **')
            if self.plr.hp <= 0:
                input('You Lose!')
                quit()
        print('You Win!')


        