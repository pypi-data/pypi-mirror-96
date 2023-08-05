// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

class chip_env_cov extends cip_base_env_cov #(.CFG_T(chip_env_cfg));
  `uvm_component_utils(chip_env_cov)

  // the base class provides the following handles for use:
  // chip_env_cfg: cfg

  // covergroups

  function new(string name, uvm_component parent);
    super.new(name, parent);
    // instantiate all covergroups here
  endfunction : new

endclass
