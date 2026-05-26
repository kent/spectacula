---
name: spectacula
description: Plan, write, store, track, audit, upgrade, and implement detailed specifications from rough ideas. Use when Claude needs to turn a high-level or terse prompt into a clarified, implementation-ready spec by combining repo context with reference examples, audit or upgrade existing specs in docs/spectacula/specs, manage the work through docs/spectacula in the user's repo, preserve resume context, answer status questions about active or completed specs, or provide Spectacula help and usage guidance.
---

# Spectacula

Use Spectacula to turn a vague request into a tracked, implementation-ready specification and then drive the work through implementation and completion.

It also supports two explicit review workflows:

- `spec-audit` for reviewing existing specs against the current Spectacula quality bar
- `spec-upgrade` for rewriting existing specs in place to meet that quality bar

Invocation aliases:

- `/spectacula:spectacula` or `spectacula` in the user request for the normal flow; record `review_policy.final_vetting = "off"` for the current run unless the user explicitly overrides it
- `spectacula++` in the user request for the stricter flow that requires a final vetting pass before `done`; record `review_policy.final_vetting = "required"` for the current run

## Help Mode

If the user asks for help, usage, examples, installation guidance, or types `/spectacula:spectacula help`:

- Do not start planning or rewriting specs unless the user also asked for that.
- Return a concise usage guide with the main workflows, command patterns, and docs/spectacula lifecycle paths.

## Core Workflow

1. Frame the request
- Identify the artifact type, audience, constraints, dependencies, deadlines, and success criteria.
- Inspect the repo or provided docs before proposing architecture when the spec depends on an existing system.
- If the prompt is terse, infer the likely implementation surface and affected areas from the repo before asking for more detail.

2. Plan before writing
- Draft a short internal outline with likely sections, missing facts, major decisions, and risks.
- Match the shape and rigor of any reference specs the user provides.
- For software, system, workflow, protocol, or implementation-facing feature work, default to a long-form engineering spec unless the user explicitly asks for something lighter.
- Assume implementation-ready depth by default.

3. Ask clarifying questions
- Ask 3-7 high-leverage questions when the request is still ambiguous.
- Prefer grouped, concrete questions that affect scope, interfaces, constraints, acceptance criteria, or rollout.
- Do not ask questions whose answers can be responsibly inferred from the repo or the supplied references.
- Ask the questions once, in a single batch to the user.
- Do not send a separate progress note that repeats or previews the same questions.
- If you need a lead-in, keep it to one sentence and include the full question list immediately after it.

4. Write the spec
- Produce a structured Markdown spec with concrete behavior, interfaces, failure handling, and validation logic where relevant.
- Match the depth of any reference spec the user provides. If the example is long-form and RFC-like, produce a long-form and RFC-like output rather than a compact brief.
- Expand short prompts into detailed implementation sections when the task is technical and implementation-facing.
- Fill in likely sections from context so a short prompt still becomes a complete engineering spec.
- End with a definition of done, validation matrix, acceptance checks, or an assumption ledger when those artifacts add review value.

5. Move into implementation when requested
- Treat the approved spec as the reference contract.
- Implement against it, re-read it, fix gaps, and run verification gates.
- Always finish with a final self-review against the same spec before moving to `done`.
- Treat `review_policy.final_vetting` as the authoritative per-run selector. If the latest invocation uses the stricter alias (`spectacula++`), require final vetting before `done`. If it uses the normal alias, do not require it.
- When `review_policy.final_vetting = "required"`, render the bundled reviewer prompt with `python3 "${CLAUDE_SKILL_DIR}/../../scripts/spectacula.py" review [<slug-or-manifest>]` or read `agents/spectacula-reviewer.md` directly, then apply that rubric as a final read-only vetting pass.
- Record the verdict as `verification.final_vetting` and keep the manifest in `inprogress` if the vetting pass fails.
- When working entirely inside Claude, use the `spectacula-reviewer` subagent or an agent team reviewer as the final vetting reviewer rather than reusing the main implementer's own judgment.

6. Audit or upgrade specs when requested
- For `spec-audit`, inspect one or more specs in `docs/spectacula/specs`, compare them against the current quality bar and supplied references, and produce structured findings without rewriting unless asked.
- For `spec-upgrade`, rewrite one or more existing specs in place to match the current quality bar while preserving the original intent and repo context.
- Use [../../references/spec-audit-rubric.md](../../references/spec-audit-rubric.md) for both workflows.

## Manage Spectacula State

- Store live specs in the user's working repository, not in the installed plugin directory.
- If `docs/spectacula` does not exist in the user's repo, bootstrap it with:

```bash
python3 "${CLAUDE_SKILL_DIR}/../../scripts/bootstrap_repo.py" .
```

- Store the canonical spec at `docs/spectacula/specs/<slug>.md`.
- Keep exactly one active JSON manifest at `docs/spectacula/specs`, `ready`, `inprogress`, or `done`.
- Move only the manifest between stage directories. Keep the spec Markdown fixed in `docs/spectacula/specs`.
- Treat `spec_path` as manifest-relative, normally `../specs/<slug>.md`.
- Preserve `summary`, `next_action`, `history`, `verification`, and `resume_context` so interrupted work can resume cleanly.
- Treat `verification.spec_review` and `verification.final_vetting` as separate signals. `done` always requires `spec_review=passed`. If `review_policy.final_vetting = "required"`, also require `final_vetting=passed` before moving to `done`.
- Prefer the bundled lifecycle command wrapper (`spectacula new`, `status`, `validate`, `move`, and `verdict`) when available instead of hand-editing routine manifest transitions.

## Use Claude Subagents And Agent Teams

- The plugin ships focused Claude subagents in `agents/` for architecture, implementation, review, and status work.
- Use subagents for focused work that reports back to the lead.
- Use Claude agent teams when you need parallel workers that can communicate and coordinate independently.
- Agent teams are experimental and must be enabled by the user before use.
- For team patterns and prompts, see [../../references/claude-agent-teams.md](../../references/claude-agent-teams.md).

## Status Queries

When asked for the status of a spec:

- inspect the manifests in `docs/spectacula/specs`, `ready`, `inprogress`, and `done`
- match by slug first, then title
- report stage, summary, blockers, next action, verification status, updated time, and canonical spec path

## Additional Resources

- For the authoritative Codex skill instructions, see [../../SKILL.md](../../SKILL.md)
- For the lifecycle contract, see [../../references/spectacula-lifecycle.md](../../references/spectacula-lifecycle.md)
- For spec structure guidance, see [../../references/spec-blueprint.md](../../references/spec-blueprint.md)
- For review and upgrade quality criteria, see [../../references/spec-audit-rubric.md](../../references/spec-audit-rubric.md)
- For clarifying-question strategy, see [../../references/question-bank.md](../../references/question-bank.md)
- For implementation handoff and verification expectations, see [../../references/implementation-handoff.md](../../references/implementation-handoff.md)
- For Claude parallel-execution guidance, see [../../references/claude-agent-teams.md](../../references/claude-agent-teams.md)
- For the scaffold copied into user repos, see [../../assets/repo-template/docs/spectacula](../../assets/repo-template/docs/spectacula)
