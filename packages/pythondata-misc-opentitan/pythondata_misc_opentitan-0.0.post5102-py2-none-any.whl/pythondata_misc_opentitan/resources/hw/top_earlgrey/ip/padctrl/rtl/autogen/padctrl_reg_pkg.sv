// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// Register Package auto-generated by `reggen` containing data structure

package padctrl_reg_pkg;

  // Param list
  parameter int NDioPads = 21;
  parameter int NMioPads = 44;
  parameter int AttrDw = 10;

  // Address width within the block
  parameter int BlockAw = 7;

  ////////////////////////////
  // Typedefs for registers //
  ////////////////////////////
  typedef struct packed {
    logic [9:0] q;
    logic        qe;
  } padctrl_reg2hw_dio_pads_mreg_t;

  typedef struct packed {
    logic [9:0] q;
    logic        qe;
  } padctrl_reg2hw_mio_pads_mreg_t;


  typedef struct packed {
    logic [9:0] d;
  } padctrl_hw2reg_dio_pads_mreg_t;

  typedef struct packed {
    logic [9:0] d;
  } padctrl_hw2reg_mio_pads_mreg_t;


  ///////////////////////////////////////
  // Register to internal design logic //
  ///////////////////////////////////////
  typedef struct packed {
    padctrl_reg2hw_dio_pads_mreg_t [20:0] dio_pads; // [714:484]
    padctrl_reg2hw_mio_pads_mreg_t [43:0] mio_pads; // [483:0]
  } padctrl_reg2hw_t;

  ///////////////////////////////////////
  // Internal design logic to register //
  ///////////////////////////////////////
  typedef struct packed {
    padctrl_hw2reg_dio_pads_mreg_t [20:0] dio_pads; // [649:440]
    padctrl_hw2reg_mio_pads_mreg_t [43:0] mio_pads; // [439:0]
  } padctrl_hw2reg_t;

  // Register Address
  parameter logic [BlockAw-1:0] PADCTRL_REGWEN_OFFSET = 7'h 0;
  parameter logic [BlockAw-1:0] PADCTRL_DIO_PADS_0_OFFSET = 7'h 4;
  parameter logic [BlockAw-1:0] PADCTRL_DIO_PADS_1_OFFSET = 7'h 8;
  parameter logic [BlockAw-1:0] PADCTRL_DIO_PADS_2_OFFSET = 7'h c;
  parameter logic [BlockAw-1:0] PADCTRL_DIO_PADS_3_OFFSET = 7'h 10;
  parameter logic [BlockAw-1:0] PADCTRL_DIO_PADS_4_OFFSET = 7'h 14;
  parameter logic [BlockAw-1:0] PADCTRL_DIO_PADS_5_OFFSET = 7'h 18;
  parameter logic [BlockAw-1:0] PADCTRL_DIO_PADS_6_OFFSET = 7'h 1c;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_0_OFFSET = 7'h 20;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_1_OFFSET = 7'h 24;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_2_OFFSET = 7'h 28;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_3_OFFSET = 7'h 2c;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_4_OFFSET = 7'h 30;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_5_OFFSET = 7'h 34;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_6_OFFSET = 7'h 38;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_7_OFFSET = 7'h 3c;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_8_OFFSET = 7'h 40;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_9_OFFSET = 7'h 44;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_10_OFFSET = 7'h 48;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_11_OFFSET = 7'h 4c;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_12_OFFSET = 7'h 50;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_13_OFFSET = 7'h 54;
  parameter logic [BlockAw-1:0] PADCTRL_MIO_PADS_14_OFFSET = 7'h 58;


  // Register Index
  typedef enum int {
    PADCTRL_REGWEN,
    PADCTRL_DIO_PADS_0,
    PADCTRL_DIO_PADS_1,
    PADCTRL_DIO_PADS_2,
    PADCTRL_DIO_PADS_3,
    PADCTRL_DIO_PADS_4,
    PADCTRL_DIO_PADS_5,
    PADCTRL_DIO_PADS_6,
    PADCTRL_MIO_PADS_0,
    PADCTRL_MIO_PADS_1,
    PADCTRL_MIO_PADS_2,
    PADCTRL_MIO_PADS_3,
    PADCTRL_MIO_PADS_4,
    PADCTRL_MIO_PADS_5,
    PADCTRL_MIO_PADS_6,
    PADCTRL_MIO_PADS_7,
    PADCTRL_MIO_PADS_8,
    PADCTRL_MIO_PADS_9,
    PADCTRL_MIO_PADS_10,
    PADCTRL_MIO_PADS_11,
    PADCTRL_MIO_PADS_12,
    PADCTRL_MIO_PADS_13,
    PADCTRL_MIO_PADS_14
  } padctrl_id_e;

  // Register width information to check illegal writes
  parameter logic [3:0] PADCTRL_PERMIT [23] = '{
    4'b 0001, // index[ 0] PADCTRL_REGWEN
    4'b 1111, // index[ 1] PADCTRL_DIO_PADS_0
    4'b 1111, // index[ 2] PADCTRL_DIO_PADS_1
    4'b 1111, // index[ 3] PADCTRL_DIO_PADS_2
    4'b 1111, // index[ 4] PADCTRL_DIO_PADS_3
    4'b 1111, // index[ 5] PADCTRL_DIO_PADS_4
    4'b 1111, // index[ 6] PADCTRL_DIO_PADS_5
    4'b 1111, // index[ 7] PADCTRL_DIO_PADS_6
    4'b 1111, // index[ 8] PADCTRL_MIO_PADS_0
    4'b 1111, // index[ 9] PADCTRL_MIO_PADS_1
    4'b 1111, // index[10] PADCTRL_MIO_PADS_2
    4'b 1111, // index[11] PADCTRL_MIO_PADS_3
    4'b 1111, // index[12] PADCTRL_MIO_PADS_4
    4'b 1111, // index[13] PADCTRL_MIO_PADS_5
    4'b 1111, // index[14] PADCTRL_MIO_PADS_6
    4'b 1111, // index[15] PADCTRL_MIO_PADS_7
    4'b 1111, // index[16] PADCTRL_MIO_PADS_8
    4'b 1111, // index[17] PADCTRL_MIO_PADS_9
    4'b 1111, // index[18] PADCTRL_MIO_PADS_10
    4'b 1111, // index[19] PADCTRL_MIO_PADS_11
    4'b 1111, // index[20] PADCTRL_MIO_PADS_12
    4'b 1111, // index[21] PADCTRL_MIO_PADS_13
    4'b 0111  // index[22] PADCTRL_MIO_PADS_14
  };
endpackage

