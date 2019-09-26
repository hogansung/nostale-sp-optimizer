from typing import Sequence

from skill import Skill


class Specialist:
    def __init__(self,
                 sp_name: str,
                 sp_ele_type: str,
                 wpn_type: str,
                 skills: Sequence[dict],
                 ):
        self.sp_name = sp_name
        self.sp_ele_type = sp_ele_type
        self.wpn_type = wpn_type
        self.skills = list(map(lambda skill: Skill(**skill), skills))
        # assert sp_name
        assert(self.wpn_type in ('left', 'right'))
        assert(self.sp_ele_type in ('light', 'shadow', 'fire', 'water', 'no-element'))