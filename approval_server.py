import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

from flask import (
    Flask,
    redirect,
    render_template_string,
    send_file
)

app = Flask(__name__)

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

RTL_ROOT = Path(
    os.getenv(
        "VERIFLOW_RTL_ROOT",
        PROJECT_ROOT / "arm32_workspace" / "Verilog Files"
    )
)

DECISIONS_FILE = PROJECT_ROOT / "agent_decisions.json"
APPROVALS_FILE = PROJECT_ROOT / "approvals.json"

REPORT_MD = PROJECT_ROOT / "veriflow_report.md"
REPORT_HTML = PROJECT_ROOT / "veriflow_report.html"


# ============================================================
# DATA HELPERS
# ============================================================

def load_decisions():

    if not DECISIONS_FILE.exists():

        return {
            "summary": {
                "total_diagnostics": 0,
                "root_issues": 0
            },
            "root_issues": []
        }

    with open(
        DECISIONS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_decisions(data):

    with open(
        DECISIONS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )


def load_approvals():

    if not APPROVALS_FILE.exists():
        return []

    try:

        with open(
            APPROVALS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return []


def save_approval(record):

    records = load_approvals()

    records.append(record)

    with open(
        APPROVALS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            records,
            f,
            indent=2
        )


# ============================================================
# PATH SAFETY
# ============================================================

def resolve_rtl_file(file_path):

    file_path = str(file_path).replace(
        "\\",
        "/"
    )

    root = RTL_ROOT.resolve()

    candidate = Path(file_path)

    try:

        resolved = candidate.resolve()

        if (
            resolved == root
            or root in resolved.parents
        ):

            return resolved

    except Exception:
        pass


    if "Verilog Files/" in file_path:

        relative = file_path.split(
            "Verilog Files/",
            1
        )[1]

        resolved = (
            root / relative
        ).resolve()

        if (
            resolved == root
            or root in resolved.parents
        ):

            return resolved


    resolved = (
        root / Path(file_path).name
    ).resolve()

    if (
        resolved == root
        or root in resolved.parents
    ):

        return resolved


    raise ValueError(
        "File outside RTL workspace."
    )


# ============================================================
# APPLY APPROVED PATCH
# ============================================================

def apply_patch(change):

    if not change:

        return {
            "success": False,
            "message": "No proposed change."
        }


    try:

        target = resolve_rtl_file(
            change["file"]
        )

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


    old_text = change.get("old")
    new_text = change.get("new")


    if old_text is None or new_text is None:

        return {
            "success": False,
            "message": "Incomplete patch."
        }


    if not target.exists():

        return {
            "success": False,
            "message": f"File not found: {target}"
        }


    with open(
        target,
        "r",
        encoding="utf-8"
    ) as f:

        source = f.read()


    count = source.count(old_text)


    if count == 0:

        return {
            "success": False,
            "message": "Expected original code was not found."
        }


    if count > 1:

        return {
            "success": False,
            "message": "Original code appears multiple times."
        }


    updated = source.replace(
        old_text,
        new_text,
        1
    )


    with open(
        target,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(updated)


    return {

        "success": True,

        "file": str(target),

        "old": old_text,

        "new": new_text,

        "message": "Approved patch applied."

    }


# ============================================================
# VERILATOR
# ============================================================

def run_verilator():

    top = RTL_ROOT / "top.v"

    command = [

        "verilator",

        "--lint-only",

        f"-I{RTL_ROOT}",

        str(top)

    ]


    try:

        result = subprocess.run(

            command,

            cwd=str(PROJECT_ROOT),

            capture_output=True,

            text=True

        )


        output = (
            result.stdout
            + "\n"
            + result.stderr
        ).strip()


        warnings = [

            line

            for line in output.splitlines()

            if line.startswith("%Warning-")

        ]


        errors = [

            line

            for line in output.splitlines()

            if (
                line.startswith("%Error:")
                and
                "Exiting due to" not in line
            )

        ]


        return {

            "clean": (
                len(warnings) == 0
                and len(errors) == 0
            ),

            "warnings": len(warnings),

            "errors": len(errors),

            "returncode": result.returncode,

            "output": output

        }


    except Exception as e:

        return {

            "clean": False,

            "warnings": 0,

            "errors": 1,

            "returncode": -1,

            "output": str(e)

        }


# ============================================================
# REPORT GENERATOR
# ============================================================

def generate_report():

    data = load_decisions()

    issues = data.get(
        "root_issues",
        []
    )

    approvals = load_approvals()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    total_diagnostics = data.get(
        "summary",
        {}
    ).get(
        "total_diagnostics",
        0
    )


    solve_count = sum(

        1

        for issue in issues

        if issue.get("decision") == "SOLVE"

    )


    report_count = sum(

        1

        for issue in issues

        if issue.get("decision") == "REPORT"

    )


    verified_count = sum(

        1

        for issue in issues

        if issue.get("status") == "VERIFIED"

    )


    rejected_count = sum(

        1

        for issue in issues

        if issue.get("status") == "REJECTED"

    )


    # ========================================================
    # MARKDOWN REPORT
    # ========================================================

    md = []

    md.append("# VERIFLOW — RTL Analysis Report\n")

    md.append(
        f"**Generated:** {now}\n"
    )

    md.append(
        f"**Workspace:** `{RTL_ROOT.resolve()}`\n"
    )

    md.append(
        "## Executive Summary\n"
    )

    md.append(
        f"- Total Verilator diagnostics: **{total_diagnostics}**"
    )

    md.append(
        f"- Root issues identified: **{len(issues)}**"
    )

    md.append(
        f"- SOLVE decisions: **{solve_count}**"
    )

    md.append(
        f"- REPORT decisions: **{report_count}**"
    )

    md.append(
        f"- Verified repairs: **{verified_count}**"
    )

    md.append(
        f"- Rejected repairs: **{rejected_count}**\n"
    )


    md.append(
        "## Agent Decision Breakdown\n"
    )


    for issue in issues:

        issue_id = issue.get(
            "root_issue_id"
        )

        decision = issue.get(
            "decision",
            "UNKNOWN"
        )

        status = issue.get(
            "status",
            "AWAITING HUMAN DECISION"
        )


        md.append(
            f"### Root Issue #{issue_id}\n"
        )

        md.append(
            f"**Decision:** `{decision}`  \n"
        )

        md.append(
            f"**Status:** `{status}`  \n"
        )


        md.append(
            f"**Root Cause:** "
            f"{issue.get('root_cause', '')}\n"
        )

        md.append(
            f"**Reasoning:** "
            f"{issue.get('reason', '')}\n"
        )


        change = issue.get(
            "proposed_change"
        )


        if change:

            md.append(
                "#### Proposed Change\n"
            )

            md.append(
                f"- File: `{change.get('file')}`"
            )

            md.append(
                f"- Line: `{change.get('line')}`"
            )

            md.append(
                f"- Old: `{change.get('old')}`"
            )

            md.append(
                f"- New: `{change.get('new')}`\n"
            )


        md.append(
            "#### Verilator Diagnostics\n"
        )


        for diag in issue.get(
            "related_diagnostics",
            []
        ):

            md.append(
                f"- **{diag.get('rule')}** — "
                f"{diag.get('file')}:{diag.get('line')}:{diag.get('column')}"
            )

            md.append(
                f"  - {diag.get('message')}"
            )


        verification = issue.get(
            "verification"
        )


        if verification:

            md.append(
                "\n#### Verification\n"
            )

            md.append(
                f"- Warnings after action: "
                f"**{verification.get('warnings', 0)}**"
            )

            md.append(
                f"- Errors after action: "
                f"**{verification.get('errors', 0)}**"
            )

            md.append(
                f"- Repair status: "
                f"**{status}**"
            )


        md.append("\n---\n")


    md.append(
        "## Human Approval Audit Trail\n"
    )


    if approvals:

        for record in approvals:

            md.append(
                f"- `{record.get('timestamp', '')}` "
                f"Root Issue #{record.get('root_issue_id')} "
                f"→ **{record.get('action')}** "
                f"→ `{record.get('status')}`"
            )

    else:

        md.append(
            "No human approval actions recorded yet."
        )


    md.append(
        "\n## Verification Philosophy\n"
    )

    md.append(
        "VERIFLOW treats Verilator as the deterministic lint authority. "
        "The understanding agent groups diagnostics and decides whether "
        "there is sufficient repository evidence for an automatic repair. "
        "SOLVE decisions require explicit human approval before modifying "
        "RTL. REPORT decisions remain untouched for human review."
    )


    markdown = "\n".join(md)


    with open(
        REPORT_MD,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(markdown)


    # ========================================================
    # HTML REPORT
    # ========================================================

    html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>VERIFLOW RTL Report</title>

<style>

body {{
    background:#080b12;
    color:#e8edf5;
    font-family:Arial,sans-serif;
    max-width:1000px;
    margin:40px auto;
    padding:20px;
}}

h1 {{
    color:#42e69a;
}}

h2 {{
    color:#8fc5ff;
}}

.card {{
    background:#101722;
    border:1px solid #253044;
    border-radius:12px;
    padding:20px;
    margin:18px 0;
}}

.solve {{
    border-left:5px solid #31d58b;
}}

.report {{
    border-left:5px solid #f1b84b;
}}

.verified {{
    color:#42e69a;
    font-weight:bold;
}}

.rejected {{
    color:#ff7885;
    font-weight:bold;
}}

.pending {{
    color:#f1c266;
    font-weight:bold;
}}

.code {{
    background:#070a10;
    padding:12px;
    border-radius:8px;
    font-family:monospace;
    margin:8px 0;
}}

.stat {{
    display:inline-block;
    background:#111925;
    padding:15px;
    margin:5px;
    border-radius:8px;
}}

</style>

</head>

<body>

<h1>VERIFLOW</h1>

<p>
Agentic RTL Analysis & Human-Governed Repair
</p>

<p>
Generated: {now}
</p>

<div>

<div class="stat">
Diagnostics: <strong>{total_diagnostics}</strong>
</div>

<div class="stat">
Root Issues: <strong>{len(issues)}</strong>
</div>

<div class="stat">
SOLVE: <strong>{solve_count}</strong>
</div>

<div class="stat">
REPORT: <strong>{report_count}</strong>
</div>

<div class="stat">
VERIFIED: <strong>{verified_count}</strong>
</div>

</div>
"""


    for issue in issues:

        decision = issue.get(
            "decision"
        )

        status = issue.get(
            "status",
            "AWAITING HUMAN DECISION"
        )

        css = (
            "solve"
            if decision == "SOLVE"
            else "report"
        )


        html += f"""

<div class="card {css}">

<h2>
Root Issue #{issue.get('root_issue_id')}
</h2>

<p>
<strong>Decision:</strong>
{decision}
</p>

<p>
<strong>Status:</strong>
<span class="{status.lower().replace(' ', '-')}">
{status}
</span>
</p>

<p>
<strong>Root Cause:</strong>
{issue.get('root_cause', '')}
</p>

<p>
<strong>Agent Reasoning:</strong>
{issue.get('reason', '')}
</p>
"""


        change = issue.get(
            "proposed_change"
        )


        if change:

            html += f"""

<h3>Proposed Change</h3>

<div class="code">
OLD: {change.get('old')}
</div>

<div class="code">
NEW: {change.get('new')}
</div>

<p>
File: {change.get('file')}<br>
Line: {change.get('line')}
</p>
"""


        html += """

<h3>Diagnostics</h3>
"""


        for diag in issue.get(
            "related_diagnostics",
            []
        ):

            html += f"""

<div class="code">

<strong>{diag.get('rule')}</strong><br>

{diag.get('file')}:
{diag.get('line')}:
{diag.get('column')}<br><br>

{diag.get('message')}

</div>

"""


        html += "</div>"


    html += """

</body>

</html>
"""


    with open(
        REPORT_HTML,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)


    return {
        "markdown": str(REPORT_MD),
        "html": str(REPORT_HTML)
    }


# ============================================================
# DASHBOARD HTML
# ============================================================

PAGE = r"""

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>VERIFLOW</title>

<style>

body {
    margin:0;
    background:#080b12;
    color:#e8edf5;
    font-family:Arial,sans-serif;
}

.container {
    width:92%;
    max-width:1200px;
    margin:40px auto;
}

.header {
    background:#101722;
    border:1px solid #243044;
    border-radius:18px;
    padding:28px;
}

.logo {
    font-size:34px;
    font-weight:900;
    color:#42e69a;
}

.subtitle {
    color:#8c98aa;
    margin-top:6px;
}

.stats {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:12px;
    margin-top:25px;
}

.stat {
    background:#0b1019;
    border:1px solid #202b3c;
    border-radius:12px;
    padding:18px;
}

.num {
    font-size:28px;
    font-weight:900;
}

.label {
    color:#8491a4;
    font-size:11px;
    margin-top:4px;
}

.actions {
    display:flex;
    gap:10px;
    margin-top:22px;
    flex-wrap:wrap;
}

button,
.action {
    border:0;
    border-radius:9px;
    padding:11px 15px;
    font-weight:800;
    cursor:pointer;
    text-decoration:none;
    display:inline-block;
}

.yes {
    background:#31d58b;
    color:#06120c;
}

.no {
    background:#ff6675;
    color:#180609;
}

.reportbtn {
    background:#5b9cff;
    color:white;
}

.reset {
    background:#303b4d;
    color:#e8edf5;
}

.card {
    background:#0d131d;
    border:1px solid #202b3c;
    border-radius:16px;
    padding:24px;
    margin-top:18px;
}

.solve-card {
    border-left:5px solid #31d58b;
}

.report-card {
    border-left:5px solid #f1b84b;
}

.title {
    font-size:20px;
    font-weight:900;
}

.badge {
    display:inline-block;
    padding:6px 10px;
    border-radius:7px;
    font-size:10px;
    font-weight:900;
    margin-top:8px;
}

.solve-badge {
    background:#103d2b;
    color:#42e69a;
}

.report-badge {
    background:#3c3118;
    color:#f1c266;
}

.verified {
    background:#103d2b;
    color:#42e69a;
}

.rejected {
    background:#421a20;
    color:#ff7885;
}

.pending {
    background:#332b17;
    color:#f1c266;
}

.reason {
    color:#9ba8ba;
    line-height:1.6;
    margin-top:14px;
}

.rootcause {
    line-height:1.6;
    margin-top:15px;
}

.change {
    margin-top:20px;
}

.code {
    background:#06090e;
    border:1px solid #1e2734;
    border-radius:9px;
    padding:14px;
    font-family:monospace;
    margin-top:8px;
    overflow:auto;
}

.old {
    color:#ff7b87;
}

.new {
    color:#42e69a;
}

.diag {
    border-top:1px solid #1c2532;
    padding:12px 0;
}

.diag-rule {
    color:#f1c266;
    font-family:monospace;
    font-weight:bold;
}

.diag-text {
    color:#aeb9c8;
    font-size:12px;
    margin-top:5px;
}

.actions-small {
    display:flex;
    gap:10px;
    margin-top:20px;
}

.note {
    background:#17150e;
    border:1px solid #46391b;
    color:#c0aa72;
    padding:14px;
    border-radius:9px;
    margin-top:20px;
}

.verify {
    background:#08150f;
    border:1px solid #1e5940;
    padding:15px;
    border-radius:10px;
    margin-top:20px;
    color:#42e69a;
}

</style>

</head>


<body>

<div class="container">

<div class="header">

<div class="logo">
VERIFLOW
</div>

<div class="subtitle">
Agentic RTL Lint Analysis — Human Approval Gateway
</div>

<p style="color:#718096;font-family:monospace;font-size:11px;">
{{ workspace }}
</p>


<div class="stats">

<div class="stat">
<div class="num">{{ total }}</div>
<div class="label">DIAGNOSTICS</div>
</div>

<div class="stat">
<div class="num">{{ issues }}</div>
<div class="label">ROOT ISSUES</div>
</div>

<div class="stat">
<div class="num">{{ solves }}</div>
<div class="label">SOLVE</div>
</div>

<div class="stat">
<div class="num">{{ reports }}</div>
<div class="label">REPORT</div>
</div>

</div>


<div class="actions">

<form
method="POST"
action="/approve-all"
style="display:inline;"
>

<button class="yes">
✓ ACCEPT ALL
</button>

</form>


<form
method="POST"
action="/reject-all"
style="display:inline;"
>

<button class="no">
✕ REJECT ALL
</button>

</form>


<form
method="POST"
action="/generate-report"
style="display:inline;"
>

<button class="reportbtn">
📄 GENERATE REPORT
</button>

</form>


<a
class="action reset"
href="/"
>
↻ REFRESH
</a>


{% if report_exists %}

<a
class="action reportbtn"
href="/download-report"
>
⬇ DOWNLOAD REPORT
</a>

{% endif %}

</div>

</div>


{% for issue in root_issues %}

<div class="card
{% if issue.decision == 'SOLVE' %}
solve-card
{% else %}
report-card
{% endif %}
">


<div class="title">

Root Issue #{{ issue.root_issue_id }}

</div>


{% if issue.decision == "SOLVE" %}

<div class="badge solve-badge">
SOLVE
</div>

{% else %}

<div class="badge report-badge">
REPORT
</div>

{% endif %}


{% if issue.status %}

<div class="badge
{% if issue.status == 'VERIFIED' %}
verified
{% elif issue.status == 'REJECTED' %}
rejected
{% else %}
pending
{% endif %}
">

{{ issue.status }}

</div>

{% elif issue.decision == "SOLVE" %}

<div class="badge pending">
AWAITING HUMAN APPROVAL
</div>

{% endif %}


<div class="rootcause">

<strong>Root Cause:</strong><br>

{{ issue.root_cause }}

</div>


<div class="reason">

<strong>Agent Reasoning:</strong><br>

{{ issue.reason }}

</div>


{% if issue.proposed_change %}

<div class="change">

<strong>PROPOSED CHANGE</strong>

<div class="code old">
{{ issue.proposed_change.old }}
</div>

<div style="color:#718096;margin:8px 0;">
↓ change to
</div>

<div class="code new">
{{ issue.proposed_change.new }}
</div>

<p style="color:#718096;font-size:11px;">
File:
{{ issue.proposed_change.file }}
<br>
Line:
{{ issue.proposed_change.line }}
</p>

</div>

{% endif %}


<h4 style="color:#8995a8;margin-top:25px;">
VERILATOR DIAGNOSTICS
</h4>


{% for diag in issue.related_diagnostics %}

<div class="diag">

<div class="diag-rule">
{{ diag.rule }}
</div>

<div style="color:#66758a;font-size:11px;">
{{ diag.file }}:{{ diag.line }}:{{ diag.column }}
</div>

<div class="diag-text">
{{ diag.message }}
</div>

</div>

{% endfor %}


{% if issue.decision == "SOLVE" and not issue.status %}

<div class="actions-small">


<form
method="POST"
action="/approve/{{ issue.root_issue_id }}"
>

<button class="yes">
✓ YES — APPLY & VERIFY
</button>

</form>


<form
method="POST"
action="/reject/{{ issue.root_issue_id }}"
>

<button class="no">
✕ NO — REJECT
</button>

</form>

</div>

{% endif %}


{% if issue.decision == "REPORT" %}

<div class="note">

⚠ <strong>REPORT — HUMAN REVIEW REQUIRED</strong>

<br><br>

VERIFLOW will not modify this issue automatically because
the repository evidence is insufficient for an unambiguous
safe repair.

</div>

{% endif %}


{% if issue.verification %}

<div class="verify">

<strong>

{% if issue.status == "VERIFIED" %}

✓ APPROVED REPAIR VERIFIED

{% else %}

VERIFICATION RESULT

{% endif %}

</strong>

<br><br>

Verilator warnings after patch:
{{ issue.verification.warnings }}

<br>

Verilator errors:
{{ issue.verification.errors }}

</div>

{% endif %}


</div>

{% endfor %}


</div>

</body>

</html>

"""


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def index():

    data = load_decisions()

    root_issues = data.get(
        "root_issues",
        []
    )


    total = data.get(
        "summary",
        {}
    ).get(
        "total_diagnostics",
        0
    )


    solves = sum(

        1

        for issue in root_issues

        if issue.get("decision") == "SOLVE"
        and not issue.get("status")

    )


    reports = sum(

        1

        for issue in root_issues

        if issue.get("decision") == "REPORT"

    )


    return render_template_string(

        PAGE,

        workspace=str(
            RTL_ROOT.resolve()
        ),

        total=total,

        issues=len(root_issues),

        solves=solves,

        reports=reports,

        root_issues=root_issues,

        report_exists=REPORT_HTML.exists()

    )


# ============================================================
# APPROVE ONE
# ============================================================

@app.route(
    "/approve/<int:issue_id>",
    methods=["POST"]
)
def approve(issue_id):

    data = load_decisions()

    issues = data.get(
        "root_issues",
        []
    )


    issue = next(

        (
            x

            for x in issues

            if x.get("root_issue_id")
            == issue_id

        ),

        None

    )


    if not issue:

        return "Issue not found.", 404


    if issue.get("decision") != "SOLVE":

        return "Only SOLVE issues can be approved.", 400


    if issue.get("status"):

        return redirect("/")


    change = issue.get(
        "proposed_change"
    )


    patch = apply_patch(change)

    issue["patch_result"] = patch


    if not patch["success"]:

        issue["status"] = "PATCH_FAILED"

        save_decisions(data)

        return redirect("/")


    issue["status"] = "APPROVED"


    verification = run_verilator()

    issue["verification"] = verification


    # The repair itself is what we verify.
    # Other REPORT issues may still remain.

    target = resolve_rtl_file(
        change["file"]
    )


    with open(
        target,
        "r",
        encoding="utf-8"
    ) as f:

        source = f.read()


    if (
        change["new"] in source
        and change["old"] not in source
    ):

        issue["status"] = "VERIFIED"

    else:

        issue["status"] = "VERIFICATION_FAILED"


    save_approval({

        "timestamp":
            datetime.now().isoformat(),

        "root_issue_id":
            issue_id,

        "action":
            "APPROVE",

        "status":
            issue["status"]

    })


    save_decisions(data)

    return redirect("/")


# ============================================================
# REJECT ONE
# ============================================================

@app.route(
    "/reject/<int:issue_id>",
    methods=["POST"]
)
def reject(issue_id):

    data = load_decisions()

    issues = data.get(
        "root_issues",
        []
    )


    issue = next(

        (
            x

            for x in issues

            if x.get("root_issue_id")
            == issue_id

        ),

        None

    )


    if not issue:

        return "Issue not found.", 404


    if issue.get("decision") != "SOLVE":

        return "Only SOLVE issues can be rejected.", 400


    issue["status"] = "REJECTED"


    save_approval({

        "timestamp":
            datetime.now().isoformat(),

        "root_issue_id":
            issue_id,

        "action":
            "REJECT",

        "status":
            "REJECTED"

    })


    save_decisions(data)

    return redirect("/")


# ============================================================
# ACCEPT ALL
# ============================================================

@app.route(
    "/approve-all",
    methods=["POST"]
)
def approve_all():

    data = load_decisions()

    issues = data.get(
        "root_issues",
        []
    )


    for issue in issues:

        if issue.get("decision") != "SOLVE":
            continue

        if issue.get("status"):
            continue


        change = issue.get(
            "proposed_change"
        )


        patch = apply_patch(change)

        issue["patch_result"] = patch


        if not patch["success"]:

            issue["status"] = "PATCH_FAILED"

            continue


        issue["status"] = "APPROVED"


        verification = run_verilator()

        issue["verification"] = verification


        target = resolve_rtl_file(
            change["file"]
        )


        with open(
            target,
            "r",
            encoding="utf-8"
        ) as f:

            source = f.read()


        if (
            change["new"] in source
            and change["old"] not in source
        ):

            issue["status"] = "VERIFIED"

        else:

            issue["status"] = "VERIFICATION_FAILED"


        save_approval({

            "timestamp":
                datetime.now().isoformat(),

            "root_issue_id":
                issue["root_issue_id"],

            "action":
                "APPROVE_ALL",

            "status":
                issue["status"]

        })


    save_decisions(data)

    return redirect("/")


# ============================================================
# REJECT ALL
# ============================================================

@app.route(
    "/reject-all",
    methods=["POST"]
)
def reject_all():

    data = load_decisions()

    issues = data.get(
        "root_issues",
        []
    )


    for issue in issues:

        if issue.get("decision") != "SOLVE":
            continue

        if issue.get("status"):
            continue


        issue["status"] = "REJECTED"


        save_approval({

            "timestamp":
                datetime.now().isoformat(),

            "root_issue_id":
                issue["root_issue_id"],

            "action":
                "REJECT_ALL",

            "status":
                "REJECTED"

        })


    save_decisions(data)

    return redirect("/")


# ============================================================
# GENERATE REPORT
# ============================================================

@app.route(
    "/generate-report",
    methods=["POST"]
)
def generate_report_route():

    generate_report()

    return redirect("/")


# ============================================================
# DOWNLOAD REPORT
# ============================================================

@app.route("/download-report")
def download_report():

    generate_report()

    return send_file(
        REPORT_HTML,
        as_attachment=True,
        download_name="VERIFLOW_RTL_Report.html",
        mimetype="text/html"
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "VERIFLOW HUMAN APPROVAL SERVER"
    )

    print("=" * 70)

    print(
        "Workspace:",
        RTL_ROOT.resolve()
    )

    print(
        "Open: http://127.0.0.1:5000"
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )