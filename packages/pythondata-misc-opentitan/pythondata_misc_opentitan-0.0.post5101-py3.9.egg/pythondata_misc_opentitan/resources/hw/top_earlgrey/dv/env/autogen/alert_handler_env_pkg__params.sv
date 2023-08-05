// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// alert_handler_env_pkg__params.sv is auto-generated by `topgen.py` tool

parameter string LIST_OF_ALERTS[] = {
  "aes_recov_ctrl_update_err",
  "aes_fatal_fault",
  "otbn_fatal",
  "otbn_recov",
  "sensor_ctrl_aon_recov_as",
  "sensor_ctrl_aon_recov_cg",
  "sensor_ctrl_aon_recov_gd",
  "sensor_ctrl_aon_recov_ts_hi",
  "sensor_ctrl_aon_recov_ts_lo",
  "sensor_ctrl_aon_recov_ls",
  "sensor_ctrl_aon_recov_ot",
  "keymgr_fatal_fault_err",
  "keymgr_recov_operation_err",
  "otp_ctrl_fatal_macro_error",
  "otp_ctrl_fatal_check_error",
  "lc_ctrl_fatal_prog_error",
  "lc_ctrl_fatal_state_error",
  "entropy_src_recov_alert",
  "entropy_src_fatal_alert",
  "csrng_fatal_alert",
  "edn0_fatal_alert",
  "edn1_fatal_alert",
  "sram_ctrl_main_fatal_parity_error",
  "sram_ctrl_ret_aon_fatal_parity_error",
  "flash_ctrl_recov_err",
  "flash_ctrl_recov_mp_err",
  "flash_ctrl_recov_ecc_err"
};

parameter uint NUM_ALERTS = 27;
