// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// SECDED FPV assertion file generated by util/design/secded_gen.py

module prim_secded_hamming_22_16_assert_fpv (
  input        clk_i,
  input        rst_ni,
  input [15:0] in,
  input [15:0] d_o,
  input [5:0] syndrome_o,
  input [1:0]  err_o,
  input [21:0] error_inject_i
);

  // Inject a maximum of two errors simultaneously.
  `ASSUME_FPV(MaxTwoErrors_M, $countones(error_inject_i) <= 2)
  // This bounds the input data state space to make sure the solver converges.
  `ASSUME_FPV(DataLimit_M, $onehot0(in) || $onehot0(~in))
  // Single bit error detection
  `ASSERT(SingleErrorDetect_A, $countones(error_inject_i) == 1 |-> err_o[0])
  `ASSERT(SingleErrorDetectReverse_A, err_o[0] |-> $countones(error_inject_i) == 1)
  // Double bit error detection
  `ASSERT(DoubleErrorDetect_A, $countones(error_inject_i) == 2 |-> err_o[1])
  `ASSERT(DoubleErrorDetectReverse_A, err_o[1] |-> $countones(error_inject_i) == 2)
  // Single bit error correction (implicitly tests the syndrome output)
  `ASSERT(SingleErrorCorrect_A, $countones(error_inject_i) < 2 |-> in == d_o)
  // Basic syndrome check
  `ASSERT(SyndromeCheck_A, |syndrome_o |-> $countones(error_inject_i) > 0)
  `ASSERT(SyndromeCheckReverse_A, $countones(error_inject_i) > 0 |-> |syndrome_o)

endmodule : prim_secded_hamming_22_16_assert_fpv
