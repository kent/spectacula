# Spectacula Lifecycle

Use this reference when specs are managed in `docs/spectacula` inside the user's working repository.

## Table of Contents

1. Directory Contract
2. Stage Meanings
3. Manifest Schema
4. Example Manifest
5. Transition Rules
6. Lifecycle CLI
7. Interruption And Resume Rules
8. Status Query Workflow

## Directory Contract

Use this repository layout:

```text
docs/spectacula/
  specs/
    <slug>.md
    <slug>.json
  ready/
    <slug>.json
  inprogress/
    <slug>.json
  done/
    <slug>.json
```

Rules:

- The active `docs/spectacula` tree belongs in the user's project repo, not in the installed skill directory.
- `docs/spectacula/specs/<slug>.md` is the canonical spec text.
- `docs/spectacula/<stage>/<slug>.json` is the stage manifest for the current lifecycle state.
- Only one manifest for a given `<slug>` should exist across `specs`, `ready`, `inprogress`, and `done` at a time.
- The manifest moves between stage directories. The Markdown spec does not.

## Stage Meanings

| Stage | Meaning |
|---|---|
| `specs` | Drafting, clarifying, or revising the spec before approval |
| `ready` | Spec approved and waiting for implementation |
| `inprogress` | Implementation or execution is active |
| `done` | Implementation finished and self-reviewed against the reference spec, plus final vetting when `review_policy.final_vetting` is `required` |

## Manifest Schema

Use JSON for stage manifests. Keep them concise but sufficient to resume work and answer status questions.

Required fields:

- `spec_id`: stable ID for the spec
- `slug`: filesystem-safe short name
- `title`: human-readable spec title
- `stage`: one of `specs`, `ready`, `inprogress`, `done`
- `spec_path`: manifest-relative path to the canonical Markdown spec in `docs/spectacula/specs`
- `updated_at`: ISO-8601 timestamp
- `summary`: short current-state summary
- `next_action`: the next concrete step
- `resume_context`: object with enough detail to resume
- `history`: append-only list of notable transitions/checkpoints

Recommended fields:

- `created_at`
- `approved_at`
- `started_at`
- `completed_at`
- `owner`
- `blockers`
- `reference_examples`
- `verification`
- `implementation`
- `review_policy`

Recommended `verification` fields:

- `format`
- `lint`
- `typecheck`
- `build`
- `tests`
- `spec_review`
- `final_vetting`
- `notes`

Recommended `review_policy` fields:

- `final_vetting`: `required` or `off`

Path rule:

- Resolve `spec_path` relative to the manifest file's current directory, not relative to the repository root.
- Example: `docs/spectacula/inprogress/my-spec.json` should use `"spec_path": "../specs/my-spec.md"`.
- When the manifest moves stages, keep the same `../specs/<slug>.md` value.

Use status values such as:

- `pending`
- `passed`
- `failed`
- `skipped`
- `blocked`
- `partial`

Recommended `resume_context` fields:

- `last_completed_step`
- `pending_steps`
- `open_questions`
- `last_reviewed_sections`
- `artifacts`
- `notes`

Recommended `history` item fields:

- `at`
- `event`
- `from_stage`
- `to_stage`
- `note`

Useful additional history events:

- `spec_audited`
- `spec_upgraded`
- `upgrade_blocked`
- `review_followup_needed`
- `final_vetting_passed`
- `final_vetting_failed`

## Example Manifest

