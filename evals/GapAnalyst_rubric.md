# Gap Analyst — Job, Outputs & Grading Rubric (v1)

*The step between the profile (R1) and the strategy agent (R4). It measures the distance between the kid and similar admitted students. Written to discuss and refine, not final.*

---

## The big idea, in one minute

**What it does.** The Gap Analyst takes the kid's profile and a set of *similar admitted students*, and reports — factually and completely — **every real difference** between them. It answers one question: **"Where does this kid stand versus kids who got in?"**

**What it does NOT do.** It does not decide which gaps *matter*, and it does not say how to close them. It **reports the gaps**; **R4 decides** which are worth acting on for this kid and builds the plan. Diagnose, don't prescribe.

**Where it sits:**
1. **R1** — the profile (done).
2. **R2** — pulls similar **admitted** students from the Reddit database, matched on **college + major** (the kid's declared schools + intended major). Admits only.
3. **R3b** — a data-availability check: do we even have admit cards for this school? (For a young kid there is **no "today tier"** — GPA/SAT don't exist yet, so tiers can't be computed here. Tiers are computed later, by R5, on the *projected* profile once a plan exists.)
4. **→ Gap Analyst** — kid vs. those admits → the **gap map.** *(this doc)*
5. **R4** — picks which gaps to close and plans the moves.

**Key things we decided** (so the doc reads in context):
- **Admits only** — no rejection data. The Gap Analyst compares the kid to kids who got in.
- **Match on college + major only** — *not* on academic band or achievements. The kid is in grade 8–10 and the admits are grade 12; you can't "peer-match" a profile that isn't finished yet. The admits are a **target**, not peers.
- **Filter non-replicable admits** — drop or flag admits who got in via something the kid can't copy (recruited athlete, legacy, donor). Otherwise "the gap is: be a recruited athlete" — useless.
- **Grade-aware** — for a grade-8 kid, "missing research" is a *roadmap item with runway*, not a deficit. For a grade-11 kid the same gap is *urgent*. Same data, different meaning by years remaining.
- **No "today tier" for a young kid** — GPA/SAT and most of the profile don't exist yet, so you can't say "he can/can't get into MIT" up front. College tiers are an **output of the plan** (computed later by R5 on the projected profile), never an input here. This step only measures the distance to the target admits.
- **Report all real gaps, including small ones** — a 0.05 GPA difference is a real gap; list it with its size. R4 decides it's trivial. The Gap Analyst never pre-filters for importance.
- **Numbers come from a deterministic tally, not the LLM** — the counts ("7 of 10 admits") and GPA ranges are computed in code over the retrieved admits; the Gap Analyst *interprets and categorizes*, it doesn't count.

Running example: **Maya, Grade 9** — robotics spine at *regional* level, GPA 3.9, applying to CMU (reach) for CS. Similar CMU-CS admits typically had a *national* robotics result and an independent research project; their GPA median was 3.95.

---

## What the Gap Analyst reads in

- the **profile** (R1) — with the depth-signals per activity (level, role, duration, result)
- the **target school list** — the kid's/parent's declared schools + intended major (this is what says *which* admits to pull; it replaces any "tier baseline" — there is no meaningful today-tier for a young kid)
- the **similar admits** (R2) — admits only, matched on college + major, non-replicable-hook admits filtered
- the **tally** — deterministic counts over those admits (how many had research, the GPA range, etc.)
- a **data-availability flag** (R3b) — whether each target school has enough admit cards to compare against
- the kid's **grade / years remaining**

---

## What it outputs — the "gap map"

**One internal object → R4.** No parent-facing output (the parent sees the distance later in R9's "Two Paths"). It is **complete and structured**, not ranked by importance — R4 does the ranking.

Each **gap** carries:

| Field | What it holds |
|---|---|
| `school` / `major` | which target this gap is measured against |
| `domain` | academics · a specific activity · research · awards · leadership · out-of-school program… |
| `category` | **at-or-above** (a strength) · **missing** (kid doesn't have it) · **lower-level** (has it, but lower) |
| `kid_state` | what the kid has (from R1) |
| `admit_reference` | what admits typically show |
| `level_gap` | for *lower-level* gaps: rungs on the ladder **school → regional → state → national → international** |
| `magnitude` + `within_range` | for academics: the numeric delta and whether the kid is already inside the admit range |
| `frequency` | how common among the matched admits — "7 of 10" (from the tally) |
| `grade_context` | years remaining → "roadmap, runway" vs. "urgent" |
| `evidence_ref` | which admit cards this is based on (traceable) |

Plus a **meta** block:
- schools analyzed vs. **skipped for thin data** (too few similar admits — say so, don't guess)
- how many admits were used per school, and any **non-replicable admits filtered** (and why)

Plus a **cross-school roll-up**: gaps that recur across the target list (a gap that shows up for every school is objectively more central — still R4's call to act on, but worth surfacing).

**Example gap-map entries for Maya (CMU CS):**

```
meta: { grade: 9, years_remaining: 3, admits_used: 10, filtered: "1 recruited-athlete admit excluded" }

gaps:
- domain: research
  category: missing
  kid_state: "none"
  admit_reference: "independent research + a paper or poster"
  frequency: "7 of 10 admits"
  grade_context: "grade 9 — 3 yrs runway; roadmap item, not urgent"
  evidence_ref: [admit_ids...]

- domain: robotics
  category: lower-level
  kid_state: "regional robotics result"
  admit_reference: "national robotics result"
  level_gap: "regional → national (2 rungs)"
  frequency: "6 of 10 admits"
  grade_context: "grade 9 — reachable with runway"

- domain: gpa
  category: lower-level
  kid_state: "3.9"
  admit_reference: "admit median 3.95"
  magnitude: 0.05
  within_range: true            # already inside admit range → R4 reads: trivial, hold it
  frequency: "range 3.8–4.0 across admits"

- domain: robotics (spine)
  category: at-or-above          # a strength to build on, not a hole
  kid_state: "self-directed, builds independently"
  admit_reference: "many admits' robotics was club-driven"
```

---

## The rubric — six checks, one Fitness grade

All checks roll into one **Fitness grade** (A–F) — the Gap Analyst feeds R4, so it's graded on being useful *to R4*, not on parent trust. Threaded with Maya.

### 1. Coverage
*Compared the kid across the relevant admits, for every target school and every domain — not just the obvious one.*
- **Strong:** covers CMU and her other targets; looks at academics, spine, research, awards, breadth.
- **Weak:** only checks the reach school, or only compares GPA and ignores that her robotics is regional vs. national.
- **Fix:** prompt (or upstream — R2 returned too few admits).

### 2. Accurate & grounded
*Every gap is real and traces to the kid's profile vs. real admit cards. No invented gaps, no LLM-counted numbers, no comparing against a school with too little admit data.*
- **Strong:** "6 of 10 admits had a national robotics result" — matches the tally; Maya's regional level is from R1.
- **Weak:** invents "admits averaged 5 APs" with nothing behind it, or produces gaps for a school where only 1 admit matched (should be flagged thin, not guessed).
- **Fix:** prompt (or upstream — bad tally / thin retrieval).

### 3. Correct categorization
*Each gap is the right kind — at-or-above / missing / lower-level — and the level is read correctly on the ladder.*
- **Strong:** research = missing; robotics = lower-level (regional → national, 2 rungs); the self-driven spine = at-or-above.
- **Weak:** calls robotics "missing" when she does it (it's lower-level), or misreads school-level as national.
- **Fix:** prompt.

### 4. Complete, including small & strengths *(the "don't pre-judge" check)*
*Lists ALL real differences — small ones (0.05 GPA) and strengths (at-or-above) included — because R4, not the Gap Analyst, decides what matters.*
- **Strong:** reports the 0.05 GPA gap *with within-range = true*, and flags the self-driven spine as a strength.
- **Weak:** drops the GPA gap because "it's small," or only lists deficits and never mentions where she's ahead.
- **Fix:** prompt. *(This is the direct opposite of over-filtering — completeness is the job here.)*

### 5. Structured for handoff
*Output is specific and structured — category, magnitude/level, frequency, grade context, evidence — so R4 can filter and plan without re-deriving anything.*
- **Strong:** every gap is a clean record with all fields filled.
- **Weak:** a prose blob ("she's a bit behind on a few things") R4 can't act on.
- **Fix:** prompt / schema.

### 6. Stays in its lane
*Reports differences. Does NOT rank by relevance (R4), does NOT say how to close them (R4), does NOT invent numbers (the tally does), does NOT set tiers or say "can/can't get in."*
- **Strong:** "Gap: no research output, 7 of 10 admits had one." Stops there.
- **Weak:** "Gap: no research — so she should join a lab this summer" (that's R4), or "so CMU is out of reach" (that's R5, after the plan).
- **Fix:** prompt.

**The grade:** one Fitness grade. **Checks 2, 3, 4** are the heart — accurate, correctly categorized, and complete. Fix levers are **prompt** (the reasoning) or **bad input** (thin/wrong admits from R2, wrong tally, incomplete R1 profile).

**Example read for Maya:** *"Fitness B. Gaps accurate and well-categorized, grade context right — but it dropped the 0.05 GPA gap as 'too small' (check 4: report it, R4 decides) and didn't flag the self-driven spine as a strength (check 4). Fix: prompt."*

---

## What the Gap Analyst is NOT graded on (on purpose)

- **Which gaps matter / are worth closing** → **R4.** The Gap Analyst reports all; R4 filters by relevance to the kid's profile and capability.
- **How to close a gap** ("join a lab", "enter the state championship") → **R4.**
- **The numbers themselves** (counts, GPA ranges) → the **deterministic tally** (a module) — unit-tested, not graded here.
- **Whether the kid can get in** / college tiers → **R5, after the plan.** For a young kid there is no meaningful "today tier" (no GPA/SAT yet); tiers are earned from the plan, computed on the *projected* profile — never assigned here off today's status.
- **Any prescription or relevance ranking** — listing is the job; deciding is R4's.

---

## Open questions for Nick

1. **Match key = college + major only** (no academic-band peer-matching, because the kid isn't grade 12 yet). Agree?
2. **Non-replicable-hook filter** — drop/flag admits who got in via athlete/legacy/donor. Agree, and is that data reliably in the cards?
3. **Grade-awareness** — the same gap reads as "roadmap" for a grade-9 kid and "urgent" for a grade-11 kid. Confirm the Gap Analyst should carry that framing (and that R6, the planner, uses years-remaining too).
4. **Report all real gaps, including tiny ones** (0.05 GPA), with magnitude — no pre-filtering. Confirm the "completeness now, relevance at R4" split.
5. **Numbers from a tally module, not the LLM.** Confirm we build the deterministic tally so the agent never counts.
6. **Thin-data handling** — when too few similar admits exist for a school, we flag it rather than guess. Confirm the minimum-admits threshold is a product call.

---

*Sits between R1 (profile) and R4 (strategy). Next: R4 turns this gap map into the actual plan — and that's where "which gaps matter" and "baseball-card specificity" get graded.*
