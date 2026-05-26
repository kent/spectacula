# Spectacula

Canonical specs live in [specs](./specs). Each spec also has exactly one JSON manifest in the current stage directory:

- `specs/` for drafting and revision before approval
- `ready/` for approved specs waiting for implementation
- `inprogress/` for active implementation
- `done/` for completed work

Rules:

- Keep the Markdown spec in `specs/<slug>.md` as the source of truth.
- Move only the JSON manifest between stage directories.
- Do not duplicate the full spec body in manifests.
- Store enough metadata in the manifest to answer status questions and resume interrupted work.
- Keep `spec_path` relative to the manifest file, normally as `../specs/<slug>.md`.

Supporting directories:

- [templates](./templates) for reusable starting points
- [examples](./examples) for sample spec + manifest pairs

Recommended manifest fields:

- `spec_id`
- `slug`
- `title`
- `stage`
- `spec_path`
- `updated_at`
- `summary`
- `next_action`
- `resume_context`
- `history`
- `review_policy`

Recommended workflow:

1. Create the draft with `spectacula new <slug> --title "<Title>"`, or copy the templates manually.
2. Draft until approved.
3. Move the manifest to `ready` with `spectacula move <slug> ready`.
4. Move the manifest to `inprogress` when implementation starts.
5. Run verification and final self-review against the spec.
6. If the current Spectacula call is the stricter form (`spectacula++`), run the final vetting pass and record the result with `spectacula verdict <slug> passed|failed`.
7. Run `spectacula validate`.
8. Move the manifest to `done` only after the required review gates for the current task are complete.

Useful commands:

```bash
spectacula status [<slug-or-manifest>]
spectacula validate
spectacula review [<slug-or-manifest>]
spectacula verdict <slug-or-manifest> passed --reason "<summary>"
spectacula move <slug-or-manifest> done
```
