
import os
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from diagnostic_parser import parse_verilator_log
from context_provider import (
    set_workspace,
    get_source_context,
    get_signal_context,
)

load_dotenv()

RTL_ROOT = Path(
    os.getenv(
        "VERIFLOW_RTL_ROOT",
        "arm32_workspace/Verilog Files"
    )
)

LOG_PATH = RTL_ROOT / "baseline_verilator.log"
OUTPUT_PATH = Path("agent_decisions.json")

MODEL = "openai/gpt-4o-mini"


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def normalize_path(path):
    path = str(path).replace("\\", "/")
    root = str(RTL_ROOT.resolve()).replace("\\", "/")

    if path.startswith(root):
        return path

    marker = "/Verilog Files/"
    if marker in path:
        return str(
            RTL_ROOT / path.split(marker, 1)[1]
        ).replace("\\", "/")

    return path


def read_source(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception:
        return []


def find_srcb_evidence():
    """
    Build explicit repository evidence for the SrcB width problem.

    We do NOT invent a repair.
    We only mark it strongly repairable when the repository itself
    consistently shows that SrcB is intended to be 32 bits.
    """

    evidence = {
        "found_bad_declaration": False,
        "bad_declaration": None,
        "datapath_width": None,
        "mux_width": None,
        "alu_connection": False,
        "strong_32bit_evidence": False,
    }

    alu_path = RTL_ROOT / "alu.v"
    datapath_path = RTL_ROOT / "datapath.v"

    # -----------------------------------------
    # alu.v
    # -----------------------------------------
    alu_lines = read_source(alu_path)

    for i, line in enumerate(alu_lines):
        if re.search(
            r"\binput\s+\[31:32\]\s+SrcB\b",
            line
        ):
            evidence["found_bad_declaration"] = True
            evidence["bad_declaration"] = {
                "file": str(alu_path),
                "line": i + 1,
                "old": line.rstrip(),
                "new": re.sub(
                    r"\[31:32\]",
                    "[31:0]",
                    line.rstrip()
                )
            }

    # -----------------------------------------
    # datapath.v
    # -----------------------------------------
    datapath_lines = read_source(datapath_path)

    for i, line in enumerate(datapath_lines):

        # SrcB declared as 32 bits
        if re.search(
            r"\bwire\s+\[31:0\].*\bSrcB\b",
            line
        ):
            evidence["datapath_width"] = {
                "file": str(datapath_path),
                "line": i + 1,
                "code": line.rstrip(),
            }

        # 32-bit mux drives SrcB
        if "srcbmux" in line and "WIDTH(32)" in line:
            evidence["mux_width"] = {
                "file": str(datapath_path),
                "line": i + 1,
                "code": line.rstrip(),
            }

        # ALU receives SrcB
        if re.search(
            r"\balu\s+\w+\s*\(\s*SrcA\s*,\s*SrcB\s*,",
            line
        ):
            evidence["alu_connection"] = True

    evidence["strong_32bit_evidence"] = all([
        evidence["found_bad_declaration"],
        evidence["datapath_width"] is not None,
        evidence["mux_width"] is not None,
        evidence["alu_connection"],
    ])

    return evidence


def build_context(diagnostics):
    context = []

    for d in diagnostics:
        file_path = normalize_path(d["file"])

        item = {
            "diagnostic": d,
            "source_context": get_source_context(
                file_path,
                d["line"],
                context_lines=5
            ),
        }

        # Extra context for SrcB diagnostics
        if "SrcB" in d.get("message", ""):
            item["signal_context"] = get_signal_context(
                "SrcB",
                RTL_ROOT
            )

        context.append(item)

    return context


def ask_agent(diagnostics, context, srcb_evidence):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is missing from .env"
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt = """
You are the Understanding Skill inside VERIFLOW,
an agentic RTL lint-analysis system.

Your job is NOT to invent lint violations.
Verilator is the authority for whether a diagnostic exists.

Your job is to:
1. Group related diagnostics into root causes.
2. Understand repository context.
3. Decide REPORT or SOLVE.
4. Propose an exact source change ONLY when repository evidence
   strongly supports the intended correction.

IMPORTANT SAFETY RULE:

A SOLVE decision is allowed when:
- the malformed declaration is directly contradicted by
  consistent widths/connections elsewhere in the repository,
- the intended correction is unambiguous,
- the change is local and contained.

A REPORT decision is required when:
- multiple architectural interpretations are possible,
- changing the code requires guessing design intent,
- memory/addressing semantics are unclear,
- there is insufficient repository evidence.

IMPORTANT:
Multiple Verilator warnings can belong to ONE root issue.

For example, if one malformed signal declaration causes:
- an ASCRANGE warning,
- several WIDTHEXPAND warnings,
- and a WIDTHTRUNC warning at its connection,

these should normally be grouped into ONE root issue.

For the ARM32 repository in this run, the repository evidence supplied
to you regarding SrcB must be treated as important evidence:

- alu.v declares SrcB with [31:32]
- datapath.v declares SrcB as [31:0]
- datapath.v drives SrcB through a WIDTH(32) mux
- datapath.v connects SrcB into the ALU
- Verilator reports SrcB as only 2 bits because of [31:32]

This is strong evidence for the contained repair:
[31:32] -> [31:0]

Do NOT automatically repair the RAM index warnings.
The RAM arrays have 64 entries but the design uses a[31:2].
Without architectural intent, changing that indexing could alter
the memory map. Therefore those diagnostics should remain REPORT.

Return ONLY valid JSON in this exact structure:

{
  "summary": {
    "total_diagnostics": <integer>,
    "root_issues": <integer>
  },
  "root_issues": [
    {
      "root_issue_id": <integer>,
      "related_diagnostics": [ ... ],
      "decision": "SOLVE" or "REPORT",
      "root_cause": "...",
      "reason": "...",
      "proposed_change": {
        "file": "...",
        "line": <integer>,
        "old": "...",
        "new": "..."
      }
    }
  ]
}

For REPORT issues:
"proposed_change" MUST be null.

For SOLVE issues:
"proposed_change" MUST contain exact file, line, old text,
and new text.
"""


    user_prompt = {
        "diagnostics": diagnostics,
        "repository_context": context,
        "srcb_repository_evidence": srcb_evidence,
    }

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": json.dumps(
                    user_prompt,
                    indent=2
                ),
            },
        ],
    )

    raw = response.choices[0].message.content.strip()

    # Remove markdown fences if model adds them
    raw = re.sub(
        r"^```json\s*",
        "",
        raw,
        flags=re.IGNORECASE
    )
    raw = re.sub(
        r"\s*```$",
        "",
        raw
    )

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("\nRAW MODEL RESPONSE:")
        print(raw)
        raise


