"""Build a flat command reference for the root --help epilogue."""

from __future__ import annotations

import inspect
import types
from typing import Annotated, Any, Union, get_args, get_origin, get_type_hints

from cyclopts import App, Parameter

COL_WIDTH = 46
MAX_LINE = 78
MIN_DESC_WIDTH = 10
ELLIPSIS = "\u2026"


def _is_bool_type(tp: object) -> bool:
    if tp is bool:
        return True
    if tp is None:
        return False
    origin = get_origin(tp)
    if origin is Union or isinstance(tp, types.UnionType):
        return bool in get_args(tp)
    return False


def _display_len(s: str) -> int:
    """Return rendered width (Rich \\[ escapes render as single [)."""
    return len(s.replace("\\[", "["))


def _format_signature(func: Any, prefix_len: int, col_width: int) -> str:
    sig = inspect.signature(func)
    try:
        hints = get_type_hints(func, include_extras=True)
    except (TypeError, NameError):
        hints = {}

    required: list[str] = []
    optional: list[str] = []
    for pname, param in sig.parameters.items():
        hint = hints.get(pname)

        cli_param = None
        base_type = hint
        if hint is not None and get_origin(hint) is Annotated:
            args = get_args(hint)
            base_type = args[0]
            for arg in args[1:]:
                if isinstance(arg, Parameter):
                    cli_param = arg
                    break

        is_bool = _is_bool_type(base_type)
        has_default = param.default is not inspect.Parameter.empty

        if param.kind == param.KEYWORD_ONLY:
            if cli_param and cli_param.name:
                names = cli_param.name if isinstance(cli_param.name, (list, tuple)) else [cli_param.name]
                cli_name = names[0]
            else:
                cli_name = f"--{pname.replace('_', '-')}"

            if has_default:
                optional.append(f"\\[{cli_name}]")
            elif is_bool:
                required.append(cli_name)
            else:
                required.append(f"{cli_name} {pname.upper()}")
        elif param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
            label = pname.upper()
            if has_default:
                optional.append(f"\\[{label}]")
            else:
                required.append(label)

    max_sig = col_width - prefix_len - 2
    parts = required + optional
    result = " ".join(parts)
    while len(result) > max_sig and optional:
        optional.pop()
        parts = required + optional + ["..."]
        result = " ".join(parts)

    return result


def build_command_reference(sub_apps: list[App]) -> str:
    """Walk sub-apps and build a formatted "All Commands" block."""
    entries: list[tuple[str, str]] = []
    for sub in sub_apps:
        sub_name = sub.name[0] if sub.name else "?"
        for cmd_name, cmd_app in sub.resolved_commands().items():
            if cmd_name.startswith("-"):
                continue
            func = cmd_app.default_command
            if func is None:
                continue
            prefix = f"  {sub_name} {cmd_name} "
            sig_str = _format_signature(func, prefix_len=len(prefix), col_width=COL_WIDTH)
            doc = (func.__doc__ or "").strip().split("\n")[0]
            left = f"  {sub_name} {cmd_name}"
            if sig_str:
                left += f" {sig_str}"
            entries.append((left, doc))
        entries.append(("", ""))

    if entries and entries[-1] == ("", ""):
        entries.pop()

    lines = ["All Commands:\n"]
    for left, doc in entries:
        if not left:
            lines.append("")
        else:
            display_w = _display_len(left)
            pad = max(2, COL_WIDTH - display_w)
            avail = MAX_LINE - display_w - pad
            if len(doc) > avail > MIN_DESC_WIDTH:
                doc = doc[: avail - 1] + ELLIPSIS
            lines.append(f"{left}{' ' * pad}{doc}")
    return "\n".join(lines)
