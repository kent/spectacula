# Spectacula 🧛🏻‍♂️

Spectacula 🧛🏻‍♂️ is a spec-first workflow for Codex and Claude.

It combines:

- a reusable Codex skill at the repository root
- a first-class Claude Code plugin
- a Claude-compatible prompt reference
- a bootstrap template for creating `docs/spectacula` inside a user's working repository

The goal is to take a rough idea, turn it into a rigorous specification, track the work through approval and implementation, preserve resume context if execution is interrupted, and answer status questions from structured metadata.

## Packaging Best Practice

This repository follows a split that works well across both agent ecosystems:

- the installed package stays static and reusable
- the live `docs/spectacula` state lives in the user's project repo
- Codex uses the root [SKILL.md](./SKILL.md)
- Claude Code uses the plugin manifest at [.claude-plugin/plugin.json](./.claude-plugin/plugin.json) and the plugin skill at [skills/spectacula/SKILL.md](./skills/spectacula/SKILL.md)

The top-level `skills/` directory exists because Claude plugins require that layout. It does not mean this repo contains multiple logical skills.
The top-level `agents/` directory is shared: `openai.yaml` is Codex-facing metadata, while the Markdown files are Claude Code subagents.

## Repository Layout

```text
SKILL.md
agents/
  openai.yaml
  spectacula-architect.md
  spectacula-implementer.md
  spectacula-reviewer.md
  spectacula-status.md
.claude-plugin/
  plugin.json
  marketplace.json
skills/
  spectacula/
    SKILL.md
references/
scripts/
assets/
  repo-template/
    docs/
      spectacula/
```

## What The Skill Does

`spectacula`:

- plans before writing
- asks clarifying questions
- writes implementation-ready specs
- turns short prompts into full engineering specs by using repo context and reference examples
- audits existing specs against the current quality bar
- upgrades weaker specs in place
- stores canonical specs in `docs/spectacula/specs`
- moves stage manifests across `specs`, `ready`, `inprogress`, and `done`
- preserves summary, history, verification state, and resume context
- provides lifecycle CLI commands for creating, validating, moving, reporting, and recording final-vetting verdicts
- drives implementation from the approved spec
- requires verification gates before marking work done
- supports an invokable final-vetting prompt before marking work done

Primary files:

- Skill instructions: [SKILL.md](./SKILL.md)
- Claude prompt: [references/claude-portable-prompt.md](./references/claude-portable-prompt.md)
- Claude team guidance: [references/claude-agent-teams.md](./references/claude-agent-teams.md)
- Lifecycle contract: [references/spectacula-lifecycle.md](./references/spectacula-lifecycle.md)
- Command wrapper: [scripts/spectacula](./scripts/spectacula)
- Bootstrap script: [scripts/bootstrap_repo.py](./scripts/bootstrap_repo.py)
- Final vetting prompt renderer: [scripts/render_review_prompt.py](./scripts/render_review_prompt.py)
- Bootstrap template: [assets/repo-template/docs/spectacula](./assets/repo-template/docs/spectacula)
- Claude plugin manifest: [.claude-plugin/plugin.json](./.claude-plugin/plugin.json)
- Claude plugin skill: [skills/spectacula/SKILL.md](./skills/spectacula/SKILL.md)
- Claude plugin subagents: [agents](./agents)

Per-call aliases:

- `$spectacula ...` for the normal flow
- `$spectacula++ ...` for the stricter flow that requires a final vetting pass before `done`

What the aliases change during implementation:

- `$spectacula ...` uses the standard Spectacula loop: implement, run native checks, self-review against the spec, then move to `done` when the normal gates pass
- `$spectacula++ ...` uses the same implementation loop, but also requires `review_policy.final_vetting = "required"` and a separate final vetting verdict in `verification.final_vetting` before `done`
- `~/.codex/skills/spectacula/scripts/spectacula review` renders the exact local pre-PR review prompt and repo context for that final gate
- `~/.codex/skills/spectacula/scripts/spectacula verdict <slug> passed|failed` records the final-vetting outcome before a strict run can move to `done`

## Better Specs With Less Prompting

Spectacula is designed so the user does not need to write a perfect prompt.

Default behavior:

- short prompts are expanded into implementation-ready specs
- repo context is used to infer affected systems and current state
- reference specs set the expected depth and structure
- clarifying questions are reserved for decisions that materially change the design
- the default output is a full technical spec, not a brief

Good minimal prompts:

```text
$spectacula Add CRUD operations for Erlang-based OTP agents.
```

```text
$spectacula Add approval gates to the deploy workflow. Match the Attractor-style reference in depth.
```

```text
$spectacula Build a full implementation-ready spec for CRUD operations for Erlang-based OTP agents. Use the repo and existing docs to fill in the current state.
```

