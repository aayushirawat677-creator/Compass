# `data/` — reference data the engine reads

Every number that reaches a plan comes from one of these files or from a
verified live web lookup. Nothing is invented at any layer. See
`DATA_REQUIREMENTS.md` for the full contract and
`ENGINE_FEEDBACK_LOG.md` for why each rule exists.

---

## `acceptance_rejected_college_data_verified.csv` — the corpus

**This is the dataset behind the Outcome Cards.** Without it the cards
cannot be built and the retrieval gate escalates. It is committed for
that reason.

| | |
|---|---|
| Rows | 2,723 posts (2,613 usable after dedup/validity filters) |
| Application rows | 30,414 after the explode (see below) |
| Years | 2024–2026 |
| Size | ~10 MB |
| Source | Public Reddit admissions-results posts, parsed and verified |

### It is student-level, not application-level

One row is one student. `accepted_colleges` and `rejected_colleges` are
`"; "`-separated lists. `data_access.load_corpus(applications=True)`
explodes those into `(student, college, result)` rows — that is what
gives the 30,414-row denominator the cards are counted against.

**Querying the raw CSV per-college will silently return nothing useful.**
This is exactly the bug the retrieval gate caught on its first live run:
`match_rank` queried a `student_id` column and a `result` value that only
exist *after* the explode, and returned 0 cards from a 30,414-row table
without erroring. Always go through `load_corpus()`.

### What it answers — and what it must never answer

| Question | Source |
|---|---|
| "What does an admit to this school look like?" | **this corpus** |
| "How selective is this school?" | `admit_rates.json` (published rates, from the web) |

The corpus **never** produces an admit rate. Two measured reasons:

1. It is self-selected — people post results they want to post.
2. 32.6% of posts omit rejections entirely, which inflates top-school
   rates by 6–7 points.

A band describes the *school's* selectivity. It never describes a
student's odds.

### Handling

Rows carry `author`, `reddit_post_link` and full `post_body` — public
posts, but traceable to individuals. Keep this repo **private**. Don't
redistribute the file outside the team, don't load it into a third-party
tool, and don't surface `author` or post text in any generated plan. The
engine only ever reads the banded and structured columns.

---

## The other files

| File | What it is | Source |
|---|---|---|
| `admit_rates.json` | Published admit rates + selectivity bands, 33 schools + 13 name aliases | Web (Common Data Sets / official). Self-extends via `refresh_rates.ensure_rate()` |
| `findings.json` | The findings report, keyed by track | Supplied research |
| `tabroom_circuits.csv` | Debate circuits by state, with tier | Tabroom |
| `catalog.csv` | Verified programs/opportunities for recommendations. **5 rows — the thinnest file here.** Growing it is a named handoff task | Hand-verified; extended by `llm.research_json()` |
| `neerav_intake.json` | The worked example intake | Real intake form |
| `sample_intake.json` | Minimal intake for smoke tests | Synthetic |

`catalog.csv` being nearly empty is why recommendations fall back to live
verified web lookup. That fallback works, but it costs a call per
recommendation and can't be reviewed ahead of time — growing the catalog
is the cheaper fix.
