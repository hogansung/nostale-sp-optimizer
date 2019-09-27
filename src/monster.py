class Monster:
    def __init__(self,
        mob_def: int,
        mob_def_lvl: int,
        mob_res: int, 
        mob_ele_type: str
    ):
        self.mob_def = mob_def
        self.mob_def_lvl = mob_def_lvl
        self.mob_res = mob_res
        self.mob_ele_type = mob_ele_type
        assert(0 <= self.mob_def_lvl <= 10)
        assert(-100 <= self.mob_res <= 100)
        assert(self.mob_ele_type in ('light', 'shadow', 'fire', 'water', 'no-element'))