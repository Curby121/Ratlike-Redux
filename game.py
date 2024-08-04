'''File that contains the game state and logic.\n
Contains 'static' fields as well as the player character object instances'''

import baseclasses as bc
import player
import enemies
import encounters

class Game:
    def __init__(self):
        self.plr = player.Player()

    def Start(self):
        '''Start and run game'''
        self.StartCombat(encounters.goblins)

    # TODO: encounters should take place in a 'room'
    # this function mainly exists for testing currently
    def StartCombat(self, enemies:list[bc.Enemy]):
        while True:
            actions: list[bc.Action] = []
            actions.append(self.plr.take_turn(enemies))

            for e in enemies:
                actions.append(e.take_turn(self.plr))

            actions.sort(key = lambda x: x.reach, reverse = True)
            for a in actions:
                a.resolve()

            i = 0
            self.plr.new_turn()
            while i < len(enemies):
                if enemies[i].hp <= 0:
                    enemies.remove(enemies[i])
                    i -= 1
                else:
                    e.new_turn()
                    i += 1
            
            print (' **')


        