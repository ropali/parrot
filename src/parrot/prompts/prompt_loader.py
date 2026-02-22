from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping

_PLACEHOLDER_RE = re.compile(r"\{([A-Z0-9_]+)\}")


def _resolve_prompt_path(name: str, prompt_dir: Path | None) -> Path:
    base_dir = prompt_dir or Path(__file__).resolve().parent
    path = Path(name)

    if path.suffix != ".md":
        path = path.with_suffix(".md")

    if not path.is_absolute():
        path = base_dir / path

    return path


def load_prompt(
    name: str,
    replacements: Mapping[str, object] | None = None,
    *,
    prompt_dir: Path | None = None,
    strict: bool = True,
) -> str:
    """
    Load a markdown prompt and replace {PLACEHOLDER} tokens.

    Args:
        name: Prompt filename (with or without .md) or path.
        replacements: Mapping of placeholder name to value.
        prompt_dir: Base directory for relative prompt paths.
        strict: Raise if any placeholders are missing.

    Returns:
        Rendered prompt string.
    """
    path = _resolve_prompt_path(name, prompt_dir)
    template = path.read_text(encoding="utf-8")

    if not replacements:
        if strict:
            missing = sorted(set(_PLACEHOLDER_RE.findall(template)))
            if missing:
                raise KeyError(f"Missing replacements for: {', '.join(missing)}")
        return template

    replacement_text = {key: str(value) for key, value in replacements.items()}
    missing: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in replacement_text:
            return replacement_text[key]
        missing.add(key)
        return match.group(0)

    rendered = _PLACEHOLDER_RE.sub(replace, template)

    if strict and missing:
        raise KeyError(f"Missing replacements for: {', '.join(sorted(missing))}")

    return rendered
