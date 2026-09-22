# Knowledge Base

This directory holds **verified information only** — never content invented
or inferred by the LLM. It is deliberately separate from `app/rules/`:

- `app/rules/` answers *"is this person eligible?"* (deterministic, and
  currently placeholder pending legal verification).
- `app/knowledge/` answers *"what is the process / what documents / who do
  I contact?"* (reference material, cited to a source).

## Files

- `sources.py` — the source-of-truth registry (`SOURCE_REGISTRY`). Every
  fact surfaced to a user should trace back to an entry here, with an
  organisation, a URL where available, and a `content_verified_for_automation`
  flag.
- `__init__.py` — `KNOWLEDGE_STRUCTURE`, the actual content items (process
  guides, checklists, form references, referral list), each tagged with
  the relief type(s) it applies to and the source(s) it comes from.

## Status (v0.2)

Every `content` field in `KNOWLEDGE_STRUCTURE` is currently a `TODO(clearpath)`
placeholder. The **structure** is production-ready; the **content** awaits
material from ClearPath's legal team and partner organisations (DOJ, SAPS).

Several official reference URLs have already been added to `sources.py`
(e.g. the DOJ expungements overview page, gov.za's summary page) as
starting points for that content — they are marked `OFFICIAL` but
**not yet** `content_verified_for_automation=True`.

## How to add verified content

1. Confirm the source is current (re-check the URL; government pages move).
2. Add or update the entry in `sources.py`:
   - Set `source_type` (`OFFICIAL`, `CURATED`, or `UNVERIFIED`).
   - Set `verified_date` to today's date once checked.
   - Only set `content_verified_for_automation=True` once a legal reviewer
     has approved using this source's specific facts inside `app/rules/`
     logic — citing a source and encoding it as pass/fail logic are two
     different bars.
3. Update the matching item's `content` field in `__init__.py` with the
   verified material, in plain language, citing the source ID(s).
4. Update or add a test in `tests/test_knowledge.py` confirming the item
   now has non-placeholder content and a `verified_date`.

## Principles

- No invented information. If it isn't sourced, it doesn't go in here.
- Every item cites a source (`source_ids`), even if that source is still a
  `TODO`.
- Content that is safe to *cite* to a user is not automatically safe to
  *encode* as eligibility logic — see `app/rules/cannabis_cppa.py` for why
  that distinction matters.
- Nothing here is ever presented as more current than its `verified_date`.
