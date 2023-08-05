// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// alert_handler_env_pkg__params.sv is auto-generated by `topgen.py` tool

parameter string LIST_OF_ALERTS[] = {
% for alert in top["alert"]:
  % if loop.last:
  "${alert["name"]}"
  % else:
  "${alert["name"]}",
  % endif
% endfor
};

parameter uint NUM_ALERTS = ${len(top["alert"])};
