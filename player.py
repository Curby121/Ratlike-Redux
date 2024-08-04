import baseclasses as bc
import weapons
import actions

class Player(bc.Damageable):
    name = 'Player'
    desc = 'You!'
    def __init__(self):
        plr = {
            'max_hp': 50,
            'max_exh': 100,
            'exh_rec': 7
        }
        super().__init__(**plr)
        self.coins = 0
        self.inv = []
        self.equipment:dict[str, bc.Weapon] = {
            'Primary': weapons.Dagger(),
            'Secondary': None
        }
        self.action:bc.Action = None

    def take_turn(self, enemies:list[bc.Enemy]) -> bc.Attack:
        print('\n   Enemies:')
        for e in enemies:
            print(f' {e.name}: {e.hp}/{e.max_hp}  {e.exhaust}/{e.max_exh}')
        
        print(f'\n You: {self.hp}/{self.max_hp}  {self.exhaust}/{self.max_exh}')
        
        acts = self.get_combat_actions()
        print(f'You Can: {acts}')
        action_class = None
        while action_class is None:
            i = input('->')
            if i == '': i = 0
            try:
                action_class = acts[int(i)]
            except Exception as e:
                print(f'[Err] {e}')

        if self.exhaust >= self.max_exh:
            action_class = actions.Rest
        print(f'Chose: {action_class}')
        return super().take_turn(action_class, target = enemies[0])
    
    def get_reaction(self) -> bc.CounterAttack:
        if self.equipment['Primary'].dodge_class:
            return self.equipment['Primary'].dodge_class
        elif self.equipment['Secondary'].dodge_class:
            return self.equipment['Secondary'].dodge_class
        
    def get_combat_actions(self) -> list[bc.Attack]:
        acts = []
        for key, val in self.equipment.items():
            if val is not None:
                acts.extend(val.get_actions())
        if len(acts) == 0:
            acts.append(actions.Bite)
        acts.append(actions.Dodge)
        return acts