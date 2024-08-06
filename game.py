'''File that contains the game state and logic.\n
Contains 'static' fields as well as the player character object instances'''

import baseclasses as bc
import player
import enemies

class Game:
    def __init__(self):
        self.plr = player.Player()

    def Start(self):
        '''Start and run game'''
        encounter = [enemies.Skeleton()]
        self.StartCombat(encounter)

    # TODO: encounters should take place in a 'room'
    # this function mainly exists for testing currently
    def StartCombat(self, enemies:list[bc.Enemy]):
        while len(enemies) > 0:
            actions: list[bc.Action] = []
            actions.append(self.plr.take_turn(enemies))

            for e in enemies:
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
        input('You Win!')


        