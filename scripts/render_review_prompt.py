#!/usr/bin/env python3
"""Render Spectacula's final vetting prompt for an active manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


RESULT_SHAPE = {
    "approved": "<true if ready for done, else false>",
    "reason": "<short decisive explanation>",
    "critical_gaps": ["<blocking issue>", "<blocking issue>"],
    "important_fixes": ["<non-blocking but important fix>"],
    "verification_summary": "<what evidence exists or is missing>",
    "spec_coverage_summary": "<how well the implementation matches the spec>",
    "recommendation": "stay_inprogress | move_to_done",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render Spectacula's prompt-backed final vetting instructions for an "
            "active spec."
        )
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to the active Spectacula manifest, relative to --repo or absolute.",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--reviewer-prompt",
        help=(
            "Optional path to the reviewer prompt file. Defaults to "
            "agents/spectacula-reviewer.md in this skill."
        ),
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. Defaults to text.",
    )
    return parser.parse_args(argv)


def resolve_path(root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise SystemExit(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def load_text(path: Path) -> str:
    try:
        return path.read_text().rstrip()
    except FileNotFoundError as exc:
        raise SystemExit(f"Reviewer prompt not found: {path}") from exc


def run_git(repo_root: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_context(repo_root: Path) -> dict[str, str]:
    branch = run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD") or "unknown"

    default_branch = None
    remote_head = run_git(repo_root, "symbolic-ref", "refs/remotes/origin/HEAD")
    if remote_head and remote_head.startswith("refs/remotes/origin/"):
        default_branch = remote_head.removeprefix("refs/remotes/origin/")
    else:
        for candidate in ("main", "master"):
            if run_git(repo_root, "rev-parse", "--verify", candidate):
                default_branch = candidate
                break
            if run_git(repo_root, "rev-parse", "--verify", f"origin/{candidate}"):
                default_branch = f"origin/{candidate}"
                break

    compare_ref = default_branch or ""
    if default_branch and not default_branch.startswith("origin/"):
        if run_git(repo_root, "rev-parse", "--verify", f"origin/{default_branch}"):
            compare_ref = f"origin/{default_branch}"

    return {
        "branch": branch,
        "compare_ref": compare_ref,
        "tree_status": run_git(repo_root, "status", "--short") or "(clean working tree or status unavailable)",
    }


def build_prompt(
    repo_root: Path,
    manifest_path: Path,
    spec_path: Path,
    manifest: dict[str, Any],
    reviewer_prompt_path: Path,
    reviewer_prompt: str,
) -> str:
    verification = json.dumps(manifest.get("verification", {}), indent=2, sort_keys=True)
    review_policy = json.dumps(manifest.get("review_policy", {}), indent=2, sort_keys=True)
    stage = manifest.get("stage", "unknown")
    git_info = git_context(repo_root)
    compare_ref = git_info["compare_ref"] or "(no default branch detected)"
    if git_info["compare_ref"]:
        diff_guidance = f"""- Start with the local diff before reading supporting docs. Use the best available local comparison point, typically:
  - `git diff --stat {git_info["compare_ref"]}...HEAD`
  - `git diff --name-only {git_info["compare_ref"]}...HEAD`
  - `git diff {git_info["compare_ref"]}...HEAD`
- If there are uncommitted changes, also inspect:
  - `git diff --stat`
  - `git diff --cached --stat`"""
    else:
        diff_guidance = """- Start with the local diff before reading supporting docs.
- No default branch ref was detected automatically, so inspect the current working tree and recent commits directly, for example:
  - `git diff --stat`
  - `git diff --cached --stat`
  - `git log --oneline --decorate -n 10`"""
    return f"""Use the following Spectacula reviewer prompt as the final vetting rubric for this run.

Reviewer prompt source: {reviewer_prompt_path}

{reviewer_prompt}

Current run context:
- Repository root: {repo_root}
- Current branch: {git_info["branch"]}
- Suggested main diff base: {compare_ref}
- Active manifest: {repo_relative(manifest_path, repo_root)}
- Canonical spec: {repo_relative(spec_path, repo_root)}
- Current stage: {stage}
- Review policy:
{review_policy}
- Working tree status:
{git_info["tree_status"]}
- Current verification snapshot:
{verification}

Final vetting instructions:
- Treat this as the final vetting pass after the normal Spectacula implementation and self-review loop.
- This is a read-only review. Do not edit files or apply patches during this pass.
{diff_guidance}
- After diff triage, read the canonical spec and active manifest.
- Inspect the implementation, changed files, tests, and verification evidence.
- Use the reviewer prompt above as the primary rubric.
- Do not assume the work is ready just because tests passed.
- Return a structured verdict using this shape:
{json.dumps(RESULT_SHAPE, indent=2)}
- Return the verdict only. The caller should record the outcome with `scripts/spectacula verdict <slug-or-manifest> passed|failed --reason "<summary>"`.
- If the verdict is approved, the caller may then move to `done` after all other gates pass.
- If the verdict is not approved, the caller must keep the manifest in `inprogress` until the gaps are addressed or the user explicitly accepts the risk.
"""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    skill_root = Path(__file__).resolve().parent.parent
    repo_root = Path(args.repo).resolve()
    manifest_path = resolve_path(repo_root, args.manifest)

    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        print(f"Manifest must contain a JSON object: {manifest_path}", file=sys.stderr)
        return 2

    spec_ref = manifest.get("spec_path")
    if not isinstance(spec_ref, str) or not spec_ref:
        print(f"Manifest is missing spec_path: {manifest_path}", file=sys.stderr)
        return 2
    spec_path = (manifest_path.parent / spec_ref).resolve()
    if not spec_path.is_file():
        print(f"Canonical spec not found for manifest: {spec_path}", file=sys.stderr)
        return 2

    reviewer_prompt_path = (
        resolve_path(repo_root, args.reviewer_prompt)
        if args.reviewer_prompt
        else (skill_root / "agents" / "spectacula-reviewer.md").resolve()
    )
    reviewer_prompt = load_text(reviewer_prompt_path)
    prompt = build_prompt(
        repo_root,
        manifest_path,
        spec_path,
        manifest,
        reviewer_prompt_path,
        reviewer_prompt,
    )

    if args.format == "json":
        print(
            json.dumps(
                {
                    "repo_root": str(repo_root),
                    "manifest_path": str(manifest_path),
                    "spec_path": str(spec_path),
                    "reviewer_prompt_path": str(reviewer_prompt_path),
                    "prompt": prompt,
                    "result_shape": RESULT_SHAPE,
                },
                indent=2,
            )
        )
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
