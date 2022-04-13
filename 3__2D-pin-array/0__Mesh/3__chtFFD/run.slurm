#! /bin/bash
#
# T. Kattmann, 14.01.2022
# Write FFD-box to mesh and make a test deformation.

SU2_DEF FFD-setting_configMaster.cfg | tee DEF.log

set_ffd_design_var.py -i 8 -j 8 -k 0 -b BOX -m 'fluid_pin2_interface, fluid_pin1_interface, fluid_pin3_interface, solid_pin2_interface, solid_pin1_interface, solid_pin3_interface, fluid_inlet, fluid_outlet, solid_pin1_inlet, solid_pin3_outlet' --dimension 2
set_ffd_design_var.py -i 8 -j 8 -k 0 -b FRONTBOX -m 'fluid_pin2_interface, fluid_pin1_interface, fluid_pin3_interface, solid_pin2_interface, solid_pin1_interface, solid_pin3_interface, fluid_inlet, fluid_outlet, solid_pin1_inlet, solid_pin3_outlet' --dimension 2
set_ffd_design_var.py -i 8 -j 8 -k 0 -b BACKBOX -m 'fluid_pin2_interface, fluid_pin1_interface, fluid_pin3_interface, solid_pin2_interface, solid_pin1_interface, solid_pin3_interface, fluid_inlet, fluid_outlet, solid_pin1_inlet, solid_pin3_outlet' --dimension 2

SU2_DEF deform_configMaster.cfg | tee deform_DEF.log

SU2_CFD CFD_deform_configMaster.cfg | tee CFD.log
