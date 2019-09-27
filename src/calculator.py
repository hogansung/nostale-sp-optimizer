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
        self.sp_overall_pts = self._calculate_sp_overall_pts()
        self.best_min_dmg = 0
        self.best_max_dmg = 0
        self.best_sp_att_pts = 0
        self.best_sp_def_pts = 0
        self.best_sp_ele_pts = 0
        self.best_sp_hmp_pts = 0
        self.best_sp_acc_att_attr = 0
        self.best_sp_acc_def_attr = 0
        self.best_sp_acc_ele_attr = 0
        self.best_sp_acc_hmp_attr = 0

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

    def _calculate_sp_overall_pts(self):
        self.sp_wng_pts = [5,5,5,5,8,8,10,10,12,12,15,15,18,20,25]
        return max(0, self.char.sp_lvl - 20) * 3 + sum(self.sp_wng_pts[:self.char.sp_wng])

    def _calculate_final_dmg(self, sp_acc_att_attr, sp_acc_def_attr, sp_acc_ele_attr, sp_acc_hmp_attr):
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
        self.sp_ext_nml_att = sp_acc_att_attr
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
        self.sp_ext_ele_att = sp_acc_ele_attr
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
        self.fnl_mob_res = self.mob.mob_res - self.char.wpn.dec_mob_res
        self.char_with_wpn_with_skill_min_ele_dmg = (self.char_with_wpn_with_skill_min_ele_att * (1 + self.ele_coef / 100)) * (1 - self.fnl_mob_res / 100)
        self.char_with_wpn_with_skill_max_ele_dmg = (self.char_with_wpn_with_skill_max_ele_att * (1 + self.ele_coef / 100)) * (1 - self.fnl_mob_res / 100)

        # Final DMG
        self.fnl_min_dmg = self.char_with_wpn_with_skill_min_nml_dmg + self.char_with_wpn_with_skill_min_ele_dmg
        self.fnl_max_dmg = self.char_with_wpn_with_skill_max_nml_dmg + self.char_with_wpn_with_skill_max_ele_dmg
        return self.fnl_min_dmg, self.fnl_max_dmg

    def _calculate_sp_points_for_one_attribute(self, type, lvl):
        if type == 'sp_att':
            if lvl >= 1 and lvl <= 10: return 1
            elif lvl >= 11 and lvl <= 19: return 2
            elif lvl >= 20 and lvl <= 39: return 3
            elif lvl >= 40 and lvl <= 59: return 4
            elif lvl >= 60 and lvl <= 79: return 5
            elif lvl >= 80 and lvl <= 90: return 6
            elif lvl >= 91 and lvl <= 97: return 7
            elif lvl >= 98 and lvl <= 98: return 8
            elif lvl >= 98 and lvl <= 98: return 8
            elif lvl >= 99 and lvl <= 99: return 9
            elif lvl >= 100 and lvl <= 100: return 10
        elif type == 'sp_def':
            if lvl >= 1 and lvl <= 10: return 1
            elif lvl >= 11 and lvl <= 29: return 2
            elif lvl >= 30 and lvl <= 40: return 3
            elif lvl >= 41 and lvl <= 60: return 4
            elif lvl >= 61 and lvl <= 75: return 5
            elif lvl >= 76 and lvl <= 84: return 6
            elif lvl >= 85 and lvl <= 94: return 7
            elif lvl >= 95 and lvl <= 99: return 8
            elif lvl >= 100 and lvl <= 100: return 10
        elif type == 'sp_ele':
            if lvl >= 1 and lvl <= 20: return 1
            elif lvl >= 21 and lvl <= 30: return 2
            elif lvl >= 30 and lvl <= 40: return 3
            elif lvl >= 41 and lvl <= 50: return 4
            elif lvl >= 51 and lvl <= 70: return 5
            elif lvl >= 71 and lvl <= 80: return 6
            elif lvl >= 81 and lvl <= 100: return 7
        elif type == 'sp_hmp':
            if lvl >= 1 and lvl <= 10: return 1
            elif lvl >= 11 and lvl <= 30: return 2
            elif lvl >= 31 and lvl <= 50: return 3
            elif lvl >= 51 and lvl <= 60: return 4
            elif lvl >= 61 and lvl <= 70: return 5
            elif lvl >= 71 and lvl <= 80: return 6
            elif lvl >= 81 and lvl <= 90: return 7
            elif lvl >= 91 and lvl <= 100: return 8
        else:
            assert('Wrong sp attribute or sp attribute lvl')

    def _calculate_accumulated_sp_points_for_one_attribute(self, type, lvl):
        return sum(map(lambda x: self._calculate_sp_points_for_one_attribute(type, x), range(1, lvl+1)))

    def _calcualte_sp_attributes_for_one_attribute(self, type, lvl):
        if type == 'sp_att':
            if lvl >= 1 and lvl <= 10: return 5
            elif lvl >= 11 and lvl <= 20: return 6
            elif lvl >= 21 and lvl <= 30: return 7
            elif lvl >= 31 and lvl <= 40: return 8
            elif lvl >= 41 and lvl <= 50: return 9
            elif lvl >= 51 and lvl <= 60: return 10
            elif lvl >= 61 and lvl <= 70: return 11
            elif lvl >= 71 and lvl <= 80: return 13
            elif lvl >= 81 and lvl <= 90: return 14
            elif lvl >= 91 and lvl <= 94: return 15
            elif lvl >= 95 and lvl <= 95: return 16
            elif lvl >= 96 and lvl <= 97: return 17
            elif lvl >= 98 and lvl <= 100: return 20
        elif type == 'sp_def':
            if lvl >= 1 and lvl <= 10: return 1
            elif lvl >= 11 and lvl <= 20: return 2
            elif lvl >= 21 and lvl <= 30: return 3
            elif lvl >= 31 and lvl <= 40: return 4
            elif lvl >= 41 and lvl <= 50: return 5
            elif lvl >= 51 and lvl <= 60: return 6
            elif lvl >= 61 and lvl <= 70: return 7
            elif lvl >= 71 and lvl <= 80: return 8
            elif lvl >= 81 and lvl <= 90: return 9
            elif lvl >= 91 and lvl <= 100: return 10
        elif type == 'sp_ele':
            if lvl >= 1 and lvl <= 50: return 1
            elif lvl >= 51 and lvl <= 100: return 2
        elif type == 'sp_hmp':
            if lvl >= 1 and lvl <= 50: return 1
            elif lvl >= 51 and lvl <= 100: return 2
        else:
            assert('Wrong sp attribute or sp attribute lvl')
    
    def _calcualte_accumulated_sp_attributes_for_one_attribute(self, type, lvl):
        return sum(map(lambda x: self._calcualte_sp_attributes_for_one_attribute(type, x), range(1, lvl+1)))

    def calculate_optimized_sp_points(self):
        xd = 100
        for sp_att_pts in range(0, xd+1):
            sp_acc_att_pts = self._calculate_accumulated_sp_points_for_one_attribute('sp_att', sp_att_pts)
            if sp_acc_att_pts > self.sp_overall_pts: break
            
            sp_def_pts = 0
            sp_acc_def_pts = 0
            # for sp_def_pts in range(0, xd+1):
            #     sp_acc_def_pts = self._calculate_accumulated_sp_points_for_one_attribute('sp_def', sp_def_pts)
            #     if sp_acc_att_pts + sp_def_pts > self.sp_overall_pts: break
            
            for sp_ele_pts in range(0, xd+1):
                sp_acc_ele_pts = self._calculate_accumulated_sp_points_for_one_attribute('sp_ele', sp_ele_pts)
                if sp_acc_att_pts + sp_acc_def_pts + sp_acc_ele_pts > self.sp_overall_pts: break
            
                sp_hmp_pts = 0
                sp_acc_hmp_pts = 0
                # for sp_hmp_pts in range(0, xd+1):
                #     sp_acc_hmp_pts = self._calculate_accumulated_sp_points_for_one_attribute('sp_hmp', sp_hmp_pts)
                #     if sp_acc_att_pts + sp_acc_def_pts + sp_acc_ele_pts + sp_acc_hmp_pts > self.sp_overall_pts: break

                sp_acc_att_attr = self._calcualte_accumulated_sp_attributes_for_one_attribute(
                    'sp_att', 
                    sp_att_pts + self.char.wpn.shell.shell_sl_att + self.char.wpn.shell.shell_sl_all,
                )
                sp_acc_def_attr = self._calcualte_accumulated_sp_attributes_for_one_attribute(
                    'sp_def', 
                    sp_def_pts + self.char.wpn.shell.shell_sl_def + self.char.wpn.shell.shell_sl_all,
                )
                sp_acc_ele_attr = self._calcualte_accumulated_sp_attributes_for_one_attribute(
                    'sp_ele', 
                    sp_ele_pts + self.char.wpn.shell.shell_sl_ele + self.char.wpn.shell.shell_sl_all,
                )
                sp_acc_hmp_attr = self._calcualte_accumulated_sp_attributes_for_one_attribute(
                    'sp_hmp', 
                    sp_hmp_pts + self.char.wpn.shell.shell_sl_hmp + self.char.wpn.shell.shell_sl_all,
                )

                min_dmg, max_dmg = self._calculate_final_dmg(sp_acc_att_attr, sp_acc_def_attr, sp_acc_ele_attr, sp_acc_hmp_attr)
                if min_dmg + max_dmg > self.best_min_dmg + self.best_max_dmg:
                    self.best_min_dmg = min_dmg
                    self.best_max_dmg = max_dmg
                    self.best_sp_att_pts, self.best_sp_acc_att_attr = sp_att_pts, sp_acc_att_attr
                    self.best_sp_def_pts, self.best_sp_acc_def_attr = sp_def_pts, sp_acc_def_attr
                    self.best_sp_ele_pts, self.best_sp_acc_ele_attr = sp_ele_pts, sp_acc_ele_attr
                    self.best_sp_hmp_pts, self.best_sp_acc_hmp_attr = sp_hmp_pts, sp_acc_hmp_attr

        assert(0 <= self.best_sp_att_pts + self.best_sp_def_pts + self.best_sp_ele_pts + self.best_sp_hmp_pts <= self.sp_overall_pts)
        
        print('Best SP Settings:')
        print('ATT POINTS: {SP_ATT_PTS} - Additonal Attack {SP_ACC_ATT_ATTR}'.format(
            SP_ATT_PTS=self.best_sp_att_pts, 
            SP_ACC_ATT_ATTR=self.best_sp_acc_att_attr,
        ))
        print('DEF POINTS: {SP_DEF_PTS} - Additonal Defence {SP_ACC_DEF_ATTR}'.format(
            SP_DEF_PTS=self.best_sp_def_pts,
            SP_ACC_DEF_ATTR=self.best_sp_acc_def_attr,
        ))
        print('ELE POINTS: {SP_ELE_PTS} - Additonal Element {SP_ACC_ELE_ATTR}'.format(
            SP_ELE_PTS=self.best_sp_ele_pts, 
            SP_ACC_ELE_ATTR=self.best_sp_acc_ele_attr,
        ))
        print('HMP POINTS: {SP_HMP_PTS} - Additonal HP/MP {SP_ACC_HMP_ATTR}'.format(
            SP_HMP_PTS=self.best_sp_hmp_pts, 
            SP_ACC_HMP_ATTR=self.best_sp_acc_hmp_attr,
        ))
        print('DAMAGE: {MIN_DMG} ~ {MAX_DMG}'.format(
            MIN_DMG = self.best_min_dmg,
            MAX_DMG = self.best_max_dmg,
        ))

# def main():
char_file = 'hogan_lv89.json'
# mob_file = 'hell-knight.json'
mob_file = 'fire-.json'
# mob_file = 'bone-drake.json'
#mob_file = 'revenant-skeleton-warrior.json'

char = Character(**json.load(open(os.path.join(CHAR_FOLDER, char_file))))
mob = Monster(**json.load(open(os.path.join(MOB_FOLDER, mob_file))))

sp_calculator = SPCACULATOR(
    char = char,
    mob = mob,
)
print(sp_calculator._calculate_sp_overall_pts())
print(sp_calculator._calcualte_accumulated_sp_attributes_for_one_attribute('sp_att', 83))
print(sp_calculator._calcualte_accumulated_sp_attributes_for_one_attribute('sp_ele', 30))
print(sp_calculator._calculate_final_dmg(732, 0, 30, 0))
sp_calculator.calculate_optimized_sp_points()



# if __name__ == '__main__':
#     main()
