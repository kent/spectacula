#!/usr/bin/env python3
"""Validate Spectacula against Codex skill-building best practices."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MAX_SKILL_LINES = 500
LONG_REFERENCE_LINES = 100
REQUIRED_ROOT_LINKS = [
    "references/spec-blueprint.md",
    "references/question-bank.md",
    "references/implementation-handoff.md",
    "references/spec-audit-rubric.md",
    "references/spectacula-lifecycle.md",
    "references/claude-portable-prompt.md",
    "scripts/spectacula",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Spectacula skill packaging and progressive-disclosure hygiene."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Spectacula repository root. Defaults to the current working directory.",
    )
    return parser.parse_args(argv)


def read_text(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing required file: {path}") from exc


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = read_text(path)
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "missing opening frontmatter delimiter"
    try:
        end_index = lines[1:].index("---") + 1
    except ValueError:
        return {}, "missing closing frontmatter delimiter"

    values: dict[str, str] = {}
    for raw_line in lines[1:end_index]:
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            return values, f"invalid frontmatter line: {raw_line!r}"
        key, value = raw_line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values, ""


def validate_skill_file(path: Path, errors: list[str]) -> None:
    frontmatter, frontmatter_error = parse_frontmatter(path)
    label = str(path)
    if frontmatter_error:
        errors.append(f"{label}: {frontmatter_error}")
        return

    keys = set(frontmatter)
    if keys != {"name", "description"}:
        errors.append(f"{label}: frontmatter must contain only name and description, got {sorted(keys)}")
    if not frontmatter.get("name"):
        errors.append(f"{label}: frontmatter name is required")
    if not frontmatter.get("description"):
        errors.append(f"{label}: frontmatter description is required")
    if line_count(path) > MAX_SKILL_LINES:
        errors.append(f"{label}: exceeds {MAX_SKILL_LINES} lines")


def has_toc(text: str) -> bool:
    first_lines = "\n".join(text.splitlines()[:50]).lower()
    return "table of contents" in first_lines or "## contents" in first_lines


def validate_references(root: Path, errors: list[str]) -> None:
    references_dir = root / "references"
    for path in sorted(references_dir.glob("*.md")):
        count = line_count(path)
        if count > LONG_REFERENCE_LINES and not has_toc(read_text(path)):
            errors.append(
                f"{path}: reference has {count} lines and needs a table of contents near the top"
            )


def validate_root_links(root: Path, errors: list[str]) -> None:
    skill_text = read_text(root / "SKILL.md")
    for required in REQUIRED_ROOT_LINKS:
        if required not in skill_text:
            errors.append(f"SKILL.md: missing direct link or mention for {required}")


def yaml_value(text: str, key: str) -> str | None:
    pattern = re.compile(rf"^\s*{re.escape(key)}:\s*\"([^\"]*)\"\s*$", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1) if match else None


def validate_openai_yaml(root: Path, errors: list[str]) -> None:
    path = root / "agents" / "openai.yaml"
    text = read_text(path)
    display_name = yaml_value(text, "display_name")
    short_description = yaml_value(text, "short_description")
    default_prompt = yaml_value(text, "default_prompt")

    if display_name != "Spectacula":
        errors.append(f"{path}: display_name should be quoted and set to Spectacula")
    if short_description is None:
        errors.append(f"{path}: short_description must be a quoted string")
    elif not 25 <= len(short_description) <= 64:
        errors.append(f"{path}: short_description must be 25-64 characters")
    if default_prompt is None:
        errors.append(f"{path}: default_prompt must be a quoted string")
    elif "$spectacula" not in default_prompt:
        errors.append(f"{path}: default_prompt must explicitly mention $spectacula")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    validate_skill_file(root / "SKILL.md", errors)
    validate_skill_file(root / "skills" / "spectacula" / "SKILL.md", errors)
    validate_references(root, errors)
    validate_root_links(root, errors)
    validate_openai_yaml(root, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    errors = validate(root)
    if errors:
        print("Skill best-practices validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Skill best-practices validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
