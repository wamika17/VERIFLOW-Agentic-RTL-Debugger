import os
import shutil
from pathlib import Path

RTL_ROOT = Path(
    os.getenv(
        "VERIFLOW_RTL_ROOT",
        "arm32_workspace/Verilog Files"
    )
).resolve()

BACKUP_ROOT = (
    RTL_ROOT.parent /
    ".veriflow_backups"
)


def normalize(path):

    path = str(path).replace(
        "\\",
        "/"
    )

    if "Verilog Files/" in path:

        path = path.split(
            "Verilog Files/",
            1
        )[1]

    return path


def apply_approved_change(change):

    if not change:
        return {
            "success": False,
            "message": "No proposed change."
        }

    required = [
        "file",
        "line",
        "old",
        "new"
    ]

    if not all(
        key in change
        for key in required
    ):

        return {
            "success": False,
            "message": "Incomplete proposed change."
        }

    relative = normalize(
        change["file"]
    )

    target = (
        RTL_ROOT / relative
    ).resolve()

    try:
        target.relative_to(
            RTL_ROOT
        )
    except ValueError:

        return {
            "success": False,
            "message": "Target outside RTL workspace."
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

        lines = f.readlines()

    line = int(
        change["line"]
    )

    if line < 1 or line > len(lines):

        return {
            "success": False,
            "message": "Invalid line number."
        }

    actual = lines[
        line - 1
    ]

    old = change["old"]

    if actual.count(old) != 1:

        return {
            "success": False,
            "message": (
                "Exact old text was not found "
                "exactly once."
            )
        }

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    backup = (
        BACKUP_ROOT /
        target.name
    )

    shutil.copy2(
        target,
        backup
    )

    lines[line - 1] = actual.replace(
        old,
        change["new"],
        1
    )

    with open(
        target,
        "w",
        encoding="utf-8"
    ) as f:

        f.writelines(lines)

    return {
        "success": True,
        "file": relative,
        "line": line,
        "old": old,
        "new": change["new"],
        "backup": str(backup)
    }
