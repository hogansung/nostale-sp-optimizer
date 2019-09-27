from typing import Optional

from shell import Shell


class Weapon:
    def __init__(self,
                 wpn_name: str,
                 wpn_type: str,
                 wpn_min_att: int,
                 wpn_max_att: int,
                 wpn_att_lvl: int,
                 wpn_ext_nml_att: int,
                 wpn_ext_ele_val: int,
                 dec_mob_res: int,
                 shell: dict,
                 ):
        self.wpn_name = wpn_name
        self.wpn_type = wpn_type
        self.wpn_min_att = wpn_min_att
        self.wpn_max_att = wpn_max_att
        self.wpn_att_lvl = wpn_att_lvl
        self.wpn_ext_nml_att = wpn_ext_nml_att
        self.wpn_ext_ele_val = wpn_ext_ele_val
        self.dec_mob_res = dec_mob_res
        self.shell = Shell(**shell)
        
        assert(self.wpn_type in ('left', 'right'))
        assert(0 <= self.wpn_att_lvl <= 10)
