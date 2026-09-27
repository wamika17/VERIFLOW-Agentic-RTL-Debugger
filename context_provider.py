from pathlib import Path
import re

# Default RTL workspace
RTL_ROOT = Path("arm32_workspace/Verilog Files").resolve()


def set_workspace(workspace_path):
    global RTL_ROOT
    RTL_ROOT = Path(workspace_path).resolve()


def resolve_rtl_file(file_path, search_root=None):
    """
    Resolve a Verilator-reported file path to the actual RTL file.

    Handles:
      - absolute paths
      - paths relative to project root
      - paths relative to RTL root
      - plain filenames such as alu.v
    """

    if search_root is None:
        search_root = RTL_ROOT

    search_root = Path(search_root).resolve()
    file_path = Path(str(file_path).strip()).expanduser()

    # 1. Absolute path that already exists
    if file_path.is_absolute() and file_path.exists():
        return file_path.resolve()

    # 2. Path relative to current working directory
    candidate = Path.cwd() / file_path
    if candidate.exists():
        return candidate.resolve()

    # 3. Path relative to RTL root
    candidate = search_root / file_path
    if candidate.exists():
        return candidate.resolve()

    # 4. If Verilator gave something like:
    #    arm32_workspace/Verilog Files/alu.v
    #    try matching from the RTL root using the filename.
    candidate = search_root / file_path.name
    if candidate.exists():
        return candidate.resolve()

    # 5. Last-resort search inside RTL workspace.
    #    This keeps the system robust to different Verilator path formats.
    matches = list(search_root.rglob(file_path.name))

    if len(matches) == 1:
        return matches[0].resolve()

    if len(matches) > 1:
        # Prefer an exact suffix match.
        normalized = str(file_path).replace("\\", "/")

        for match in matches:
            match_str = str(match).replace("\\", "/")
            if match_str.endswith(normalized):
                return match.resolve()

        return matches[0].resolve()

    raise FileNotFoundError(
        f"Could not resolve RTL file '{file_path}'. "
        f"Searched from RTL root: '{search_root}'"
    )


def read_file(file_path):
    resolved_path = resolve_rtl_file(file_path)

    with open(resolved_path, "r", encoding="utf-8") as f:
        return f.readlines()


def get_source_context(file_path, line_number, context_lines=5):
    resolved_path = resolve_rtl_file(file_path)

    lines = read_file(resolved_path)

    start = max(0, line_number - 1 - context_lines)
    end = min(len(lines), line_number + context_lines)

    context = []

    for index in range(start, end):
        context.append({
            "line": index + 1,
            "code": lines[index].rstrip()
        })

    return context


def find_signal_declaration(signal_name, search_root=None):
    if search_root is None:
        search_root = RTL_ROOT

    search_root = Path(search_root).resolve()

    results = []

    declaration_pattern = re.compile(
        rf"\b(?:wire|reg|logic|input|output|inout)\b[^;]*\b{re.escape(signal_name)}\b"
    )

    for file_path in search_root.glob("*.v"):
        try:
            lines = read_file(file_path)
        except Exception:
            continue

        for index, line in enumerate(lines):
            if declaration_pattern.search(line):
                results.append({
                    "file": str(file_path),
                    "line": index + 1,
                    "code": line.rstrip()
                })

    return results


def find_signal_usage(signal_name, search_root=None):
    if search_root is None:
        search_root = RTL_ROOT

    search_root = Path(search_root).resolve()

    results = []

    usage_pattern = re.compile(
        rf"\b{re.escape(signal_name)}\b"
    )

    for file_path in search_root.glob("*.v"):
        try:
            lines = read_file(file_path)
        except Exception:
            continue

        for index, line in enumerate(lines):
            if usage_pattern.search(line):
                results.append({
                    "file": str(file_path),
                    "line": index + 1,
                    "code": line.rstrip()
                })

    return results


def find_module_instances(signal_name, search_root=None):
    if search_root is None:
        search_root = RTL_ROOT

    search_root = Path(search_root).resolve()

    results = []

    pattern = re.compile(
        rf"\b{re.escape(signal_name)}\b"
    )

    for file_path in search_root.glob("*.v"):
        try:
            lines = read_file(file_path)
        except Exception:
            continue

        for index, line in enumerate(lines):
            stripped = line.strip()

            if pattern.search(stripped):
                if (
                    "(" in stripped
                    and (
                        "." in stripped
                        or re.search(
                            r"\b\w+\s+\w+\s*\(",
                            stripped
                        )
                    )
                ):
                    results.append({
                        "file": str(file_path),
                        "line": index + 1,
                        "code": stripped
                    })

    return results


def get_signal_context(signal_name, search_root=None):
    if search_root is None:
        search_root = RTL_ROOT

    return {
        "signal": signal_name,
        "declarations": find_signal_declaration(
            signal_name,
            search_root
        ),
        "usages": find_signal_usage(
            signal_name,
            search_root
        ),
        "module_connections": find_module_instances(
            signal_name,
            search_root
        )
    }