```text
$spectacula++ Implement the approved CRUD operations for Erlang-based OTP agents and keep the manifest current through ready, inprogress, and done.
```

Review prompts:

```text
$spectacula spec-audit docs/spectacula/specs
```

```text
$spectacula spec-upgrade docs/spectacula/specs/evidence-first-insight-detail.md
```

Help prompt:

```text
$spectacula help
```

When you want to steer the result more explicitly, add one of these suffixes:

- `Match this reference in depth and structure`
- `Assume implementation-ready detail by default`
- `Use the existing repo context and make reasonable assumptions`
- `Produce a full RFC-style engineering spec`
- `Audit every spec against the current Spectacula quality bar`
- `Upgrade this spec in place to match the Attractor-style reference quality`

## Install And Upgrade In Codex

Recommended Codex install modes:

- regular users: install from GitHub with the built-in Codex skill installer
- local development: symlink the repo into `~/.codex/skills`

Best-practice install for normal use:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo argonavis-labs/spectacula \
  --path . \
  --name spectacula
```

Best-practice install for local development on this repo:

```bash
mkdir -p ~/.codex/skills
ln -s /absolute/path/to/spectacula ~/.codex/skills/spectacula
```

Upgrade if you installed with a symlink:

```bash
cd /absolute/path/to/spectacula
git pull
```

Upgrade if you installed a copied snapshot from GitHub:

```bash
rm -rf ~/.codex/skills/spectacula
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo argonavis-labs/spectacula \
  --path . \
  --name spectacula
