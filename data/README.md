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
| Application rows | 30,414 after the explode |
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

## The program / competition registry

Debate is one source, not the shape of the system. Three files, one
contract:

| File | Role |
|---|---|
| `sources.json` | **The registry.** One entry per database: what it covers, which adapter reads it, when it was verified, its refresh cadence, and what is still missing. This is the file you edit when you add a competition database. |
| `programs.csv` | **The common schema.** Every source resolves to these columns, whatever shape it arrived in. |
| `tabroom_circuits.csv` | A raw source, kept exactly as it came. The adapter does the fitting — never edit a source file to match the schema. |

### Adding a database

1. Drop the raw file in `data/` under its own name.
2. Add an entry to `sources.json` with `status: "active"`, the activities
   it covers, and `verified_on`.
3. If its columns already match `programs.csv`, set `adapter` to
   `programs_csv`. Otherwise add a function to `ADAPTERS` in
   `compass/programs.py` that yields rows in the common schema.
4. Map its levels onto the six ladder rungs.
5. Check it landed:

```bash
python -c "from compass import programs; print(programs.coverage())"
```

Nothing else in the engine changes — no step, no prompt, no gate.

### The ladder

```
school → district → regional → state → national → international
```

Ordered, and load-bearing. Step 6 (Two Paths) builds a stretch path by
INTENSIFY — same activity, next rung up — which only works if every
source speaks this vocabulary. A source that invents a seventh rung
breaks that logic, so the loader blanks any level it doesn't recognise
rather than passing it through.

An empty rung is the honest answer. It says *this activity has no
verified path upward in our data yet* — which is not the same as saying
none exists, and the planner is told the difference.

### Current coverage

`coverage()` reports it live. As committed: 135 rows across debate,
speech, venture and service, from two active sources. Robotics, math,
science research, computer science, Model UN, writing, arts, music,
athletics and leadership have **no rows yet** — they sit in
`sources.json` as `planned`, with the wanted coverage written down.

Planned entries have no URL on purpose. A URL enters a data file only
after someone has opened it and confirmed what it contains — the same
rule the engine applies to recommendations.

---

## The other files

| File | What it is | Source |
|---|---|---|
| `admit_rates.json` | Published admit rates + selectivity bands, 33 schools + 13 name aliases | Web (Common Data Sets / official). Self-extends via `refresh_rates.ensure_rate()` |
| `findings.json` | The findings report, keyed by track | Supplied research |
| `catalog.csv` | The old flat catalog. Superseded by `programs.csv`; still read so nothing that referenced it breaks | Hand-verified |
| `neerav_intake.json` | The worked example intake | Real intake form |
| `sample_intake.json` | Minimal intake for smoke tests | Synthetic |

When the registry has nothing for a task, recommendations fall back to a
live verified web lookup. That works, but it costs a call per
recommendation and can't be reviewed ahead of time — growing the registry
is the cheaper fix.
