#! /bin/bash

SU2_DEF chtMaster.cfg | tee  DEF.log

#set_ffd_design_var...

SU2_DEF deform_chtMaster.cfg | tee deform_DEF.log