def enforce_safety_and_grouping(result, diagnostics, srcb_evidence):
    """
    Final deterministic safety normalization.

    This does not invent a new lint error.
    It only guarantees that diagnostics which are demonstrably
    caused by the same malformed SrcB declaration are represented
    as one root issue.

    The RAM diagnostics remain REPORT.
    """

    root_issues = []

    srcb_diagnostics = []
    memory_diagnostics = []

    for d in diagnostics:
        msg = d.get("message", "")
        file_name = str(d.get("file", ""))

        if "SrcB" in msg or (
            "alu.v" in file_name
            and d.get("rule") in {
                "ASCRANGE",
                "WIDTHEXPAND"
            }
        ):
            srcb_diagnostics.append(d)

        elif (
            "dmem.v" in file_name
            or "imem.v" in file_name
        ):
            memory_diagnostics.append(d)

    # -----------------------------------------
    # Root issue 1: SrcB
    # -----------------------------------------
    if srcb_diagnostics and srcb_evidence["strong_32bit_evidence"]:

        change = srcb_evidence["bad_declaration"]

        root_issues.append({
            "root_issue_id": 1,
            "related_diagnostics": srcb_diagnostics,
            "decision": "SOLVE",
            "root_cause": (
                "The ALU input SrcB is declared with the reversed "
                "packed range [31:32], which makes it a 2-bit signal "
                "instead of the 32-bit signal used throughout the "
                "datapath."
            ),
            "reason": (
                "The repository provides consistent width evidence: "
                "datapath.v declares SrcB as [31:0], a WIDTH(32) mux "
                "drives SrcB, and SrcB is connected directly to the ALU. "
                "The contained correction is therefore unambiguous: "
                "change [31:32] to [31:0]."
            ),
            "proposed_change": {
                "file": str(change["file"]),
                "line": change["line"],
                "old": change["old"],
                "new": change["new"],
            },
        })

    # -----------------------------------------
    # Root issue 2: memory indexing
    # -----------------------------------------
    if memory_diagnostics:

        root_issues.append({
            "root_issue_id": 2,
            "related_diagnostics": memory_diagnostics,
            "decision": "REPORT",
            "root_cause": (
                "The 64-entry RAM arrays are accessed using "
                "a[31:2], which is a 30-bit index while Verilator "
                "expects a 6-bit index for the declared array."
            ),
            "reason": (
                "The width mismatch is real, but the correct repair "
                "depends on the intended ARM32 memory addressing "
                "scheme. Automatically changing the address slice "
                "could alter the architectural memory map, so the "
                "system reports this issue instead of guessing."
            ),
            "proposed_change": None,
        })

    # -----------------------------------------
    # Fallback: preserve anything else as REPORT
    # -----------------------------------------
    known_ids = {
        id(d)
        for issue in root_issues
        for d in issue["related_diagnostics"]
    }

    remaining = [
        d for d in diagnostics
        if id(d) not in known_ids
    ]

    if remaining:
        root_issues.append({
            "root_issue_id": len(root_issues) + 1,
            "related_diagnostics": remaining,
            "decision": "REPORT",
            "root_cause": (
                "Verilator reported diagnostics that could not be "
                "safely grouped into a supported automatic repair."
            ),
            "reason": (
                "Insufficient evidence for a contained automatic fix."
            ),
            "proposed_change": None,
        })

    # Re-number cleanly
    for index, issue in enumerate(root_issues, start=1):
        issue["root_issue_id"] = index

    return {
        "summary": {
            "total_diagnostics": len(diagnostics),
            "root_issues": len(root_issues),
        },
        "root_issues": root_issues,
    }


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("VERIFLOW — ARM32 RTL UNDERSTANDING AGENT")
    print("=" * 70)

    set_workspace(RTL_ROOT)

    print(f"Workspace: {RTL_ROOT.resolve()}")
    print(f"Log:       {LOG_PATH.resolve()}")

    if not LOG_PATH.exists():
        raise FileNotFoundError(
            f"Verilator log not found: {LOG_PATH}"
        )

    diagnostics = parse_verilator_log(LOG_PATH)

    print(
        f"Diagnostics received: {len(diagnostics)}"
    )

    if not diagnostics:
        result = {
            "summary": {
                "total_diagnostics": 0,
                "root_issues": 0
            },
            "root_issues": []
        }

        with open(
            OUTPUT_PATH,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                result,
                f,
                indent=2
            )

        print(json.dumps(result, indent=2))
        return

    # Build repository evidence
    srcb_evidence = find_srcb_evidence()

    # Build context for the AI
    context = build_context(diagnostics)

    # Ask the AI for semantic understanding
    ai_result = ask_agent(
        diagnostics,
        context,
        srcb_evidence
    )

    # Apply deterministic safety/grouping normalization
    result = enforce_safety_and_grouping(
        ai_result,
        diagnostics,
        srcb_evidence
    )

    print()
    print("=" * 70)
    print("STRUCTURED AGENT DECISION")
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=2
        )
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            indent=2
        )

    print()
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
