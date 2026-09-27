import re
import json
from pathlib import Path


WARNING_PATTERN = re.compile(
    r"^%Warning-([A-Z0-9_]+):\s+(.+?):(\d+):(\d+):\s+(.*)$"
)


def parse_verilator_log(log_path):
    """
    Parse Verilator warning diagnostics into structured records.
    """

    log_path = Path(log_path)
    diagnostics = []

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            match = WARNING_PATTERN.match(line)

            if not match:
                continue

            rule, file_path, line_no, column, message = match.groups()

            diagnostics.append({
                "rule": rule,
                "file": file_path,
                "line": int(line_no),
                "column": int(column),
                "severity": "warning",
                "message": message.strip()
            })

    return diagnostics


if __name__ == "__main__":
    log_file = "arm32_workspace/Verilog Files/baseline_verilator.log"

    diagnostics = parse_verilator_log(log_file)

    print(json.dumps({
        "lint_errors": diagnostics
    }, indent=2))

    print(f"\nTotal diagnostics parsed: {len(diagnostics)}")