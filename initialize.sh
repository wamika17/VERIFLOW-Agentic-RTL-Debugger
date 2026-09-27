#!/bin/bash

cd ~/sweat-workshop || exit 1

cp -a "arm32_original/Verilog Files/." "arm32_workspace/Verilog Files/"

export VERIFLOW_RTL_ROOT="$PWD/arm32_workspace/Verilog Files"

rm -f approvals.json
rm -f veriflow_report.md
rm -f veriflow_report.html
rm -f agent_decisions.json
rm -f "$VERIFLOW_RTL_ROOT/baseline_verilator.log"

echo "VERIFLOW workspace initialized."
