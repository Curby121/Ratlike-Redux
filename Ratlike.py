'''#Welcome to ratlike!'''

import asyncio
import game

if __name__ == "__main__":
    game_instance = game.Game()
    asyncio.run(game_instance.Start())

else:
    print('whuh woah')
    input('Enter to Exit')