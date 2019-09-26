import json
import math
import os
import random

from character import Character
from monster import Monster


CHAR_FOLDER = '../char/'
MOB_FOLDER = '../mob/'


class SPCACULATOR:
    def __init__(self,
                char: Character,
                mob: Monster,
    ):
        self.char = char
        self.mob = mob
        self.att_def_diff_table = {
            0: 0,
            1: 1.10,
            2: 1.15,
            3: 1.22,
            4: 1.32,
            5: 1.43,
            6: 1.54,
            7: 1.65,
            8: 1.90,
            9: 2.20,
            10: 3,
            -1: 0.90,
            -2: 0.85,
            -3: 0.78,
            -4: 0.68,
            -5: 0.57,
            -6: 0.46,
            -7: 0.35,
            -8: 0.10,
            -9: -0.20,
            -10: -1,
        }
        self.skill_nml_att, self.skill_ele_att = self._calculate_skill_att()
        self.ext_ele_val = self.char.wpn.wpn_ext_ele_val
        self.ele_coef = self._calculate_ele_coef()
        self.sp_pts = self._calculate_sp_pts()
        self.best_dmg = 0
        self.best_sp_att = 0
        self.best_sp_def = 0
        self.best_sp_ele = 0
        self.best_sp_hmp = 0

    def _calculate_skill_att(self):
        return self.char.sp.skills[0].skill_nml_att, self.char.sp.skills[0].skill_ele_att

    def _calculate_ele_coef(self):
        if (self.char.sp.sp_ele_type, self.mob.mob_ele_type) == ('fire', 'shadow'):
            return 50
        elif (self.char.sp.sp_ele_type, self.mob.mob_ele_type) == ('shadow', 'water'):
            return 50
        elif (self.char.sp.sp_ele_type, self.mob.mob_ele_type) == ('water', 'light'):
            return 50
        elif (self.char.sp.sp_ele_type, self.mob.mob_ele_type) == ('fire', 'water'):
            return 100
        elif (self.char.sp.sp_ele_type, self.mob.mob_ele_type) == ('water', 'fire'):
            return 100
        elif (self.char.sp.sp_ele_type, self.mob.mob_ele_type) == ('light', 'shadow'):
            return 200
        elif (self.char.sp.sp_ele_type, self.mob.mob_ele_type) == ('shadow', 'light'):
            return 200
        elif self.char.sp.sp_ele_type != 'no-element' and self.mob.mob_ele_type == 'no-element':
            return 30
        else:
            return 0

    def _calculate_sp_pts(self):
        return 0

    def _calculate_final_dmg(self):
        # AEQ
        self.att_def_diff_level = self.char.wpn.wpn_att_lvl - self.mob.mob_def_lvl
        if self.att_def_diff_level:
            self.att_def_dmg_scaler = self.att_def_diff_table[self.att_def_diff_level]
            self.scaled_wpn_min_att = self.char.wpn.wpn_min_att * self.att_def_dmg_scaler
            self.scaled_wpn_max_att = self.char.wpn.wpn_max_att * self.att_def_dmg_scaler
            if self.scaled_wpn_min_att <= 0:
                rnd_dmg = math.floor((random.random() * 5) + 1)
                self.scaled_wpn_min_att = self.scaled_wpn_max_att = rnd_dmg
        else:
            self.scaled_wpn_min_att = 0
            self.scaled_wpn_max_att = 0

        '''
            APG Function
            - sp_ext_nml_att: attack given by sp = attack with sp - attack without sp
            - wpn_ext_nml_att: attack given by equipments
            - shell_ext_nml_att: enhanced dmg given by shell
        '''
        self.sp_ext_nml_att = 290
        self.char_with_wpn_min_nml_att = self.scaled_wpn_min_att + self.char.basic_att + self.sp_ext_nml_att + self.char.wpn.wpn_ext_nml_att + self.char.wpn.shell.shell_ext_nml_att
        self.char_with_wpn_max_nml_att = self.scaled_wpn_max_att + self.char.basic_att + self.sp_ext_nml_att + self.char.wpn.wpn_ext_nml_att + self.char.wpn.shell.shell_ext_nml_att

        '''
            AT Function
            - skill_nml_att: skill physical dmg
            - att_def_diff_ext_att: (att_def_diff_table[att_def_diff_level] - 1) * 100
            - shell_ext_pct_att: S- % Damage shell
        '''
        self.att_def_diff_ext_att = (self.att_def_diff_table[self.att_def_diff_level] - 1) * 100
        self.char_with_wpn_with_skill_min_nml_att = (self.char_with_wpn_min_nml_att + self.skill_nml_att + self.att_def_diff_ext_att) * (1 + self.char.wpn.shell.shell_ext_pct_att)
        self.char_with_wpn_with_skill_max_nml_att = (self.char_with_wpn_max_nml_att + self.skill_nml_att + self.att_def_diff_ext_att) * (1 + self.char.wpn.shell.shell_ext_pct_att)
        
        '''
            Physical Damage
            - mob_def: mob defence
        '''
        self.char_with_wpn_with_skill_min_nml_dmg = self.char_with_wpn_with_skill_min_nml_att - self.mob.mob_def
        self.char_with_wpn_with_skill_max_nml_dmg = self.char_with_wpn_with_skill_max_nml_att - self.mob.mob_def

        '''
            E Function
            - fairy_pct: Faily %
            - sp_ext_ele_att: element given by sp
        '''
        self.sp_ext_ele_att = 106
        self.char_with_wpn_min_ele_att = (self.char_with_wpn_with_skill_min_nml_att + 100) * (self.char.fairy_pct + self.sp_ext_ele_att) / 100
        self.char_with_wpn_max_ele_att = (self.char_with_wpn_with_skill_max_nml_att + 100) * (self.char.fairy_pct + self.sp_ext_ele_att) / 100

        '''
            Et Function
            - ext_ele_val: increased ele val
            - skill_ele_att: skill elemental dmg
        '''
        self.char_with_wpn_with_skill_min_ele_att = self.char_with_wpn_min_ele_att + self.ext_ele_val + self.skill_ele_att
        self.char_with_wpn_with_skill_max_ele_att = self.char_with_wpn_max_ele_att + self.ext_ele_val + self.skill_ele_att

        '''
            Ef Function
            - mob_res # % mob res
            - ele_coef # element-based coefficient
            - dec_mob_res # % enemy reduced res
            - fnl_mob_res = mob_res - dec_mob_res
        '''
        self.fnl_mob_res = max(0, self.mob.mob_res - self.char.wpn.dec_mob_res)
        self.char_with_wpn_with_skill_min_ele_dmg = (self.char_with_wpn_with_skill_min_ele_att * (1 + self.ele_coef / 100)) * (1 - self.fnl_mob_res / 100)
        self.char_with_wpn_with_skill_max_ele_dmg = (self.char_with_wpn_with_skill_max_ele_att * (1 + self.ele_coef / 100)) * (1 - self.fnl_mob_res / 100)

        # Final DMG
        self.fnl_min_dmg = self.char_with_wpn_with_skill_min_nml_dmg + self.char_with_wpn_with_skill_min_ele_dmg
        self.fnl_max_dmg = self.char_with_wpn_with_skill_max_nml_dmg + self.char_with_wpn_with_skill_max_ele_dmg
        return self.fnl_min_dmg, self.fnl_max_dmg

    def calculate_optimized_sp_points(self):
        for sp_att in range(0, min(100, self.sp_pts)+1):
            for sp_def in range(0, min(100, self.sp_pts - sp_att)+1):
                for sp_ele in range(0, min(100, self.sp_pts - sp_att - sp_def)+1):
                    for sp_hmp in range(0, min(100, self.sp_pts - sp_att - sp_def - sp_ele)+1):
                        dmg = self._calculate_final_dmg()
                        if dmg > self.best_dmg:
                            self.best_sp_att = sp_att
                            self.best_sp_def = sp_def
                            self.best_sp_ele = sp_ele
                            self.best_sp_hmp = sp_hmp

        assert(0 <= self.best_sp_att + self.best_sp_def + self.best_sp_ele + self.best_sp_hmp <= self.sp_pts)


# def main():
char_file = 'hogan_lv89.json'
mob_file = 'dander.json'

char = Character(**json.load(open(os.path.join(CHAR_FOLDER, char_file))))
mob = Monster(**json.load(open(os.path.join(MOB_FOLDER, mob_file))))

sp_calculator = SPCACULATOR(
    char = char,
    mob = mob,
)
print(sp_calculator._calculate_final_dmg())



# if __name__ == '__main__':
#     main()
