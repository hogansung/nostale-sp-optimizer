import json
import os

from typing import Optional

from shell import Shell
from specialist import Specialist
from weapon import Weapon


SPS_FOLDER = '../sp/'
WPN_FOLDER = '../wpn/'

SPS_TEMPLATE = 'sp_template.json'
WPN_TEMPLATE = 'wpn_template.json'


class Character():
    def __init__(self,
                 basic_att: int,
                 fairy_pct: int,
                 lt_wpn_name: Optional[str],
                 rt_wpn_name: Optional[str],
                 sp_name: Optional[str],
                 sp_lvl: int,
                 sp_wng: int,
                 ):
        self.basic_att = basic_att
        self.fairy_pct = fairy_pct
        self.lt_wpn_name = lt_wpn_name
        self.rt_wpn_name = rt_wpn_name
        self.sp_name = sp_name
        self.sp_lvl = sp_lvl
        self.sp_wng = sp_wng
        self.sp_data = {}
        self.wpn_data = {}
        self._load_sp_data()
        assert(self.sp_name is None or self.sp_name in self.sp_data)
        self.sp = self._find_sps(self.sp_name)
        self._load_wpn_data()
        assert(self.lt_wpn_name is None or self.lt_wpn_name in self.wpn_data)
        assert(self.rt_wpn_name is None or self.rt_wpn_name in self.wpn_data)
        self.lt_wpn = self._find_wpn(self.lt_wpn_name)
        self.rt_wpn = self._find_wpn(self.rt_wpn_name)
        assert(1 <= self.sp_lvl <= 99)
        assert(0 <= self.sp_wng <= 15)
        self.wpn = Weapon(
            self.lt_wpn.wpn_name if self.sp.wpn_type == 'left' else self.rt_wpn.wpn_name,
            self.lt_wpn.wpn_type if self.sp.wpn_type == 'left' else self.rt_wpn.wpn_type,
            self.lt_wpn.wpn_min_att if self.sp.wpn_type == 'left' else self.rt_wpn.wpn_min_att,
            self.lt_wpn.wpn_max_att if self.sp.wpn_type == 'left' else self.rt_wpn.wpn_max_att,
            self.lt_wpn.wpn_att_lvl if self.sp.wpn_type == 'left' else self.rt_wpn.wpn_att_lvl,
            max(self.lt_wpn.wpn_ext_nml_att, self.rt_wpn.wpn_ext_nml_att),
            max(self.lt_wpn.wpn_ext_ele_val, self.rt_wpn.wpn_ext_ele_val),
            max(self.lt_wpn.dec_mob_res, self.rt_wpn.dec_mob_res),
            {
               "shell_ext_nml_att": max(self.lt_wpn.shell.shell_ext_nml_att, self.rt_wpn.shell.shell_ext_nml_att),
               "shell_ext_ele_att": max(self.lt_wpn.shell.shell_ext_ele_att, self.rt_wpn.shell.shell_ext_ele_att),
               "shell_ext_pct_att": max(self.lt_wpn.shell.shell_ext_pct_att, self.rt_wpn.shell.shell_ext_pct_att),
               "shell_sl_att": max(self.lt_wpn.shell.shell_sl_att, self.rt_wpn.shell.shell_sl_att),
               "shell_sl_def": max(self.lt_wpn.shell.shell_sl_def, self.rt_wpn.shell.shell_sl_def),
               "shell_sl_ele": max(self.lt_wpn.shell.shell_sl_ele, self.rt_wpn.shell.shell_sl_ele),
               "shell_sl_hmp": max(self.lt_wpn.shell.shell_sl_hmp, self.rt_wpn.shell.shell_sl_hmp),
               "shell_sl_all": max(self.lt_wpn.shell.shell_sl_all, self.rt_wpn.shell.shell_sl_all),                 
            }
        )

    def _load_sp_data(self):
        for sp_file in os.listdir(SPS_FOLDER):
            sp_filepath = os.path.join(SPS_FOLDER, sp_file)
            if sp_file != SPS_TEMPLATE and os.path.isfile(sp_filepath):
                sp = Specialist(**json.load(open(sp_filepath)))
                self.sp_data[sp.sp_name] = sp

    def _load_wpn_data(self):
        for wpn_file in os.listdir(WPN_FOLDER):
            wpn_filepath = os.path.join(WPN_FOLDER, wpn_file)
            if wpn_file != WPN_TEMPLATE and os.path.isfile(wpn_filepath):
                wpn = Weapon(**json.load(open(wpn_filepath)))
                self.wpn_data[wpn.wpn_name] = wpn

    def _find_sps(self, sp_name):
        return self.sp_data[sp_name] if sp_name else None

    def _find_wpn(self, wpn_name):
        return self.wpn_data[wpn_name] if wpn_name else None
