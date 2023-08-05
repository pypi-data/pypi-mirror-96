// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// Register Package auto-generated by `reggen` containing data structure

package sram_ctrl_reg_pkg;

  // Param list
  parameter int NumAlerts = 1;

  // Address width within the block
  parameter int BlockAw = 5;

  ////////////////////////////
  // Typedefs for registers //
  ////////////////////////////
  typedef struct packed {
    logic        q;
    logic        qe;
  } sram_ctrl_reg2hw_alert_test_reg_t;

  typedef struct packed {
    logic [2:0]  q;
  } sram_ctrl_reg2hw_exec_reg_t;

  typedef struct packed {
    logic        q;
    logic        qe;
  } sram_ctrl_reg2hw_ctrl_reg_t;


  typedef struct packed {
    struct packed {
      logic        d;
    } error;
    struct packed {
      logic        d;
    } escalated;
    struct packed {
      logic        d;
    } scr_key_valid;
    struct packed {
      logic        d;
    } scr_key_seed_valid;
  } sram_ctrl_hw2reg_status_reg_t;

  typedef struct packed {
    logic [31:0] d;
    logic        de;
  } sram_ctrl_hw2reg_error_address_reg_t;


  ///////////////////////////////////////
  // Register to internal design logic //
  ///////////////////////////////////////
  typedef struct packed {
    sram_ctrl_reg2hw_alert_test_reg_t alert_test; // [6:5]
    sram_ctrl_reg2hw_exec_reg_t exec; // [4:2]
    sram_ctrl_reg2hw_ctrl_reg_t ctrl; // [1:0]
  } sram_ctrl_reg2hw_t;

  ///////////////////////////////////////
  // Internal design logic to register //
  ///////////////////////////////////////
  typedef struct packed {
    sram_ctrl_hw2reg_status_reg_t status; // [36:33]
    sram_ctrl_hw2reg_error_address_reg_t error_address; // [32:0]
  } sram_ctrl_hw2reg_t;

  // Register Address
  parameter logic [BlockAw-1:0] SRAM_CTRL_ALERT_TEST_OFFSET = 5'h 0;
  parameter logic [BlockAw-1:0] SRAM_CTRL_STATUS_OFFSET = 5'h 4;
  parameter logic [BlockAw-1:0] SRAM_CTRL_EXEC_REGWEN_OFFSET = 5'h 8;
  parameter logic [BlockAw-1:0] SRAM_CTRL_EXEC_OFFSET = 5'h c;
  parameter logic [BlockAw-1:0] SRAM_CTRL_CTRL_REGWEN_OFFSET = 5'h 10;
  parameter logic [BlockAw-1:0] SRAM_CTRL_CTRL_OFFSET = 5'h 14;
  parameter logic [BlockAw-1:0] SRAM_CTRL_ERROR_ADDRESS_OFFSET = 5'h 18;

  // Reset values for hwext registers and their fields
  parameter logic [0:0] SRAM_CTRL_ALERT_TEST_RESVAL = 1'h 0;
  parameter logic [0:0] SRAM_CTRL_ALERT_TEST_FATAL_PARITY_ERROR_RESVAL = 1'h 0;
  parameter logic [3:0] SRAM_CTRL_STATUS_RESVAL = 4'h 0;
  parameter logic [0:0] SRAM_CTRL_CTRL_RESVAL = 1'h 0;

  // Register Index
  typedef enum int {
    SRAM_CTRL_ALERT_TEST,
    SRAM_CTRL_STATUS,
    SRAM_CTRL_EXEC_REGWEN,
    SRAM_CTRL_EXEC,
    SRAM_CTRL_CTRL_REGWEN,
    SRAM_CTRL_CTRL,
    SRAM_CTRL_ERROR_ADDRESS
  } sram_ctrl_id_e;

  // Register width information to check illegal writes
  parameter logic [3:0] SRAM_CTRL_PERMIT [7] = '{
    4'b 0001, // index[0] SRAM_CTRL_ALERT_TEST
    4'b 0001, // index[1] SRAM_CTRL_STATUS
    4'b 0001, // index[2] SRAM_CTRL_EXEC_REGWEN
    4'b 0001, // index[3] SRAM_CTRL_EXEC
    4'b 0001, // index[4] SRAM_CTRL_CTRL_REGWEN
    4'b 0001, // index[5] SRAM_CTRL_CTRL
    4'b 1111  // index[6] SRAM_CTRL_ERROR_ADDRESS
  };
endpackage

