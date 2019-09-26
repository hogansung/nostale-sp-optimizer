class Skill:
    def __init__(self,
                 skill_name: str,
                 skill_cast_time: float,
                 skill_cool_down: float,
                 skill_nml_att: int,
                 skill_ele_att: int,
                 ):
        self.skill_name = skill_name
        self.skill_cast_time = skill_cast_time
        self.skill_cool_down = skill_cool_down
        self.skill_nml_att = skill_nml_att
        self.skill_ele_att = skill_ele_att
