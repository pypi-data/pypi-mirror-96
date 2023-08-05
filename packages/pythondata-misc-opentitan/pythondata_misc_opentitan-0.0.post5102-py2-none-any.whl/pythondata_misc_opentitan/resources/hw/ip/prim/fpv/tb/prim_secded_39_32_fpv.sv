// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// SECDED FPV testbench generated by util/design/secded_gen.py

module prim_secded_39_32_fpv (
  input               clk_i,
  input               rst_ni,
  input        [31:0] in,
  output logic [31:0] d_o,
  output logic [6:0] syndrome_o,
  output logic [1:0]  err_o,
  input        [38:0] error_inject_i
);

  logic [38:0] data_enc;

  prim_secded_39_32_enc prim_secded_39_32_enc (
    .in,
    .out(data_enc)
  );

  prim_secded_39_32_dec prim_secded_39_32_dec (
    .in(data_enc ^ error_inject_i),
    .d_o,
    .syndrome_o,
    .err_o
  );

endmodule : prim_secded_39_32_fpv
