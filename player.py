import baseclasses as bc
import actions

class Player(bc.Damageable):
    name = 'Player'
    desc = 'You!'
    dmg_base = 5
    stagger_base = 3
    move = 1
    defense = 5
    def __init__(self):
        plr = {
            'max_hp': 35,
            'bal_max': 15,
            'bal_rec': 1
        }
        super().__init__(**plr)
        self.coins = 0
        self.inv:list[bc.Item] = []
        self.equipment:dict[str, bc.Equippable] = {
            'Primary': None,
            'Secondary': None,
            'Hand': None,
            'Neck': None,
            'Head': None,
            'Chest': None
        }
        self.action:bc.Action = None

    def get_first_from_eqps(self, predicate) -> bc.Equippable:
        for slot, eq in self.equipment.items():
            if eq is not None:
                if predicate(eq) is not None:
                    return predicate(eq)
        return None

    def get_combat_actions(self) -> list[bc.Action]:
        acts = []
        for key, wep in self.equipment.items():
            if wep is not None:
                for act in wep.get_actions():
                    if act not in acts:
                        acts.append(act)
                #acts.extend(wep.get_actions())
        if len(acts) == 0:
            acts.append(actions.Bite)
        acts.append(actions.Dodge)
        acts.append(actions.Pause)
        return acts

    def get_availables(self, actns:list[bc.Action]) -> list[bool]:
        res = []
        for a in actns:
            if self.can_use_action(a):
                res.append(True)
            else:
                res.append(False)
        return res

    def get_weapon_with_attack(self, atk:bc.Attack) -> bc.Weapon:
        for key, wep in self.equipment.items():
            if wep is not None:
                for a in wep.get_actions():
                    if isinstance(atk, a):
                        return wep
        else:
            print('Atk not found in eqp')
            return atk

    def generate_effects(self):
        self.effects.clear()
        for slot, item in self.equipment.items():
            if item is None: continue
            if not hasattr(item, 'effects'): continue
            for e in item.effects:
                try:
                    self.grant_effect(e)
                except AttributeError: pass

    def get_dmg(self, atk:bc.Attack) -> float:
        for key, wep in self.equipment.items():
            if wep is not None:
                for a in wep.get_actions():
                    if isinstance(atk, a):
                        return wep.dmg_base
        else:
            raise Exception('Atk not found in eqp')

    def get_def(self) -> int:
        res = self.defense
        for slot, item in self.equipment.items():
            if item is not None:
                res += item.defense
        return res

    def get_atk_source(self, atk) -> bc.Weapon:
        return self.get_weapon_with_attack(atk)
    
    def get_parry_base(self, atk):
        res = 0
        for slot, item in self.equipment.items():
            try:
                for act in item.get_actions():
                    if isinstance(atk, act):
                        res += item.parry
                        print(f'{atk.name} found.')
                        break
                else:
                    res += item.parry / 2
            except AttributeError as e:
                pass
        return res

    def examine_equipment(self) -> str:
        res = ''
        for key,value in self.equipment.items():
            name = 'None'
            if value is not None:
                name = value.name
            res+=f'{key}: {name}\n'
        return res[:-1]