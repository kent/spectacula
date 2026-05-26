---
name: spectacula
description: Plan, write, store, track, audit, upgrade, and implement detailed specifications from rough ideas. Use when Codex needs to take a high-level or terse prompt, infer a strong implementation-ready spec shape from repo context and reference examples, ask clarifying questions only where they materially change the design, write a structured spec, audit or upgrade existing specs in `docs/spectacula/specs`, move the work through the `docs/spectacula` lifecycle, preserve resume context across `specs`, `ready`, `inprogress`, and `done`, answer status questions about active or completed specs, or provide Spectacula help and usage guidance, including the common typo `spectacular`.
---

# Spectacula

Turn a vague request into a concrete specification in this order: frame the problem, plan the document, ask clarifying questions, then write the final spec. When the task continues into delivery, hand off into an implementation loop that builds against the spec and re-checks the result until the build matches the reference.

Spectacula also supports two explicit review workflows:

- `spec-audit`: review one or more existing specs against the current Spectacula quality bar and report structured findings
- `spec-upgrade`: rewrite one or more existing specs in place so they meet the current Spectacula quality bar while preserving intent

## Help Mode

If the user asks for help, usage, examples, installation guidance, or types `spectacula help`, `$spectacula help`, or the common typo `spectacular help` / `$spectacular help`:

- Do not start planning or rewriting specs unless the user also asked for that.
- Return a concise help response with:
  - what Spectacula does
  - the core commands or prompt patterns
  - where specs and manifests live
  - how to create, audit, upgrade, implement, and query status
  - the most relevant install or upgrade note when asked
- Prefer concrete command-style examples over abstract explanation.
- Mention that the canonical Codex invocation is `$spectacula ...`.
- Mention the stronger alias `$spectacula++ ...` for runs that require a final vetting pass before `done`.

## Run The Workflow

Invocation aliases the skill should recognize:

- `$spectacula ...` or `spectacula ...`: normal Spectacula run; set `review_policy.final_vetting = "off"` for this call unless the user explicitly overrides it
- `$spectacula++ ...` or `spectacula++ ...`: stricter Spectacula run; set `review_policy.final_vetting = "required"` for this call

When either alias is used:

- strip the alias token from the working title or slug derivation
- record the current choice in the active manifest as `review_policy.final_vetting`
- treat the latest call as authoritative when resuming an existing manifest

1. Frame the request
- Identify the artifact type: product spec, system design, API/interface spec, workflow/process spec, migration plan, or decision memo.
- Identify the reader: engineer, operator, PM, reviewer, or mixed audience.
- Extract explicit constraints, success criteria, dependencies, deadlines, and platform limits from the prompt or codebase.
- Inspect the repo or provided docs before proposing architecture when the request depends on an existing system.
- If the user prompt is terse, infer the likely implementation surface from repo context instead of waiting for the user to restate obvious details.
- Synthesize a concrete working title, purpose line, and likely affected subsystems before the question phase.

2. Plan before writing
- Draft a short internal outline: likely sections, missing facts, major decisions, and risks.
- Choose only the sections that add decision value. Do not emit boilerplate sections that say nothing.
- Use [spec-blueprint.md](./references/spec-blueprint.md) as the default structure unless the user supplied a format to mirror.
- For software, architecture, workflow, protocol, or implementation-facing feature work, default to the high-rigor or contract-heavy formats from [spec-blueprint.md](./references/spec-blueprint.md), not the light-weight variant.
- Treat a long-form reference spec as the minimum acceptable detail level, not just a loose style cue.
- Assume the user wants an implementation-ready spec by default. Do not ask whether they want a brief versus a full spec unless the prompt explicitly suggests they want something lightweight.
- Prefer a deeper spec over a broader one. Cut filler first.

3. Ask clarifying questions
- Ask 3-7 high-leverage questions from [question-bank.md](./references/question-bank.md).
- Prioritize questions that change scope, interfaces, constraints, acceptance criteria, or rollout decisions.
- Do not spend questions on details you can responsibly infer from the repo, the user prompt, or the provided reference specs.
- Ask grouped, concrete questions instead of open-ended fishing.
- Ask the clarifying questions once, in a single user-facing batch.
- Do not preview the same questions in a progress update and then repeat them again.
- If a short lead-in is useful, keep it to one sentence and place the questions immediately below it in the same message.
- Skip questions only when the prompt already contains enough detail to support a defensible spec.
- If the user says to make reasonable assumptions, proceed and record the assumptions explicitly.

