CAPI=2:
# Copyright lowRISC contributors.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0
#
# xbar_${xbar.name}_sim core file generated by `tlgen.py` tool
name: "lowrisc:dv:xbar_${xbar.name}_sim:0.1"
description: "XBAR DV sim target"
filesets:
  files_dv:
    depend:
      - lowrisc:${library_name}:xbar_${xbar.name}
      - lowrisc:dv:dv_utils
      - lowrisc:dv:xbar_tb
      - lowrisc:dv:xbar_${xbar.name}_bind
    files:
      - tb__xbar_connect.sv: {is_include_file: true}
      - xbar_env_pkg__params.sv: {is_include_file: true}
    file_type: systemVerilogSource


targets:
  sim: &sim_target
    toplevel: xbar_tb_top
    filesets:
      - files_dv
    default_tool: vcs

  lint:
    <<: *sim_target
