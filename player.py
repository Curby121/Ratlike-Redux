import baseclasses as bc
import weapons
import actions

class Player(bc.Damageable):
    name = 'Player'
    desc = 'You!'
    dmg_base = 6
    stagger_base = 10
    def __init__(self):
        plr = {
            'max_hp': 35,
            'max_exh': 60,
            'exh_rec': 10
        }
        super().__init__(**plr)
        self.coins = 0
        self.inv = []
        self.equipment:dict[str, bc.Weapon] = {
            'Primary': None,
            'Secondary': None
        }
        self.action:bc.Action = None

    def take_turn(self, enemies:list[bc.Enemy]) -> bc.Attack:
        '''For testing with CLI only, this will need to be redone once GUI
        is implemented'''
        print('\n   Enemies:')
        for e in enemies:
            print(f' {e.name}: {e.hp}/{e.max_hp}  {e.exhaust}/{e.max_exh}')
        
        print(f'\n You: {self.hp}/{self.max_hp}  {self.exhaust}/{self.max_exh}')

        acts = self.get_combat_actions()
        msg = ''
        for i,a in enumerate(acts):
            msg += f'{i}:{a.name}, '
        msg = msg[:-2]
        print(f'Actions: {msg}')
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
        print(f'Chose: {action_class.name}')
        return super().take_turn(action_class, target = enemies[0])
    
    def get_reaction(self) -> bc.CounterAttack:
        if self.equipment['Primary'].dodge_class is not None:
            return self.equipment['Primary'].dodge_class
        elif self.equipment['Secondary'] is not None:
            if self.equipment['Secondary'].dodge_class is not None:
                return self.equipment['Secondary'].dodge_class
        
    def get_combat_actions(self) -> list[bc.Attack]:
        acts = []
        for key, val in self.equipment.items():
            if val is not None:
                acts.extend(val.get_actions())
        if len(acts) == 0:
            acts.append(actions.Bite)
        acts.append(actions.Dodge)
        acts.append(actions.Rest)
        return acts
    
    def get_dmg(self, atk:bc.Attack) -> float:
        # TODO: modifiers
        for key, wep in self.equipment.items():
            if wep is not None:
                for a in wep.get_actions():
                    if isinstance(atk, a):
                        return wep.dmg_base
                if isinstance(atk, wep.dodge_class):
                    return wep.dmg_base
        else:
            raise Exception('Atk not found in eqp')