4. Write the spec
- Match the user's requested format. When the user provides an example spec, mirror its title style, numbered headings, table usage, and appendix/checklist structure.
- Mirror the reference spec's detail density too: if the example is RFC-like, produce a full RFC-like document with substantial sections and subsections, not a compressed brief.
- If the user provides multiple example specs, synthesize the shared structure and quality bar instead of copying any single document mechanically.
- Separate facts, decisions, and assumptions.
- Make behavior concrete: include inputs, outputs, state, routing rules, failure handling, and validation logic where relevant.
- Expand terse bullets into implementation-usable sections. A short user prompt does not justify a short spec when the requested output is an implementation-ready technical specification.
- Convert short prompts into rich specs by filling in the missing structure: current state, goals, scope, UX or operator flow, data contracts, backend/frontend changes, instrumentation, edge cases, rollout, and validation.
- Use tables for schemas, attributes, comparison points, and configuration surfaces.
- Use pseudocode only when it clarifies nontrivial behavior.
- For repository-backed feature work, include current-state context, proposed data/backend/frontend changes, instrumentation, failure handling, testing, and definition of done unless the user explicitly asks for a lighter artifact.
- End with a definition of done, validation matrix, acceptance checks, open questions, or assumption ledger when those artifacts add review value.

5. Close the loop
- Call out unresolved unknowns instead of hiding them in vague prose.
- Mark assumptions with enough specificity that another engineer or PM can confirm or reject them.
- Compress the spec only when the user explicitly asks for a lighter artifact, draft, brief, or memo. Otherwise, keep the default output fully detailed.

6. Move into implementation when requested
- Treat the completed spec as the reference contract for implementation.
- Use the implementation-phase handoff in [implementation-handoff.md](./references/implementation-handoff.md) when the user wants code built from the plan.
- Require an explicit self-check loop: implement, compare against the reference spec, fix gaps, then perform a final review against the same spec.
- Run available verification gates before the final review: format, lint, typecheck, build, test, or equivalent project-native checks.
- Fix verification failures before claiming completion unless the user explicitly accepts a blocked state.
- Record the self-review result in `verification.spec_review`.
- Treat `review_policy.final_vetting` as the per-call selector. If the latest invocation was `spectacula++`, require final vetting before `done`. If it was plain `spectacula`, do not require it.
- When `review_policy.final_vetting = "required"`, look for [agents/spectacula-reviewer.md](./agents/spectacula-reviewer.md) or render the bundled prompt with [scripts/spectacula++](./scripts/spectacula++) or [scripts/spectacula](./scripts/spectacula) `review`, then apply that rubric as a final read-only, diff-first, PR-gate-style vetting pass after the normal implementation loop.
- Record the final vetting verdict in `verification.final_vetting` and append a `final_vetting_passed` or `final_vetting_failed` history event to the manifest.
- If the current run requires final vetting and it fails, keep the manifest in `inprogress` until the findings are addressed and the vetting pass is rerun.
- Do not stop at "implementation done" if the result still misses required behavior from the reference spec.

## Audit And Upgrade Existing Specs

When the user asks for `spec-audit`:

- Inspect one spec or all specs under `docs/spectacula/specs`.
- Compare each spec against [spec-audit-rubric.md](./references/spec-audit-rubric.md), the current [spec-blueprint.md](./references/spec-blueprint.md), and any explicit reference specs the user supplied.
- Evaluate at least:
  - structure and section coverage
  - implementation detail and current-state context
  - contracts, data model, and interfaces where relevant
  - failure handling, instrumentation, rollout, testing, and definition of done
  - unresolved assumptions and missing decisions
- Produce concrete findings per spec, ordered by severity and implementation risk.
- Prefer a review style that says what is missing, weak, ambiguous, or non-actionable. Do not hide the gaps behind polite summaries.
- If the user asked only for audit, do not rewrite the spec yet.
- Update the matching manifest when present with review-oriented `summary`, `next_action`, `resume_context`, and a history event such as `spec_audited`.

When the user asks for `spec-upgrade`:

- Start from the existing spec as source material, not from scratch.
- Preserve the original problem statement and product intent unless the user explicitly changes scope.
- Rewrite the spec in place to meet the current Spectacula quality bar.
- Use repo context, existing code, existing docs, and prior manifests to infer missing implementation detail where safe.
- Add the missing structure, subsections, tables, validation material, and assumptions needed to make the document implementation-ready.
- If key decisions are still unknown, ask only the minimum clarifying questions that materially affect the upgraded spec.
- Update the matching manifest with what changed, any remaining blockers, the next action, and a history event such as `spec_upgraded`.
- If the upgraded spec is still blocked on human decisions, record that explicitly instead of pretending it is complete.

