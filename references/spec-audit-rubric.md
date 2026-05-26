# Spec Audit Rubric

Use this rubric when Spectacula reviews or upgrades an existing spec.

## Table of Contents

1. Quality Bar
2. Problem Framing
3. Current-State Context
4. Requirements And Behavior
5. Design And Architecture
6. Contracts And Data Model
7. Operational Behavior
8. Validation And Done Criteria
9. Assumptions And Open Questions
10. Review Output Format

## Quality Bar

A good Spectacula spec is implementation-ready. It should let an engineer build with minimal guesswork and let a reviewer identify what is in scope, out of scope, risky, and still unresolved.

Audit against these dimensions:

## 1. Problem Framing

Check for:

- clear title and purpose
- explicit problem statement
- goals and non-goals
- audience or operator context when relevant

Common failure modes:

- starts directly with features and skips the problem
- lacks scope boundaries
- reads like notes instead of a decision document

## 2. Current-State Context

Check for:

- what exists today in the repo or product
- affected modules, workflows, or interfaces
- limitations of the current system

Common failure modes:

- describes only the future state
- forces implementers to rediscover where the feature belongs
- does not distinguish existing behavior from proposed behavior

## 3. Requirements And Behavior

Check for:

- functional requirements
- edge requirements and fallback behavior
- explicit non-requirements where scope could drift
- user-visible behavior described concretely

Common failure modes:

- requirements are short bullets without behavioral detail
- missing state, routing, or error semantics
- vague language such as "support", "handle", or "improve" with no contract

## 4. Design And Architecture

Check for:

- proposed components or affected layers
- backend, frontend, workflow, or service responsibilities
- data flow or control flow when relevant
- rationale for the chosen approach

Common failure modes:

- no architecture section at all
- only lists modules without saying what changes
- no separation of responsibilities

## 5. Contracts And Data Model

Check for:

- schemas, typed fields, interfaces, events, or payloads when relevant
- persistence rules and source-of-truth fields
- compatibility or fallback behavior for older data

Common failure modes:

- references metadata or state without defining shape
- no mention of defaults, precedence, or fallback logic
- leaves names and contracts unstable

## 6. Operational Behavior

Check for:

- failure modes
- retries, recovery, or operator handling where relevant
- observability and instrumentation
- rollout, migration, or adoption plan when existing systems are affected

Common failure modes:

- no explanation of what happens when data is missing or stale
- no metrics or instrumentation for user-facing trust features
- no rollout guidance for risky changes

## 7. Validation And Done Criteria

Check for:

- acceptance criteria
- test plan or validation matrix
- definition of done
- implementation gates when the spec will drive coding

Common failure modes:

- ends without a validation plan
- "done" is implied rather than stated
- no way to tell whether the implementation matches the spec

## 8. Assumptions And Open Questions

Check for:

- clearly marked assumptions
- unresolved decisions isolated in one place
- explicit blockers where user input is still needed

Common failure modes:

- assumptions buried in requirements prose
- unresolved choices presented as if decided
- missing questions that materially affect implementation

## Review Output Format

For `spec-audit`, report:

1. Overall verdict
2. Findings by severity
3. Missing sections or weak sections
4. Recommended upgrade plan

For `spec-upgrade`, ensure the rewritten spec:

- closes the findings that can be resolved from repo context
- records remaining assumptions explicitly
- reaches the current Spectacula depth bar instead of only patching obvious omissions
