#!/usr/bin/env python3
"""Command wrapper for common Spectacula script workflows."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import bootstrap_repo
import render_review_prompt


STAGES = ("specs", "ready", "inprogress", "done")
STATUS_VALUES = {"pending", "passed", "failed", "skipped", "blocked", "partial"}
REQUIRED_FIELDS = {
    "spec_id",
    "slug",
    "title",
    "stage",
    "spec_path",
    "updated_at",
    "summary",
    "next_action",
    "resume_context",
    "history",
}
SLUG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="spectacula",
        description="Run common Spectacula workflows from a single command."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap_parser = subparsers.add_parser(
        "bootstrap",
        help="Scaffold docs/spectacula into a target repository.",
    )
    bootstrap_parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target repository root. Defaults to the current working directory.",
    )
    bootstrap_parser.add_argument(
        "--include-examples",
        action="store_true",
        help="Copy example files into docs/spectacula/examples.",
    )
    bootstrap_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing template files in the target repo.",
    )

    new_parser = subparsers.add_parser(
        "new",
        help="Create a tracked spec and draft manifest.",
    )
    new_parser.add_argument("slug", help="Filesystem-safe spec slug.")
    new_parser.add_argument("--repo", default=".", help="Repository root. Defaults to cwd.")
    new_parser.add_argument("--title", help="Human-readable spec title.")
    new_parser.add_argument(
        "--summary",
        help="Initial manifest summary and spec purpose.",
    )
    new_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing spec or manifest files.",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate docs/spectacula lifecycle integrity.",
    )
    validate_parser.add_argument("--repo", default=".", help="Repository root. Defaults to cwd.")
    validate_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. Defaults to text.",
    )

    status_parser = subparsers.add_parser(
        "status",
        help="Report tracked Spectacula status.",
    )
    status_parser.add_argument(
        "target",
        nargs="?",
        help="Optional spec slug or manifest path. Omit to list all tracked specs.",
    )
    status_parser.add_argument("--repo", default=".", help="Repository root. Defaults to cwd.")
    status_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. Defaults to text.",
    )

    move_parser = subparsers.add_parser(
        "move",
        help="Move one spec manifest to another lifecycle stage.",
    )
    move_parser.add_argument("target", help="Spec slug or manifest path.")
    move_parser.add_argument("stage", choices=STAGES, help="Target lifecycle stage.")
    move_parser.add_argument("--repo", default=".", help="Repository root. Defaults to cwd.")
    move_parser.add_argument("--summary", help="Replacement manifest summary.")
    move_parser.add_argument("--next-action", help="Replacement manifest next action.")
    move_parser.add_argument("--note", help="History note for this transition.")
    move_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow otherwise refused transitions such as incomplete done gates.",
    )

    verdict_parser = subparsers.add_parser(
        "verdict",
        help="Record a strict final-vetting verdict.",
    )
    verdict_parser.add_argument("target", help="Spec slug or manifest path.")
    verdict_parser.add_argument("verdict", choices=["passed", "failed"])
    verdict_parser.add_argument("--repo", default=".", help="Repository root. Defaults to cwd.")
    verdict_parser.add_argument("--reason", help="Short reason to append to verification notes.")

    review_parser = subparsers.add_parser(
        "review",
        help="Render Spectacula's final vetting prompt for an active spec.",
    )
    review_parser.add_argument(
        "target",
        nargs="?",
        help=(
            "Optional spec slug or manifest path. If omitted, uses the only manifest "
            "in docs/spectacula/inprogress."
        ),
    )
    review_parser.add_argument(
        "--repo",
        default=".",
        help="Repository root to review. Defaults to the current working directory.",
    )
    review_parser.add_argument(
        "--reviewer-prompt",
        help=(
            "Optional path to the reviewer prompt file. Defaults to the installed "
            "agents/spectacula-reviewer.md."
        ),
    )
    review_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. Defaults to text.",
    )

    return parser.parse_args(argv)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def spectacula_root(repo_root: Path) -> Path:
    return repo_root / "docs" / "spectacula"


def stage_dir(repo_root: Path, stage: str) -> Path:
    return spectacula_root(repo_root) / stage


def repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise SystemExit(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def load_manifest(path: Path) -> dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise SystemExit(f"Manifest must contain a JSON object: {path}")
    return data


def ensure_repo_exists(repo_root: Path) -> None:
    if not repo_root.is_dir():
        raise SystemExit(f"Repository root does not exist or is not a directory: {repo_root}")


def ensure_docs_tree(repo_root: Path) -> None:
    ensure_repo_exists(repo_root)
    root = spectacula_root(repo_root)
    if root.is_dir():
        return
    bootstrap_repo.main([str(repo_root)])


def require_docs_tree(repo_root: Path) -> None:
    ensure_repo_exists(repo_root)
    root = spectacula_root(repo_root)
    if not root.is_dir():
        raise SystemExit(
            f"No docs/spectacula tree found in {repo_root}. "
            "Run `spectacula bootstrap .` first."
        )


def manifest_paths(repo_root: Path) -> list[Path]:
    require_docs_tree(repo_root)
    paths: list[Path] = []
    for stage in STAGES:
        directory = stage_dir(repo_root, stage)
        if not directory.is_dir():
            continue
        paths.extend(sorted(path for path in directory.glob("*.json") if path.is_file()))
    return paths


def path_stage(repo_root: Path, path: Path) -> str | None:
    try:
        relative = path.resolve().relative_to(spectacula_root(repo_root).resolve())
    except ValueError:
        return None
    if len(relative.parts) < 2:
        return None
    stage = relative.parts[0]
    return stage if stage in STAGES else None


def resolve_spec_path(manifest_path: Path, manifest: dict[str, Any]) -> Path | None:
    spec_ref = manifest.get("spec_path")
    if not isinstance(spec_ref, str) or not spec_ref:
        return None
    return (manifest_path.parent / spec_ref).resolve()


def find_manifest_matches(repo_root: Path, target: str) -> list[Path]:
    raw_target = Path(target)
    if raw_target.suffix == ".json" or "/" in target or raw_target.is_absolute():
        candidate = raw_target if raw_target.is_absolute() else (repo_root / raw_target)
        return [candidate.resolve()] if candidate.is_file() else []

    return [path.resolve() for path in manifest_paths(repo_root) if path.stem == target]


def resolve_manifest(repo_root: Path, target: str, allowed_stages: tuple[str, ...] = STAGES) -> Path:
    matches = [
        path
        for path in find_manifest_matches(repo_root, target)
        if (path_stage(repo_root, path) in allowed_stages)
    ]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        allowed = ", ".join(allowed_stages)
        raise SystemExit(f"No manifest found for {target!r} in stages: {allowed}")

    choices = "\n".join(f"- {repo_relative(path, repo_root)}" for path in matches)
    raise SystemExit(f"Target {target!r} is ambiguous. Choose a manifest path:\n{choices}")


def title_from_slug(slug: str) -> str:
    words = re.split(r"[-_.]+", slug)
    return " ".join(word.capitalize() for word in words if word) + " Specification"


def default_stage_summary(stage: str) -> str:
    return {
        "specs": "Spec is in draft or revision.",
        "ready": "Spec approved and ready for implementation.",
        "inprogress": "Implementation is active.",
        "done": "Implementation completed and verified.",
    }[stage]


def default_stage_next_action(stage: str) -> str:
    return {
        "specs": "Resolve open questions and approve the spec.",
        "ready": "Move manifest to inprogress and implement the spec.",
        "inprogress": "Complete implementation, verification, and spec review.",
        "done": "No further action.",
    }[stage]


def transition_event(from_stage: str, to_stage: str) -> str:
    if to_stage == "ready":
        return "spec_approved"
    if to_stage == "inprogress":
        return "implementation_started"
    if to_stage == "done":
        return "implementation_completed"
    if to_stage == "specs":
        return "spec_reopened"
    return "stage_moved"


def append_history(
    manifest: dict[str, Any],
    *,
    event: str,
    from_stage: str | None,
    to_stage: str | None,
    note: str,
    at: str,
) -> None:
    history = manifest.setdefault("history", [])
    if not isinstance(history, list):
        history = []
        manifest["history"] = history
    history.append(
        {
            "at": at,
            "event": event,
            "from_stage": from_stage,
            "to_stage": to_stage,
            "note": note,
        }
    )


def verification(manifest: dict[str, Any]) -> dict[str, Any]:
    existing = manifest.setdefault("verification", {})
    if not isinstance(existing, dict):
        existing = {}
        manifest["verification"] = existing
    return existing


def done_gate_errors(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    checks = manifest.get("verification")
    if not isinstance(checks, dict):
        errors.append("verification object is missing")
        return errors

    if checks.get("spec_review") != "passed":
        errors.append("verification.spec_review must be passed before done")

    policy = manifest.get("review_policy")
    final_vetting = policy.get("final_vetting") if isinstance(policy, dict) else "off"
    if final_vetting == "required" and checks.get("final_vetting") != "passed":
        errors.append(
            "verification.final_vetting must be passed before done "
            "when review_policy.final_vetting is required"
        )
    return errors


def validation_issues(repo_root: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    seen: dict[str, list[Path]] = {}

    if not spectacula_root(repo_root).is_dir():
        errors.append(
            {
                "path": "docs/spectacula",
                "message": "docs/spectacula does not exist; run `spectacula bootstrap .` first",
            }
        )
        return errors, warnings

    for stage in STAGES:
        directory = stage_dir(repo_root, stage)
        if not directory.is_dir():
            errors.append(
                {
                    "path": repo_relative(directory, repo_root),
                    "message": "stage directory is missing",
                }
            )
            continue

        for path in sorted(directory.glob("*.json")):
            rel_path = repo_relative(path, repo_root)
            try:
                manifest = json.loads(path.read_text())
            except json.JSONDecodeError as exc:
                errors.append({"path": rel_path, "message": f"invalid JSON: {exc}"})
                continue

            if not isinstance(manifest, dict):
                errors.append({"path": rel_path, "message": "manifest must be a JSON object"})
                continue

            missing = sorted(field for field in REQUIRED_FIELDS if field not in manifest)
            for field in missing:
                errors.append({"path": rel_path, "message": f"missing required field: {field}"})

            slug = manifest.get("slug")
            if isinstance(slug, str) and slug:
                seen.setdefault(slug, []).append(path)
                if slug != path.stem:
                    errors.append(
                        {
                            "path": rel_path,
                            "message": f"slug {slug!r} does not match filename {path.stem!r}",
                        }
                    )
            else:
                errors.append({"path": rel_path, "message": "slug must be a non-empty string"})

            manifest_stage = manifest.get("stage")
            if manifest_stage != stage:
                errors.append(
                    {
                        "path": rel_path,
                        "message": f"stage {manifest_stage!r} does not match directory {stage!r}",
                    }
                )

            spec_path = resolve_spec_path(path, manifest)
            if spec_path is None:
                errors.append({"path": rel_path, "message": "spec_path must be a non-empty string"})
            elif not spec_path.is_file():
                errors.append(
                    {
                        "path": rel_path,
                        "message": f"spec_path does not resolve to a file: {spec_path}",
                    }
                )

            policy = manifest.get("review_policy")
            if isinstance(policy, dict) and "final_vetting" in policy:
                if policy["final_vetting"] not in {"off", "required"}:
                    errors.append(
                        {
                            "path": rel_path,
                            "message": "review_policy.final_vetting must be off or required",
                        }
                    )

            checks = manifest.get("verification")
            if isinstance(checks, dict):
                for name, value in checks.items():
                    if name == "notes":
                        continue
                    if isinstance(value, str) and value not in STATUS_VALUES:
                        errors.append(
                            {
                                "path": rel_path,
                                "message": f"verification.{name} has invalid status {value!r}",
                            }
                        )
            elif checks is not None:
                errors.append({"path": rel_path, "message": "verification must be an object"})

            if stage == "done":
                for message in done_gate_errors(manifest):
                    errors.append({"path": rel_path, "message": message})

    for slug, paths in sorted(seen.items()):
        if len(paths) > 1:
            joined = ", ".join(repo_relative(path, repo_root) for path in paths)
            errors.append(
                {
                    "path": slug,
                    "message": f"duplicate manifests for slug across stages: {joined}",
                }
            )

    return errors, warnings


def cmd_new(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo).resolve()
    ensure_docs_tree(repo_root)

    slug = args.slug
    if not SLUG_PATTERN.match(slug):
        raise SystemExit(
            "Slug must start with a letter or number and contain only letters, "
            "numbers, dots, underscores, or hyphens."
        )

    title = args.title or title_from_slug(slug)
    summary = args.summary or "Draft spec created and awaiting clarification."
    timestamp = now_utc()
    docs_root = spectacula_root(repo_root)
    spec_path = docs_root / "specs" / f"{slug}.md"
    manifest_path = docs_root / "specs" / f"{slug}.json"

    existing = [path for path in (spec_path, manifest_path) if path.exists()]
    active_manifest_matches = [
        path
        for path in find_manifest_matches(repo_root, slug)
        if path.resolve() != manifest_path.resolve()
    ]
    existing.extend(active_manifest_matches)
    if existing and not args.force:
        choices = "\n".join(f"- {repo_relative(path, repo_root)}" for path in existing)
        raise SystemExit(f"Refusing to overwrite existing files. Use --force to replace:\n{choices}")
    if active_manifest_matches and args.force:
        for path in active_manifest_matches:
            path.unlink()

    template_root = skill_root() / "assets" / "repo-template" / "docs" / "spectacula" / "templates"
    spec_template = (template_root / "spec.template.md").read_text()
    manifest_template = json.loads((template_root / "manifest.template.json").read_text())

    spec_text = spec_template.replace("<Specification Title>", title)
    spec_text = spec_text.replace(
        "<One-sentence description of what this spec defines.>",
        args.summary or f"Define {title}.",
    )

    manifest_template.update(
        {
            "spec_id": slug,
            "slug": slug,
            "title": title,
            "stage": "specs",
            "spec_path": f"../specs/{slug}.md",
            "created_at": timestamp,
            "updated_at": timestamp,
            "summary": summary,
            "next_action": "Answer open questions and refine the draft.",
        }
    )
    manifest_template["resume_context"] = {
        "last_completed_step": "Created initial draft from template.",
        "pending_steps": [
            "Fill in the major sections",
            "Resolve open questions",
            "Approve the spec",
        ],
        "open_questions": [],
        "last_reviewed_sections": [],
        "artifacts": [f"docs/spectacula/specs/{slug}.md"],
        "notes": "",
    }
    manifest_template["history"] = [
        {
            "at": timestamp,
            "event": "spec_created",
            "from_stage": None,
            "to_stage": "specs",
            "note": "Initial draft created from template.",
        }
    ]

    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(spec_text)
    write_json(manifest_path, manifest_template)

    print(f"Created {repo_relative(spec_path, repo_root)}")
    print(f"Created {repo_relative(manifest_path, repo_root)}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo).resolve()
    errors, warnings = validation_issues(repo_root)
    result = {"errors": errors, "warnings": warnings, "ok": not errors}
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if not errors and not warnings:
            print("Spectacula lifecycle validation passed.")
        if errors:
            print("Errors:")
            for issue in errors:
                print(f"- {issue['path']}: {issue['message']}")
        if warnings:
            print("Warnings:")
            for issue in warnings:
                print(f"- {issue['path']}: {issue['message']}")
    return 0 if not errors else 1


def load_all_manifests(repo_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    items: list[tuple[Path, dict[str, Any]]] = []
    for path in manifest_paths(repo_root):
        items.append((path, load_manifest(path)))
    return items


def manifest_summary(repo_root: Path, path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    spec_path = resolve_spec_path(path, manifest)
    return {
        "slug": manifest.get("slug", path.stem),
        "title": manifest.get("title", ""),
        "stage": manifest.get("stage", path_stage(repo_root, path)),
        "summary": manifest.get("summary", ""),
        "next_action": manifest.get("next_action", ""),
        "updated_at": manifest.get("updated_at", ""),
        "blockers": manifest.get("blockers", []),
        "verification": manifest.get("verification", {}),
        "resume_context": manifest.get("resume_context", {}),
        "manifest_path": repo_relative(path, repo_root),
        "spec_path": repo_relative(spec_path, repo_root) if spec_path else manifest.get("spec_path", ""),
    }


def cmd_status(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo).resolve()
    if args.target:
        path = resolve_manifest(repo_root, args.target)
        manifest = load_manifest(path)
        payload = manifest_summary(repo_root, path, manifest)
        if args.format == "json":
            print(json.dumps(payload, indent=2))
            return 0

        print(f"{payload['title']} ({payload['slug']})")
        print(f"Stage: {payload['stage']}")
        print(f"Summary: {payload['summary']}")
        print(f"Next action: {payload['next_action']}")
        blockers = payload["blockers"] or []
        print(f"Blockers: {', '.join(blockers) if blockers else 'none'}")
        print(f"Updated: {payload['updated_at']}")
        print(f"Spec: {payload['spec_path']}")
        print(f"Manifest: {payload['manifest_path']}")
        if payload["verification"]:
            print("Verification:")
            for name, value in payload["verification"].items():
                if name == "notes" and not value:
                    continue
                print(f"- {name}: {value}")
        resume_context = payload["resume_context"]
        if isinstance(resume_context, dict):
            last_completed = resume_context.get("last_completed_step")
            if last_completed:
                print(f"Last completed: {last_completed}")
            pending = resume_context.get("pending_steps") or []
            if pending:
                print("Pending:")
                for step in pending:
                    print(f"- {step}")
        return 0

    summaries = [
        manifest_summary(repo_root, path, manifest)
        for path, manifest in load_all_manifests(repo_root)
    ]
    if args.format == "json":
        print(json.dumps(summaries, indent=2))
        return 0

    if not summaries:
        print("No Spectacula manifests found.")
        return 0
    for item in summaries:
        print(
            f"{item['slug']} [{item['stage']}] "
            f"{item['title']} - next: {item['next_action']} "
            f"(updated {item['updated_at']})"
        )
    return 0


def cmd_move(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo).resolve()
    target_stage = args.stage
    source_path = resolve_manifest(repo_root, args.target)
    source_stage = path_stage(repo_root, source_path)
    manifest = load_manifest(source_path)

    if target_stage == "done" and not args.force:
        gate_errors = done_gate_errors(manifest)
        if gate_errors:
            joined = "\n".join(f"- {message}" for message in gate_errors)
            raise SystemExit(f"Refusing to move to done:\n{joined}")

    slug = manifest.get("slug")
    if not isinstance(slug, str) or not slug:
        raise SystemExit(f"Manifest is missing a valid slug: {source_path}")

    destination_path = stage_dir(repo_root, target_stage) / f"{slug}.json"
    if destination_path.exists() and destination_path.resolve() != source_path.resolve():
        raise SystemExit(
            f"Refusing to overwrite existing manifest: {repo_relative(destination_path, repo_root)}"
        )

    timestamp = now_utc()
    from_stage = manifest.get("stage") if isinstance(manifest.get("stage"), str) else source_stage
    manifest["stage"] = target_stage
    manifest["updated_at"] = timestamp
    manifest["summary"] = args.summary or default_stage_summary(target_stage)
    manifest["next_action"] = args.next_action or default_stage_next_action(target_stage)
    if target_stage == "ready":
        manifest["approved_at"] = timestamp
    elif target_stage == "inprogress":
        manifest["started_at"] = timestamp
    elif target_stage == "done":
        manifest["completed_at"] = timestamp

    resume_context = manifest.get("resume_context")
    if isinstance(resume_context, dict) and target_stage == "done":
        resume_context["last_completed_step"] = "Moved manifest to done after required verification gates passed."
        resume_context["pending_steps"] = []

    append_history(
        manifest,
        event=transition_event(str(from_stage), target_stage),
        from_stage=str(from_stage) if from_stage is not None else None,
        to_stage=target_stage,
        note=args.note or f"Moved manifest to {target_stage}.",
        at=timestamp,
    )

    write_json(destination_path, manifest)
    if destination_path.resolve() != source_path.resolve():
        source_path.unlink()
    print(
        f"Moved {slug} from {from_stage or 'unknown'} to {target_stage}: "
        f"{repo_relative(destination_path, repo_root)}"
    )
    return 0


def cmd_verdict(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo).resolve()
    path = resolve_manifest(repo_root, args.target)
    manifest = load_manifest(path)
    stage = path_stage(repo_root, path)
    if args.verdict == "failed" and stage != "inprogress":
        raise SystemExit("Failed final vetting must be recorded on an inprogress manifest.")

    timestamp = now_utc()
    checks = verification(manifest)
    checks["final_vetting"] = args.verdict
    if args.reason:
        existing_notes = checks.get("notes")
        prefix = f"{timestamp} final_vetting_{args.verdict}: {args.reason}"
        checks["notes"] = f"{existing_notes}\n{prefix}".strip() if existing_notes else prefix

    append_history(
        manifest,
        event=f"final_vetting_{args.verdict}",
        from_stage=manifest.get("stage") if isinstance(manifest.get("stage"), str) else stage,
        to_stage=manifest.get("stage") if isinstance(manifest.get("stage"), str) else stage,
        note=args.reason or f"Final vetting {args.verdict}.",
        at=timestamp,
    )
    manifest["updated_at"] = timestamp
    write_json(path, manifest)
    print(f"Recorded final vetting {args.verdict} for {manifest.get('slug', path.stem)}.")
    return 0


def find_inprogress_manifests(repo_root: Path) -> list[Path]:
    manifests_dir = repo_root / "docs" / "spectacula" / "inprogress"
    if not manifests_dir.is_dir():
        return []
    return sorted(
        path
        for path in manifests_dir.glob("*.json")
        if path.is_file()
    )


def resolve_review_manifest(repo_root: Path, target: str | None) -> Path:
    if target:
        raw_target = Path(target)
        if raw_target.suffix == ".json" or "/" in target or raw_target.is_absolute():
            candidate = raw_target if raw_target.is_absolute() else (repo_root / raw_target)
            if candidate.is_file():
                return candidate.resolve()
            raise SystemExit(f"Manifest path not found: {candidate}")

        slug_candidate = repo_root / "docs" / "spectacula" / "inprogress" / f"{target}.json"
        if slug_candidate.is_file():
            return slug_candidate.resolve()

        raise SystemExit(
            "Could not resolve review target. Use a slug from docs/spectacula/inprogress "
            f"or a manifest path. Target: {target}"
        )

    manifests = find_inprogress_manifests(repo_root)
    if len(manifests) == 1:
        return manifests[0].resolve()
    if not manifests:
        raise SystemExit(
            "No active manifests found in docs/spectacula/inprogress. "
            "Pass a slug or manifest path explicitly."
        )

    choices = "\n".join(f"- {path.relative_to(repo_root)}" for path in manifests)
    raise SystemExit(
        "Multiple active manifests found in docs/spectacula/inprogress. "
        "Pass a slug or manifest path explicitly:\n"
        f"{choices}"
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.command == "bootstrap":
        child_args = [args.target]
        if args.include_examples:
            child_args.append("--include-examples")
        if args.force:
            child_args.append("--force")
        return bootstrap_repo.main(child_args)

    if args.command == "new":
        return cmd_new(args)

    if args.command == "validate":
        return cmd_validate(args)

    if args.command == "status":
        return cmd_status(args)

    if args.command == "move":
        return cmd_move(args)

    if args.command == "verdict":
        return cmd_verdict(args)

    if args.command == "review":
        repo_root = Path(args.repo).resolve()
        manifest_path = resolve_review_manifest(repo_root, args.target)
        child_args = [
            "--repo",
            str(repo_root),
            "--manifest",
            str(manifest_path),
        ]
        if args.reviewer_prompt:
            child_args.extend(["--reviewer-prompt", args.reviewer_prompt])
        if args.format:
            child_args.extend(["--format", args.format])
        return render_review_prompt.main(child_args)

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
