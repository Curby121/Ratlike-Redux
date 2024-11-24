'''#Welcome to ratlike!'''

import asyncio
import game

game_instance = None

if __name__ == "__main__":
    game_instance = game.Game()
    try:
        asyncio.run(game_instance.Start())
    except KeyboardInterrupt:
        print('\n****\nKeyboard Interrupt: Kill program \n')
        quit()

else:
    print('whuh woah')
    input('Enter to Exit')