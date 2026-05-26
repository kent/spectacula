# Skill Building Best Practices Specification

Status: Approved v1
Purpose: Bring Spectacula in line with modern Codex skill-building practices and add repeatable checks.

## 1. Problem Statement

Spectacula already has a strong workflow, bundled scripts, references, assets, and UI metadata. The remaining risk is maintenance drift: skill-building guidance evolves around progressive disclosure, metadata quality, reference organization, and validation integrity, but the repository currently relies on manual review to catch those issues.

This spec makes the best-practices checks repeatable and fixes concrete gaps found during the audit.

## 2. Goals and Non-Goals

### 2.1 Goals

- Validate the root Codex skill and Claude plugin skill against modern skill-building constraints.
- Keep `SKILL.md` files concise, trigger-focused, and navigational.
- Ensure long reference files expose a table of contents so agents can preview scope before loading details.
- Ensure `agents/openai.yaml` remains useful and conforms to interface guidance.
- Add a project-local validation script that can run alongside `quick_validate.py`.
- Update development docs so future changes run both syntax/lifecycle checks and skill-quality checks.

### 2.2 Non-Goals

- Remove repository-level README or plugin docs. This repository is both a reusable skill package and a Claude plugin package, so repo-level docs are still appropriate.
- Replace the official `skill-creator` validator.
- Rewrite the Spectacula workflow or substantially shorten the root skill in this pass.
- Add subagent forward-testing automation.

## 3. Best-Practices Checklist

The implementation should check or satisfy:

| Area | Requirement |
|---|---|
| Frontmatter | `SKILL.md` frontmatter contains only `name` and `description`; both are non-empty. |
| Triggering | The root description clearly states what the skill does and when to use it. |
| Progressive disclosure | `SKILL.md` files stay under 500 lines and point to references/scripts instead of embedding every detail. |
| Reference hygiene | Reference files over 100 lines include a table of contents near the top. |
| Resource discoverability | Root `SKILL.md` directly links core references and scripts. |
| UI metadata | `agents/openai.yaml` has quoted strings, a 25-64 character short description, and a default prompt containing `$spectacula`. |
| Validation | Local commands can validate skill structure without relying on a human checklist. |

## 4. Implementation Plan

1. Add `scripts/validate_skill_best_practices.py`.
2. Make the script validate frontmatter, line-count limits, root resource links, long-reference table-of-contents markers, and `agents/openai.yaml` interface basics.
3. Add table-of-contents sections to long reference files that are intended to be loaded by agents.
4. Update README development guidance to include:
   - `quick_validate.py`
   - `scripts/validate_skill_best_practices.py`
   - `scripts/spectacula validate`
   - Python compile checks
5. Update the active manifest with verification evidence.

## 5. Test and Validation Plan

- Run `python3 -m py_compile scripts/*.py`.
- Run `python3 scripts/validate_skill_best_practices.py .`.
- Run the official skill validator: `PYTHONPATH=/tmp/skill-creator-deps python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .`.
- Run `python3 scripts/spectacula.py validate`.
- Run `git diff --check`.

## 6. Definition of Done

- Best-practices validation script exists and passes.
- Official skill validation passes.
- Long reference files have table-of-contents markers.
- README development commands include the new checks.
- Spectacula lifecycle validation passes.
- Manifest records verification and moves to `done`.
