#!/bin/bash

cd ~/sweat-workshop || exit 1

export VERIFLOW_RTL_ROOT="$PWD/arm32_workspace/Verilog Files"

echo "Running Verilator lint analysis..."

verilator --lint-only \
  -I"$VERIFLOW_RTL_ROOT" \
  "$VERIFLOW_RTL_ROOT/top.v" \
  2>&1 | tee "$VERIFLOW_RTL_ROOT/baseline_verilator.log"

echo ""
echo "Lint analysis complete."