```

After any install or upgrade, restart Codex so it reloads the skill.

Codex entrypoint:

- [SKILL.md](./SKILL.md)

Codex invocation:

```text
$spectacula <your idea>
```

Examples:

```text
$spectacula help
```

```text
$spectacula Build a full implementation-ready spec for CRUD operations for Erlang-based OTP agents.
```

```text
$spectacula spec-audit docs/spectacula/specs
```

```text
$spectacula spec-upgrade docs/spectacula/specs/evidence-first-insight-detail.md
```

Important:

- Installing the skill does not make this repository the home for your live specs.
- Live specs should be stored in the user's active project repo under `docs/spectacula`.
- Use the bootstrap script or copy the template into the target repo before first use.

## Install And Upgrade In Claude

Official Claude best practice is:

- use a plugin marketplace for shared installs and updates
- use `--plugin-dir` only for local development and testing

This repo now includes a marketplace manifest at [.claude-plugin/marketplace.json](./.claude-plugin/marketplace.json), so you can install it with Claude's marketplace flow.

Best-practice install from GitHub:

```text
/plugin marketplace add argonavis-labs/spectacula
/plugin install spectacula@argonavis-labs
```

Choose installation scope through the `/plugin` UI if you want `user`, `project`, or `local` scope explicitly. The CLI form also works:

```bash
claude plugin install spectacula@argonavis-labs --scope project
```

Best-practice upgrade from the marketplace:

```text
/plugin marketplace update argonavis-labs
/reload-plugins
```

Notes:

- third-party marketplaces have auto-update disabled by default in Claude; enable it in `/plugin` -> `Marketplaces` if you want automatic updates at startup
- if Claude reports that a restart is required after plugin changes, restart Claude Code
- Spectacula currently ships skills and agents, not LSP servers, so `/reload-plugins` is normally enough

Best-practice local development flow:

```bash
claude --plugin-dir /absolute/path/to/spectacula
```

Then invoke the plugin as:

```text
/spectacula:spectacula
```

If you are using `--plugin-dir`, upgrading is just updating the local repo and restarting or rerunning Claude:

```bash
cd /absolute/path/to/spectacula
git pull
```

You can still copy the prompt from [references/claude-portable-prompt.md](./references/claude-portable-prompt.md) into Claude project instructions or an agent definition when a plugin is not available.

Keep using the same `docs/spectacula` directory contract so Codex and Claude share the same source of truth.

Plugin files:

- Manifest: [.claude-plugin/plugin.json](./.claude-plugin/plugin.json)
- Marketplace: [.claude-plugin/marketplace.json](./.claude-plugin/marketplace.json)
- Skill: [skills/spectacula/SKILL.md](./skills/spectacula/SKILL.md)
- Subagents: [agents](./agents)

Claude Code entrypoint:

- `/spectacula:spectacula`

Claude usage examples:

```text
/spectacula:spectacula help
```

```text
/spectacula:spectacula Build a full implementation-ready spec for CRUD operations for Erlang-based OTP agents.
```

```text
/spectacula:spectacula spec-audit docs/spectacula/specs
```

```text
/spectacula:spectacula spec-upgrade docs/spectacula/specs/otp-agent-crud.md
```

Available Claude plugin subagents:

- `spectacula-architect`
- `spectacula-implementer`
- `spectacula-reviewer`
- `spectacula-status`

### Parallel / Swarm Execution In Claude

Claude's docs distinguish subagents from agent teams:

- use subagents for focused workers that report back to the lead
- use agent teams when teammates need to communicate and coordinate with each other

Agent teams are experimental and must be enabled first. Add this to Claude `settings.json` or set it in the environment:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Then start Claude with the plugin:

```bash
claude --plugin-dir /absolute/path/to/spectacula
```

Example team prompt:

```text
Create an agent team for this approved Spectacula spec. Use one spectacula-architect teammate to split the work into safe parallel tasks, two spectacula-implementer teammates for separate workstreams, and one spectacula-reviewer teammate to compare the result against the spec and verification gates. Avoid file conflicts and keep docs/spectacula resume context current.
```

See [references/claude-agent-teams.md](./references/claude-agent-teams.md) for recommended patterns.

## Bootstrap A User Repo

Create the working `docs/spectacula` tree in a user repo with:

```bash
~/.codex/skills/spectacula/scripts/spectacula bootstrap /path/to/project-repo
```

If already inside the target repo:

```bash
~/.codex/skills/spectacula/scripts/spectacula bootstrap .
```

This creates:

- `docs/spectacula/specs`
- `docs/spectacula/ready`
- `docs/spectacula/inprogress`
- `docs/spectacula/done`
- `docs/spectacula/templates`
- `docs/spectacula/README.md`

Use `--include-examples` if you also want sample files copied into the target repo.

## Spectacula Lifecycle

Canonical spec text always lives in:

- `docs/spectacula/specs/<slug>.md`

Each spec also has exactly one stage manifest:

- `docs/spectacula/specs/<slug>.json`
- `docs/spectacula/ready/<slug>.json`
- `docs/spectacula/inprogress/<slug>.json`
- `docs/spectacula/done/<slug>.json`

Rules:

- Move only the JSON manifest between stage directories.
- Keep the Markdown spec fixed in `specs/`.
- Do not duplicate the full spec text in the manifest.
- Keep enough metadata to answer status questions and resume work.
- Keep `spec_path` manifest-relative, normally as `../specs/<slug>.md`.

This lifecycle lives in the user's working repo, not in the installed skill directory.

See [assets/repo-template/docs/spectacula/README.md](./assets/repo-template/docs/spectacula/README.md) for the scaffolded local workflow and [references/spectacula-lifecycle.md](./references/spectacula-lifecycle.md) for the authoritative contract.

## Quick Start

1. Run [scripts/spectacula](./scripts/spectacula) `bootstrap` against the target repo.
2. Run `scripts/spectacula new otp-agent-crud --title "OTP Agent CRUD Specification"`.
3. Use `spectacula` to clarify and draft the spec for CRUD operations for Erlang-based OTP agents.
4. Move the manifest to `ready` once approved: `scripts/spectacula move otp-agent-crud ready`.
5. Move the manifest to `inprogress` when implementation starts: `scripts/spectacula move otp-agent-crud inprogress`.
6. Run verification and final self-review.
7. If the current run uses `spectacula++`, render and apply the final vetting pass, then record the verdict.
8. Validate lifecycle state: `scripts/spectacula validate`.
9. Move the manifest to `done` only when the required review gates for the task are complete.

Example strict implementation flow:

```text
$spectacula Build a full implementation-ready spec for CRUD operations for Erlang-based OTP agents.
$spectacula++ Implement docs/spectacula/specs/otp-agent-crud.md and keep the manifest current through ready, inprogress, and done.
~/.codex/skills/spectacula/scripts/spectacula review otp-agent-crud
~/.codex/skills/spectacula/scripts/spectacula verdict otp-agent-crud passed --reason "Final vetting found no blocking gaps."
~/.codex/skills/spectacula/scripts/spectacula move otp-agent-crud done
```

## Lifecycle CLI

The command wrapper supports the routine state operations that agents otherwise have to perform by editing JSON:

```bash
./scripts/spectacula new <slug> --title "<Title>"
./scripts/spectacula status [<slug-or-manifest>]
./scripts/spectacula validate
./scripts/spectacula move <slug-or-manifest> ready
./scripts/spectacula move <slug-or-manifest> inprogress
./scripts/spectacula review [<slug-or-manifest>]
./scripts/spectacula verdict <slug-or-manifest> passed --reason "<summary>"
./scripts/spectacula move <slug-or-manifest> done
```

`validate` checks duplicate manifests, stage/path consistency, required fields, known verification statuses, and `done` gate rules. A strict run cannot move to `done` unless `verification.spec_review = "passed"` and, when `review_policy.final_vetting = "required"`, `verification.final_vetting = "passed"`.

## Codex Invocation

Invoke the skill explicitly in Codex with:

```text
$spectacula <your idea>
```

Examples:

```text
$spectacula help
```

```text
$spectacula Add CRUD operations for Erlang-based OTP agents.
```

```text
$spectacula Build a full implementation-ready spec for CRUD operations for Erlang-based OTP agents. Use repo context and existing docs.
```

```text
$spectacula++ Implement docs/spectacula/specs/otp-agent-crud.md and keep the manifest current through ready, inprogress, and done.
```

```text
$spectacula spec-audit docs/spectacula/specs and rank the weakest specs by implementation risk.
```

```text
$spectacula spec-upgrade docs/spectacula/specs/otp-agent-crud.md using repo context and the current Spectacula quality bar.
```

## Help And Best-Practice Usage

Use help when you want the workflow summary without starting work:

```text
$spectacula help
```

If you accidentally type the common typo:

```text
$spectacular help
```

Spectacula should treat that as a request for help and return the same usage guidance.

Best-practice prompt patterns:

- New spec from a short idea:

```text
$spectacula Add CRUD operations for Erlang-based OTP agents.
```

- New spec with stronger steering:

```text
$spectacula Add CRUD operations for Erlang-based OTP agents. Match this reference in depth and structure. Use repo context and make reasonable assumptions.
```

- Audit all specs:

```text
$spectacula spec-audit docs/spectacula/specs
```

- Upgrade one weak spec:

```text
$spectacula spec-upgrade docs/spectacula/specs/<slug>.md
```

- Check status:

```text
$spectacula What is the status of <slug>?
```

- Drive implementation from an approved spec:

```text
$spectacula Implement docs/spectacula/specs/<slug>.md and keep the manifest current through ready, inprogress, and done.
```

- Drive implementation with required final vetting:

```text
$spectacula++ Implement docs/spectacula/specs/<slug>.md and keep the manifest current through ready, inprogress, and done.
```

- Render the local pre-PR final vetting prompt:

```bash
~/.codex/skills/spectacula/scripts/spectacula review <slug-or-manifest>
```

## Final Vetting Command

When Spectacula is used for implementation work, you can choose the review strength on each call:

- `$spectacula ...` keeps `review_policy.final_vetting = "off"`
- `$spectacula++ ...` sets `review_policy.final_vetting = "required"`

When the stricter alias is active, the recommended gate is:

- native verification passes
- `verification.spec_review` passes after a final self-review against the canonical spec
- `verification.final_vetting` passes after the reviewer prompt is applied as a separate final check

Render the final vetting prompt from the command wrapper:

```bash
~/.codex/skills/spectacula/scripts/spectacula review
```

For local development inside this repository:

```bash
./scripts/spectacula review
```

There is also a direct shorthand command for the stricter path:

```bash
~/.codex/skills/spectacula/scripts/spectacula++
./scripts/spectacula++
```

If there is exactly one active manifest in `docs/spectacula/inprogress`, the command resolves it automatically. You can also target a specific slug or manifest path:

```bash
~/.codex/skills/spectacula/scripts/spectacula review my-spec
~/.codex/skills/spectacula/scripts/spectacula review docs/spectacula/inprogress/my-spec.json
```

The command renders the reviewer prompt plus the active repo/spec/manifest context so Codex or Claude can apply it as the final vetting pass. Record the outcome with `spectacula verdict <slug-or-manifest> passed|failed --reason "<summary>"`. A failed verdict keeps the work in `inprogress`; a passed verdict still requires a deliberate `spectacula move <slug-or-manifest> done`.

The built-in reviewer prompt is modeled after a PR merge gate, but adapted for local pre-PR use:

- start with the local diff, not the docs
- scale review depth as Quick, Standard, or Deep based on risk
- keep the pass read-only
- check correctness, boundaries, security, consistency, and entropy
- block only on actionable, substantive issues

Typical strict workflow:

1. Draft and approve the spec with `$spectacula ...`.
2. Implement with `$spectacula++ ...` so the manifest records `review_policy.final_vetting = "required"`.
3. Run `spectacula review` or `spectacula++` to render the diff-first final vetting prompt.
4. Apply that prompt as a separate read-only review pass.
5. Record the verdict in `verification.final_vetting` and move to `done` only if it passes.

## Examples And Templates

- Templates: [assets/repo-template/docs/spectacula/templates](./assets/repo-template/docs/spectacula/templates)
- Example spec and manifest: [assets/repo-template/docs/spectacula/examples](./assets/repo-template/docs/spectacula/examples)

## Development

Validate the skill package:

```bash
PYTHONPATH=/tmp/skill-creator-deps python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
python3 scripts/validate_skill_best_practices.py .
python3 scripts/spectacula.py validate
python3 -m py_compile scripts/*.py
git diff --check
```

Test the Claude plugin locally:

```bash
claude --plugin-dir .
```
