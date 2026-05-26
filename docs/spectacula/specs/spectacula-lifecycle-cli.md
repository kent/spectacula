# Spectacula Lifecycle CLI Specification

Status: Approved v1
Purpose: Make Spectacula's lifecycle bookkeeping enforceable through local commands instead of relying only on prompt discipline.

## 1. Problem Statement

Spectacula defines a clear lifecycle for specs, manifests, verification, and strict final vetting, but most lifecycle mutations are still manual. Agents are instructed to create manifests, move stage files, validate `done` gates, report status, and record final-vetting outcomes by editing JSON directly. That creates avoidable drift between the contract, the manifests, and the actual repository state.

The CLI currently supports only `bootstrap` and `review`. This improvement adds mechanical support for the common lifecycle operations while preserving Spectacula's prompt-first design.

## 2. Goals and Non-Goals

### 2.1 Goals

- Add local commands for creating a tracked spec, validating manifests, reporting status, moving manifests between stages, and recording final-vetting verdicts.
- Enforce the core lifecycle invariants from `references/spectacula-lifecycle.md`.
- Make strict `$spectacula++` runs safer by refusing to move work to `done` unless the required verification signals are present.
- Update docs so users can operate Spectacula without hand-editing JSON for routine lifecycle actions.

### 2.2 Non-Goals

- Build a full interactive TUI or daemon.
- Replace the agent's responsibility to write high-quality specs.
- Automatically judge implementation correctness. The CLI records verification state, but it does not decide whether code matches a spec without an explicit verdict.
- Change the canonical `docs/spectacula` directory layout.

## 3. Command Contract

### 3.1 `spectacula new`

Creates a canonical spec and a draft manifest.

Required behavior:

- Accept a slug as the first positional argument.
- Accept optional `--title`, `--repo`, `--summary`, and `--force`.
- Create `docs/spectacula/specs/<slug>.md` from the bundled spec template when absent.
- Create `docs/spectacula/specs/<slug>.json` from the manifest template when absent.
- Fill placeholder values for slug, title, timestamps, spec path, summary, history, and artifact references.
- Refuse to overwrite existing spec or manifest files unless `--force` is set.

### 3.2 `spectacula validate`

Checks lifecycle integrity.

Required behavior:

- Inspect manifests in `docs/spectacula/specs`, `ready`, `inprogress`, and `done`.
- Validate each manifest is JSON object with required fields.
- Validate `stage` matches the manifest directory.
- Validate `slug` matches the manifest filename.
- Validate `spec_path` resolves to an existing canonical Markdown spec.
- Detect duplicate manifests for the same slug across stage directories.
- Validate `review_policy.final_vetting` is either `off` or `required` when present.
- Validate verification statuses are from the lifecycle status set.
- Enforce `done` gates:
  - `verification.spec_review` must be `passed`.
  - If `review_policy.final_vetting = required`, `verification.final_vetting` must be `passed`.
- Return a non-zero exit code when errors are present.
- Support `--format text|json`.

### 3.3 `spectacula status`

Reports tracked spec state.

Required behavior:

- With no target, list all tracked specs with stage, title, next action, and updated timestamp.
- With a slug or manifest path, report detailed state for that spec.
- Include blockers, verification state, canonical spec path, and resume-context summary in detailed output.
- Support `--format text|json`.

### 3.4 `spectacula move`

Moves one manifest between lifecycle stages.

Required behavior:

- Accept a slug or manifest path and a target stage.
- Support stages `specs`, `ready`, `inprogress`, and `done`.
- Update `stage`, `updated_at`, relevant transition timestamps, summary, next action, and history.
- Refuse to create duplicate active manifests.
- Refuse `done` unless done-gate verification requirements pass, unless `--force` is explicitly supplied.
- Preserve the canonical spec Markdown in `docs/spectacula/specs`.

### 3.5 `spectacula verdict`

Records a final-vetting verdict.

Required behavior:

- Accept a slug or manifest path and `passed` or `failed`.
- Update `verification.final_vetting`.
- Append `final_vetting_passed` or `final_vetting_failed` to history.
- Accept optional `--reason` and store it in `verification.notes`.
- Keep failed work in `inprogress`.
- When passed, do not automatically move to `done`; require a separate `move ... done` command so the final stage transition remains deliberate.

## 4. Manifest Path Contract

`spec_path` is manifest-relative. A manifest at `docs/spectacula/inprogress/foo.json` should point to `../specs/foo.md`. The CLI and docs must state this explicitly and resolve paths the same way.

## 5. Failure Model

- Missing `docs/spectacula` should produce a clear bootstrap hint.
- Ambiguous targets should list possible matches.
- Invalid JSON should identify the bad file and parser error.
- Refused transitions should explain the exact missing gate.
- Text output should be concise enough for agent logs; JSON output should be structured enough for follow-up automation.

## 6. Test and Validation Plan

- Run `python3 -m py_compile scripts/*.py`.
- Exercise `new`, `status`, `validate`, `verdict`, and `move` in a temporary bootstrapped repo.
- Validate this repository's own `docs/spectacula` state.
- Render strict final-vetting context with `scripts/spectacula++`.
- Perform a read-only final vetting pass against this spec before moving the manifest to `done`.

## 7. Definition of Done

- The command wrapper exposes `new`, `validate`, `status`, `move`, and `verdict`.
- The CLI enforces duplicate, stage, path, status, and done-gate rules.
- README and lifecycle docs describe the new commands and the manifest-relative `spec_path` rule.
- Verification commands pass or blocked gates are recorded explicitly.
- `verification.spec_review` is `passed`.
- Because this run uses `$spectacula++`, `verification.final_vetting` is `passed` before the manifest moves to `done`.
