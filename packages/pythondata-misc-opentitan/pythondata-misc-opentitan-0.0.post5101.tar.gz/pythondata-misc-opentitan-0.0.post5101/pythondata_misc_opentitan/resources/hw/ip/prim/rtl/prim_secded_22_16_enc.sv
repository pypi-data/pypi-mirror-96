// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// SECDED Encoder generated by
// util/design/secded_gen.py -m 6 -k 16 -s 3741324996 -c hsiao

module prim_secded_22_16_enc (
  input        [15:0] in,
  output logic [21:0] out
);

  always_comb begin : p_encode
    out = 22'(in);
    out[16] = ^(out & 22'h00C5C6);
    out[17] = ^(out & 22'h003317);
    out[18] = ^(out & 22'h009E2C);
    out[19] = ^(out & 22'h0031E9);
    out[20] = ^(out & 22'h00CA71);
    out[21] = ^(out & 22'h006C9A);
  end

endmodule : prim_secded_22_16_enc
