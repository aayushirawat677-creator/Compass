# Compass Engine — data the engine needs

Everything goes in **one folder**: `compass_engine/data/`.
Nothing else needs moving. `settings.DATA_DIR` points there by default, and every path
below is overridable by an environment variable if you'd rather keep the big files
elsewhere (e.g. your Peggy folder) — see "Alternative" at the bottom.

Legend: **P1** = engine produces wrong/fake output without it · **P2** = degrades quality ·
**P3** = nice to have.

---

## P1 — the one that matters most

### 1. `acceptance_rejected_college_data_verified.csv`  ← THE BIG GAP
The verified admit/reject corpus. **One row per student-college decision.**

Feeds: `match_rank` (finding similar admitted students), the whole gap analysis,
`cohort_rates()` (real band percentages), `admit_pattern()` (observed GPA/test ranges).

Required columns (logical name → your header, editable in `settings.CORPUS_COLUMNS`):

| logical | current expected header | notes |
|---|---|---|
| student_id | `post_id` | same id repeats across that student's schools |
| college | `college_raw` | name as written |
| result | `result` | accepted / rejected / waitlisted / deferred |
| major | `major_category` | bucket used to match direction |
| gpa | `gpa_unweighted` | |
| test | `test_score` | SAT or ACT |
| activities | `activities` | free text or list |
| awards | `awards` | |

**Without it:** retrieval silently falls back to *fictional* mock cards, the gap analysis
compares the student to invented people, and every band percentage stays hand-authored.
This is the single file that turns the numbers real.

If a header differs, don't rename the file — edit `CORPUS_COLUMNS` in `settings.py`.

---

## P2 — quality

### 2. `ipeds.sqlite`
IPEDS institution data — published admit rates and test bands. Used by `tiering()` and, per
rule #16, is the ONLY source allowed for a school's own published rate (kept strictly separate
from our cohort rate). **Without it:** no published-rate anchor; selectivity context is missing.
Needs a table with institution name + admit rate; tell me the schema and I'll wire the query.

### 3. `catalog.csv`  *(a starter version is already there — 5 verified rows)*
The program catalog recommendations are drawn from. Current rows cover Neerav's Bay-Area
needs only. **Without a real one:** every task outside those 5 rows escalates to live web
research, which works but is slower, costs API calls, and re-verifies the same programs for
every family. Columns in place: name, org, category, ages_min, ages_max, format, city, state,
price, price_note, registration, contact, url, verified_on, notes.
Worth growing per region as you onboard families.

### 4. Reddit / applicant profile cards  *(not yet wired)*
The anonymised profiles behind the Profile Comparisons supplement, and the source for
calibrating what level of achievement a given tier actually requires. **Without it:** the
achievement levels on the Outcome Card stay my judgment rather than evidence.
Any structured form works — CSV or JSON with credentials, accepted list, rejected list.

---

## P3 — already in place, listed for completeness

### 5. `tabroom_circuits.csv` ✅ present
Circuit inventory. Gives the real competitive ladder per state.

### 6. `findings.json` ✅ present
The Top-10 findings report as structured claims, with source and caveat.
**Open question:** the report doesn't say whether "first-generation" means first-gen
*college* or first-gen *immigrant*. Until you resolve it, the guard stays conservative and
the 1.5x hook is not applied to a student with college-graduate parents.

---

## Where to put them

```
compass-v1-build/compass_engine/data/
├── acceptance_rejected_college_data_verified.csv   ← P1, missing
├── ipeds.sqlite                                    ← P2, missing
├── catalog.csv                                     ✅ starter present
├── tabroom_circuits.csv                            ✅ present
├── findings.json                                   ✅ present
├── profiles_cards.csv                              ← P2, missing (any shape)
└── neerav_intake.json                              ✅ present
```

## Alternative — keep the big files in the Peggy folder
If the corpus is large or lives with your other data, don't copy it. Point the engine at it:

```bash
export COMPASS_DATA_DIR="/Users/aayushi/Documents/Peggy"
# or per-file:
export COMPASS_CORPUS_CSV="/Users/aayushi/Documents/Peggy/acceptance_rejected_college_data_verified.csv"
export COMPASS_IPEDS="/Users/aayushi/Documents/Peggy/ipeds.sqlite"
```

## To run for real
```bash
export LLM_MODE=real
export ANTHROPIC_API_KEY=...        # enables the prompts AND live research
python run.py --intake data/neerav_intake.json --out out/neerav.pdf --dump-state
```
`--dump-state` writes the full per-step JSON so you can see exactly what each agent received
and returned — that's the file to read when grading a step against its rubric.
