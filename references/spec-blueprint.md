# Specification Blueprint

Use this blueprint as the default shape for long-form specs. Reorder or trim sections to fit the request, but keep the document decision-heavy and concrete.

## Table of Contents

1. Detail Floor
2. Style Signals To Mirror
3. High-Rigor Format
4. Contract-Heavy Service Spec
5. Repository-Backed Feature Spec
6. Recommended Section Menu
7. Section Patterns
8. Formatting Rules
9. Light-Weight Variant
10. Final Review Pass

## Detail Floor

When Spectacula is asked for an implementation-ready technical spec, detail is the default, not an optional extra.

Use the high-rigor or contract-heavy formats by default when any of these are true:

- the user invokes Spectacula for software, systems, workflows, protocols, migrations, or repository-backed feature work
- the user provides a long-form reference spec with numbered sections, subsections, tables, appendices, or validation checklists
- the output is intended to guide implementation rather than just discussion

In those cases:

- treat the reference spec as the minimum acceptable depth bar
- prefer full sections with explanatory prose over short bullet-only summaries
- include subsections, contracts, and validation material when they reduce guesswork
- do not collapse to the light-weight variant unless the user explicitly asks for a brief, draft, memo, or short version

## Style Signals To Mirror

When the user provides an example spec, mirror the structural signals before you mirror the wording:

- Title line: `# <Name> Specification`
- Optional preamble metadata lines such as `Status:`, `Purpose:`, or `Audience:`
- Numbered top-level sections with numbered subsections
- Tables for explicit contracts and default values
- Pseudocode for execution loops, routing, or lifecycle logic
- Validation matrices and implementation checklists near the end
- Appendices for optional extensions, examples, or exhaustive references

## High-Rigor Format

Use this format when the user asks for a full technical spec or provides an example similar to an RFC or architecture document:

```md
# <Project or System> Specification

Brief summary paragraph.

---

## Table of Contents

1. Overview and Goals
2. Scope and Non-Goals
3. Users, Actors, or Stakeholders
4. Functional Requirements
5. Non-Functional Requirements
6. Proposed Design
7. Interfaces and Data Contracts
8. Workflows and State Transitions
9. Failure Modes and Safeguards
10. Operations and Observability
11. Security, Privacy, and Compliance
12. Rollout, Migration, or Adoption Plan
13. Test Plan
14. Definition of Done
15. Open Questions / Assumptions
```

## Contract-Heavy Service Spec

Use this shape when the spec describes a service, orchestrator, agent runtime, protocol, workflow engine, or other operational system with explicit contracts:

```md
# <Service> Specification

Status: Draft v1
Purpose: Define the service, runtime contract, and validation scope.

## 1. Problem Statement
## 2. Goals and Non-Goals
## 3. System Overview
## 4. Core Domain Model
## 5. External or Repository Contract
## 6. Configuration Specification
## 7. State Machine or Lifecycle
## 8. Scheduling, Execution, or Control Flow
## 9. Workspace / Data / Resource Safety
## 10. Integration Protocols and Interfaces
## 11. Logging, Status, and Observability
## 12. Failure Model and Recovery
## 13. Security and Operational Safety
## 14. Reference Algorithms
## 15. Test and Validation Matrix
## 16. Implementation Checklist
## Appendix A. Optional Extensions
```

Use this variant when the document needs to define:

- clear system boundaries
- typed entities and normalized identifiers
- configuration precedence and defaults
- runtime states and transitions
- integration contracts
- failure classes and recovery behavior
- conformance tests and implementation gates

## Repository-Backed Feature Spec

Use this shape when the request is a feature inside an existing product or codebase and the user still wants an implementation-ready document rather than a short product brief:

```md
# <Feature> Specification

Status: Draft v1
Purpose: Define the feature, affected systems, implementation contract, and validation scope.

## 1. Overview and Goals
## 2. Current State and Problem
## 3. Scope and Non-Goals
## 4. UX / Interaction Model
## 5. Functional Requirements
## 6. Data and Domain Model
## 7. Backend / Service / Context Changes
## 8. Frontend / UI / Rendering Changes
## 9. Observability and Instrumentation
## 10. Failure Modes, Edge Cases, and Backward Compatibility
## 11. Rollout / Migration Plan
## 12. Test Plan and Validation Matrix
## 13. Definition of Done
## 14. Open Questions / Assumptions
```

This variant is the right default for requests like:

- “build this dashboard feature”
- “add this workflow to the existing app”
- “design this repo-backed UI change”
- “write the implementation spec for this product behavior”