```json
{
  "spec_id": "symphony-service",
  "slug": "symphony-service",
  "title": "Symphony Service Specification",
  "stage": "inprogress",
  "spec_path": "../specs/symphony-service.md",
  "created_at": "2026-03-12T14:00:00Z",
  "approved_at": "2026-03-12T15:20:00Z",
  "started_at": "2026-03-12T15:30:00Z",
  "updated_at": "2026-03-12T16:05:00Z",
  "summary": "Implementation is active for orchestrator state and retry handling.",
  "next_action": "Finish reconciliation flow and run the validation matrix.",
  "blockers": [],
  "review_policy": {
    "final_vetting": "off"
  },
  "resume_context": {
    "last_completed_step": "Implemented dispatch loop and claim tracking.",
    "pending_steps": [
      "Implement reconciliation termination rules",
      "Add retry timer backoff tests",
      "Run build and conformance checks"
    ],
    "open_questions": [],
    "last_reviewed_sections": [
      "7. Orchestration State Machine",
      "8. Polling, Scheduling, and Reconciliation"
    ],
    "artifacts": [
      "src/orchestrator.ts",
      "tests/orchestrator.test.ts"
    ],
    "notes": "Continue from the current branch state; do not restart from planning."
  },
  "verification": {
    "format": "pending",
    "lint": "pending",
    "typecheck": "pending",
    "build": "pending",
    "tests": "partial",
    "spec_review": "pending",
    "final_vetting": "pending"
  },
  "history": [
    {
      "at": "2026-03-12T14:00:00Z",
      "event": "spec_created",
      "from_stage": null,
      "to_stage": "specs",
      "note": "Initial draft saved."
    },
    {
      "at": "2026-03-12T15:20:00Z",
      "event": "spec_approved",
      "from_stage": "specs",
      "to_stage": "ready",
      "note": "Ready for implementation."
    },
    {
      "at": "2026-03-12T15:30:00Z",
      "event": "implementation_started",
      "from_stage": "ready",
      "to_stage": "inprogress",
      "note": "Implementation handoff accepted."
    }
  ]
}
```

## Transition Rules

- `specs -> ready`: move the manifest after approval; update `approved_at`, `summary`, and `next_action`.
- `ready -> inprogress`: move the manifest when implementation begins; add implementation/resume context.
- `inprogress -> done`: move the manifest after final self-review against the reference spec and, when `review_policy.final_vetting = "required"`, a final vetting pass; add verification results and `completed_at`.
- If the work is reopened, move the manifest back to the appropriate earlier stage instead of creating a duplicate.

Best practice for `inprogress -> done`:

- `done` should mean the implementation exists, the relevant verification gates were run, and `verification.spec_review` passed.
- When `review_policy.final_vetting = "required"`, `done` also requires `verification.final_vetting` to pass.
- When you want the assembled final vetting prompt and current context, prefer Spectacula's `scripts/spectacula++` or `scripts/spectacula review [<slug-or-manifest>]` command, then record the resulting verdict with `scripts/spectacula verdict <slug-or-manifest> passed|failed`.
- If a verification gate cannot pass yet, keep the manifest in `inprogress` unless the user explicitly accepts a blocked or partial state and that decision is recorded in `verification.notes` and `history`.

## Lifecycle CLI

The bundled command wrapper can perform the routine bookkeeping that otherwise requires hand-editing JSON:

```bash
scripts/spectacula new <slug> --title "<Title>"
scripts/spectacula status [<slug-or-manifest>]
scripts/spectacula validate
scripts/spectacula move <slug-or-manifest> ready
scripts/spectacula move <slug-or-manifest> inprogress
scripts/spectacula review [<slug-or-manifest>]
scripts/spectacula verdict <slug-or-manifest> passed --reason "<summary>"
scripts/spectacula move <slug-or-manifest> done
```

Use `validate` before important stage transitions and before marking work complete. It checks manifest uniqueness, stage/path consistency, required fields, known verification statuses, and `done` gate requirements.

## Interruption And Resume Rules

- Never treat stage manifests as copies of the spec.
- Resume by reading the canonical spec first, then the current stage manifest.
- Use `resume_context.last_completed_step`, `pending_steps`, and `history` to continue from the latest checkpoint.
- Update `updated_at`, `summary`, `next_action`, and `resume_context` whenever the current state materially changes.
- When a spec is audited or upgraded, record the result in `history` and update `resume_context` with the remaining findings or follow-up tasks.

## Status Query Workflow

When a user asks about spec status:

1. Search manifests across `docs/spectacula/specs`, `docs/spectacula/ready`, `docs/spectacula/inprogress`, and `docs/spectacula/done`.
2. Match by slug first, then by exact title, then by best-effort title similarity.
3. Read the matched manifest and the canonical spec title/path.
4. Report:
   - current stage
   - short summary
   - next action
   - blockers
   - verification status
   - last updated timestamp
   - canonical spec path
5. If no manifest exists but `docs/spectacula/specs/<slug>.md` exists, report it as an untracked draft and suggest creating a manifest.
