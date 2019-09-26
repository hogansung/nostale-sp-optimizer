class Shell:
    def __init__(self,
                 shell_ext_nml_att: int = 0,
                 shell_ext_ele_att: int = 0,
                 shell_ext_pct_att: int = 0,
                 shell_sl_att: int = 0,
                 shell_sl_def: int = 0,
                 shell_sl_ele: int = 0,
                 shell_sl_hmp: int = 0,
                 shell_sl_all: int = 0,
                 ):
        self.shell_ext_nml_att = shell_ext_nml_att
        self.shell_ext_ele_att = shell_ext_ele_att
        self.shell_ext_pct_att = shell_ext_pct_att
        self.shell_sl_att = shell_sl_att
        self.shell_sl_def = shell_sl_def
        self.shell_sl_ele = shell_sl_ele
        self.shell_sl_hmp = shell_sl_hmp
        self.shell_sl_all = shell_sl_all
        assert(0 <= shell_sl_att <= 16)
        assert(0 <= shell_sl_def <= 16)
        assert(0 <= shell_sl_ele <= 16)
        assert(0 <= shell_sl_hmp <= 16)
        assert(0 <= shell_sl_all <= 10)  # is that true?