For this variant, include:

- current codebase context and affected modules when known
- exact user-visible behavior
- persisted data and fallback behavior
- backend and frontend responsibilities
- instrumentation and success signals
- explicit acceptance checks and implementation gates

## Recommended Section Menu

Pick from these sections based on the artifact type:

| Section | Use it when | Typical contents |
|---|---|---|
| Overview and Goals | Always | Problem statement, desired outcome, why now |
| Scope and Non-Goals | Scope can drift | In-scope v1, excluded work, future work |
| Users / Actors | Humans or systems interact with the design | Roles, responsibilities, personas, external systems |
| Functional Requirements | Behavior must be testable | Capabilities, actions, invariants, business rules |
| Non-Functional Requirements | Quality constraints matter | Performance, cost, scale, reliability, UX, compliance |
| Proposed Design | The solution needs structure | Components, responsibilities, data flow, control flow |
| Core Domain Model | Runtime entities matter | Typed records, IDs, normalization rules, state carriers |
| External / Repository Contract | Behavior depends on owned files or external config | File formats, schema contracts, environment resolution, validation |
| Configuration Specification | Runtime behavior is configurable | Source precedence, defaults, coercion, reload semantics |
| Interfaces and Data Contracts | Boundaries matter | APIs, schemas, events, configs, storage contracts |
| Workflows and State | The design changes over time | Sequences, lifecycle, routing, state machines |
| Reference Algorithms | Execution order must be unambiguous | Poll loops, reconciliation, retry handling, scheduling pseudocode |
| Failure Modes and Safeguards | Failure handling matters | Retries, fallback, operator intervention, edge cases |
| Operations and Observability | The system must run in production | Logging, metrics, tracing, dashboards, ownership |
| Security / Privacy / Compliance | Regulated or sensitive data exists | Auth, authz, secrets, retention, policy constraints |
| Rollout / Migration | Existing systems or users are affected | Phasing, cutover, compatibility, backfills |
| Test Plan | Implementation readiness matters | Unit, integration, e2e, fixtures, parity checks |
| Validation Matrix | Conformance must be provable | Enumerated behaviors that must pass |
| Definition of Done | Review needs a clear finish line | Checklist of implementation and validation gates |
| Open Questions / Assumptions | Information is missing | Assumption ledger, risks, follow-up decisions |

## Section Patterns

Use these subsection patterns when they add clarity:

- `1.1 Problem Statement`, `1.2 Goals`, `1.3 Design Principles`
- `4.1 Core Requirements`, `4.2 Edge Requirements`, `4.3 Explicit Non-Requirements`
- `6.1 Architecture`, `6.2 Component Responsibilities`, `6.3 Sequence of Operations`
- `7.1 API Surface`, `7.2 Data Model`, `7.3 Configuration`
- `9.1 Expected Failures`, `9.2 Operator Recovery`, `9.3 Hard Failures`
- `10.1 Launch Contract`, `10.2 Startup Handshake`, `10.3 Streaming / Event Processing`
- `15.1 Parsing`, `15.2 Validation`, `15.3 Runtime Behavior`, `15.4 Integrations`
- `16.1 Required for Conformance`, `16.2 Optional Extensions`, `16.3 Operational Validation`

## Formatting Rules

- Use tables for fields, attributes, options, policies, enums, and comparison points.
- Use pseudocode for routing rules, orchestration loops, validation logic, and nontrivial state transitions.
- Use checklists for definition of done, parity matrices, rollout gates, and test matrices.
- Use numbered sections and subsections when the output is implementation-facing.
- State defaults explicitly.
- State precedence rules explicitly when multiple configuration layers exist.
- State implementation boundaries explicitly: what the system owns, what extensions own, and what remains out of scope.
- Distinguish facts from assumptions when the source material is incomplete.
- Expand terse requirements into prose that explains behavior, source of truth, fallback behavior, and validation expectations.

## Light-Weight Variant

Use this shorter shape when the user wants a brief spec but still expects rigor:

1. Overview
2. Scope and Constraints
3. Proposed Design
4. Key Requirements
5. Risks and Edge Cases
6. Validation Plan
7. Open Questions / Assumptions

## Final Review Pass

Before delivering the spec, check these points:

- Can an engineer implement from this document without guessing the core flow?
- Can an operator understand runtime behavior, failure handling, and safety boundaries?
- Can a reviewer see what is explicitly out of scope?
- Are the acceptance criteria concrete enough to test?
- Are unresolved questions isolated instead of mixed into requirements?