## Manage Spectacula State

- Always store live specs in the user's current working repository, not in the installed skill directory.
- If `docs/spectacula` does not exist in the current working repo, bootstrap it with [scripts/bootstrap_repo.py](./scripts/bootstrap_repo.py) or copy [assets/repo-template/docs/spectacula](./assets/repo-template/docs/spectacula) into the repo.
- Store canonical specs in `docs/spectacula/specs/<slug>.md`.
- Keep exactly one active stage manifest per spec as `docs/spectacula/<stage>/<slug>.json`.
- Use stages `specs`, `ready`, `inprogress`, and `done`.
- Do not copy the full spec body into stage manifests. The manifest must point back to the canonical spec in `docs/spectacula/specs`.
- Treat `spec_path` as manifest-relative, normally `../specs/<slug>.md`.
- Move the manifest file between stage directories as work advances. The Markdown spec stays in `docs/spectacula/specs`.
- Update manifest metadata whenever the stage changes or an important checkpoint is reached, so interrupted work can resume cleanly.
- Prefer [scripts/spectacula](./scripts/spectacula) `new`, `status`, `validate`, `move`, and `verdict` for routine lifecycle bookkeeping when the script is available.
- Use the Spectacula contract in [spectacula-lifecycle.md](./references/spectacula-lifecycle.md).

## Answer Status Questions

- When the user asks for the status of a spec, inspect `docs/spectacula/specs`, `docs/spectacula/ready`, `docs/spectacula/inprogress`, and `docs/spectacula/done`.
- Identify the spec by slug, title, or closest matching manifest/spec pair.
- Report the current stage, summary, blockers, next action, verification status, last update time, and canonical spec path.
- For interrupted work, use the manifest `resume_context` plus the canonical spec to continue from the last checkpoint instead of starting over.
- If the latest manifest history includes an audit or upgrade event, report the most important findings or upgrades too.

## Adapt The Spec To The Artifact

- For product or feature specs, emphasize user journeys, scope boundaries, success metrics, dependencies, rollout, and operational ownership.
- For system or architecture specs, emphasize components, data flow, state transitions, interfaces, failure modes, observability, and test strategy.
- For workflow or process specs, emphasize roles, triggers, handoffs, approvals, exception paths, and SLAs.
- For API, schema, or protocol specs, emphasize contracts, invariants, versioning, compatibility, error models, and example payloads.

## Keep The Output Sharp

- Default to Markdown.
- Use numbered sections for long-form specs.
- Preserve short preamble metadata such as `Status:` or `Purpose:` when the examples use that pattern.
- Define terms once and keep names stable across sections.
- Prefer explicit tradeoffs over generic praise or filler.
- Avoid repeating the same requirement in multiple sections unless the repetition is intentional and cross-referenced.
- Make the user's job easy: a short, rough prompt should still yield a strong spec if the repo and examples provide enough context.

## Use The References

- Use [spec-blueprint.md](./references/spec-blueprint.md) to choose and shape the final document structure.
- Use [question-bank.md](./references/question-bank.md) to select the smallest set of clarifying questions that materially affects the spec.
- Use [implementation-handoff.md](./references/implementation-handoff.md) when the task transitions from planning/specification into coding.
- Use [spec-audit-rubric.md](./references/spec-audit-rubric.md) when reviewing or upgrading existing specs.
- Use [spectacula-lifecycle.md](./references/spectacula-lifecycle.md) when storing or tracking specs in `docs/spectacula`.
- Use [scripts/spectacula](./scripts/spectacula) for lifecycle commands, or [scripts/bootstrap_repo.py](./scripts/bootstrap_repo.py) / [assets/repo-template/docs/spectacula](./assets/repo-template/docs/spectacula) to scaffold `docs/spectacula` into the user's working repo.
- Use [claude-portable-prompt.md](./references/claude-portable-prompt.md) when adapting this skill for Claude project instructions or a Claude agent prompt.
- When updating Spectacula itself, also run [scripts/validate_skill_best_practices.py](./scripts/validate_skill_best_practices.py) and the official `skill-creator` `quick_validate.py` check before finishing.

This skill is intentionally prompt-first and portable. The Codex skill is the source of truth; the Claude prompt reference keeps the same workflow and quality bar when you need the same behavior in Claude.
