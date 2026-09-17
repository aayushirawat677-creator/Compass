# R4 Strategy — Grading Rubric (v3)

*How we grade the strategy the system builds. Written to discuss and refine, not final.*

*v3 change: rewritten to the R1 v2 format — running example, object spec with per-field ownership, explicit scoring table, and Strong/Weak/Broken examples on every check. v2 had cut the check count from six to four; that holds.*

---

## The big idea, in one minute

**What R4 does.** R4 reads every gap between the kid and similar admitted students, and decides **which few actually matter for this kid** — then turns them into MOVES. It answers one question: **"What should this student actually do?"** Nothing else.

**Two kinds of thinking — R4 does the other one:**
- R1 and the Gap Analyst do the **reading and measuring**: *"who is this kid, and how far is he from the admits?"*
- R4 does the **deciding**: *"which of those distances are worth closing, and how hard do we push?"* This is R4's whole job, and nobody else in the pipeline is allowed to do it.

R1 **describes**; the Gap Analyst **diagnoses**; R4 **decides.** Hold that line and the rubric stays clean.

**A consequence worth stating plainly:** because R1 is forbidden from making pacing calls, **if R4 skips them, nobody makes them.** "Start low-stakes", "commit in grade 10, not now" — those decisions live here or they don't exist.

**What the strategy is made of** (four parts):
- **Selected moves** — the few gaps worth closing, each with why, priority, and how hard to push.
- **Dropped moves** — what was considered and rejected. Not noise; evidence of a real choice.
- **Tensions** — where the four voices disagreed, and which one won.
- **Pacing notes** — how gently each move is introduced, given this kid's temperament.

**Four voices that disagree on purpose.** Strategist (fit the admit pattern) · Advocate (a plan he'll finish) · Budget (sustainable in hours and money) · Skeptic (is the evidence real?). The disagreement is the product — a strategy with no disagreement recorded didn't make a trade-off, it made a list.

**R4 gets ONE grade: a Fitness grade** — is this good enough for R6 to schedule and R7 to source against? That's it.

**How to read a low score — every miss points to one fix:**
- **Fix the prompt** — R4 had what it needed and reasoned badly.
- **Bad input** — the gap map was thin, or R1 never carried the guardrails through.
- **Change the schema** — there's no slot for what we need recorded (usually `tensions`).
- **Ask the parent** — a constraint we needed was never collected.

Running example: **Maya, Grade 9** — robotics spine at *regional* level, builds bots alone at home, also dances; GPA 3.9; CMU CS is the target; perfectionist who hates failing publicly; tight budget, rural.

---

## What R4 outputs

R4 produces **one thing: a moves object.** It has **no parent-facing output** — the "Two Paths" the parent reads are built later by R5 and written by R9. Everything here is *internal*, consumed by R5 (the target/stretch fork), R6 (scheduling) and R7 (sourcing).

**Selected moves** — the few gaps worth closing
- `which_gap` (the gap id it closes) · `why` (in one line) · `priority` · `dependency_order` · `intensity` (core / stretch) · `pacing_note`
- *supports checks 1, 2 and 3 · used by R5, R6, R7*

**Dropped moves** ★
- `move` · `considered_because` · `dropped_because`
- *★ the addition that makes check 4 gradeable at all. A strategy without this looks identical to a strategy that never considered anything. · used by the human reviewer, not by a downstream agent*

**Tensions** ★
- `move` · `voice_for` · `voice_against` · `resolution`
- *★ this is the audit trail. It is what lets a human trust the choice, and what lets us debug a bad plan without re-running it. · used by the human reviewer*

**Pacing notes** (carried on each move)
- how gently to introduce it, traced to a temperament trait from R1
- *supports check 3 · used by R6 · **never rendered as a prediction about the child** — that was a real defect: "a big competition would end with him quitting by winter" is a pacing input, not a sentence a parent should read*

**Constraint application record** ★
- which constraint eliminated which candidate move
- *★ so we can tell "applied at selection" from "bolted on later" — supports check 3 · used by the validator*

**Design note (decided):** constraints are applied **during** selection, not checked afterwards by the guardrail module. The guardrail stays as a backstop, but a strategy that picks an unaffordable move and relies on being caught has already failed check 3. Flag for Nick if he'd rather R4 propose freely and let the validator filter.

**Rule that still holds:** **no numbers in this object** — no odds, tiers, or score targets. R4 decides direction; the numbers come from modules. A number here is a bug.

---

## Scoring scale (same for every check)

| Level | Score | Means |
|---|---|---|
| **Strong** | 3 | Does the job fully. |
| **Okay** | 2 | Mostly there, small gaps. |
| **Weak** | 1 | Real problems, needs work. |
| **Missing / Broken** | 0 | Not done, or wrong. |

The four checks roll up into one **Fitness grade** (A–F).

---

## The four things we grade

### 1. Does it produce a spike?  *(the outcome check)*

**Plain meaning:** Did R4 actually choose — concentrating effort on one thread taken high — or did it spread effort evenly and call that a strategy?

**Why it matters:** This is the single finding the admissions data is bluntest about: **admits list FEWER activity areas than rejects (5.8 vs 6.2)**, and what separates them is the tier of one best achievement. A strategy that adds four things at equal intensity is building the exact profile that gets rejected — while looking productive. It is also the failure that is hardest to spot, because every individual move looks sensible.

**What we look for:**
- One clear spike identified and resourced above the others.
- Everything else held steady, or subtracted. **Subtraction is a valid move** and should appear.
- The number of moves is small. More than about six for a young student means no choice was made.
- The spike is on-spine, not the most impressive-sounding option.

**Strong:** Robotics named as the spike and pushed regional → national; dance held steady; nothing new added.
**Weak:** Robotics, research, a service club and a summer course, all at "high" priority.
**Broken:** Selects every gap the Gap Analyst listed. That is a pass-through, not a strategy. Score 0.

**Fix if low:** **Fix the prompt.**

---

### 2. Built on what the kid already has

**Plain meaning:** Does the plan grow Maya's own interests toward the admit pattern, or bolt on what admits happened to have?

**Why it matters:** A move the kid has no foothold in will not survive four years — and the plan is four years long. Growing an existing thread compounds; starting a new one restarts the clock. This is also where a strategy quietly becomes generic: once you copy the admit pattern instead of growing the kid, every student's plan starts looking the same.

**What we look for:**
- Each move traces to something in R1's profile — an activity, an interest, a stated ambition.
- Where an admit pattern can be reached two ways, the one closer to the kid's existing thread wins.
- **Join, don't found.** The student goes deeper inside something that exists — a defined role, a real project, a result. Not "start a club" or "found a nonprofit": readers discount a founder title created for admissions, and a real result inside an existing group is worth more.

**Strong:** "Her home-built bots become a competition record" — the gap is closed by growing what she already does alone at night.
**Weak:** "Add independent research" because 7 of 10 admits had research, with nothing in her profile pointing there.
**Broken:** "Found a robotics outreach nonprofit." A manufactured credential, and it contradicts the join-don't-found rule. Score 0.

**Fix if low:** **Fix the prompt.**

---

### 3. Fits the kid, and the family's limits

**Plain meaning:** Will Maya actually finish these moves, and can this family actually afford and reach them? One check, because in practice they fail together.

**Why it matters:** A plan the kid abandons in March is worse than no plan — the family paid for it and lost a term. And a plan that breaks the budget isn't a stretch, it's a plan for a different family. Both failures produce the same outcome: the document gets put in a drawer.

**What we look for:**
- **Temperament used WITH its condition attached.** "Fears public failure" → the first competitive step is low-stakes with a route back, not a regional final.
- **Capacity respected** — weekly hours are a real number, not an aspiration.
- **Preference-vs-behaviour used.** If the intake says she prefers groups but everything she competes in is solo, favour a team format: she'll do better and stay longer.
- **Constraints applied at selection.** Budget, travel radius, hard-nos eliminate candidates *before* they're chosen — with the elimination recorded.

**Strong:** Drops the travel-heavy national circuit at selection (rural + tight budget), records why, and picks the regional league instead.
**Weak:** Picks a one-shot invitational as her first competition, for a kid who needs a second attempt to stay engaged.
**Broken:** Selects a $6k summer program against a stated $3–5k cap and leaves the guardrail to catch it. Score 0.

**Fix if low:** **Fix the prompt**, or **Bad input** if R1 never carried the guardrails through.

---

### 4. Shows its working  *(the trust check)*

**Plain meaning:** Can a human see what was rejected, and why?

**Why it matters:** Two reasons, and the second is the one people miss. First, it is how a reviewer decides whether to trust the plan — a choice with visible alternatives reads as a decision; the same choice with no alternatives reads as the model's first idea. Second, **it is how we debug**: when a plan is wrong, `tensions` tells us whether the strategy considered the right option and rejected it for a bad reason, or never considered it at all. Those two failures need completely different fixes, and without this record you cannot tell them apart.

**What we look for:**
- Every contested move that was dropped appears in `dropped_moves` with a reason.
- `tensions` names which voice argued for, which against, and how it resolved.
- On a constrained family, this is **not** empty. If nothing was traded away, no real constraint was applied.

**Strong:** "Strategist wanted the national robotics circuit; Budget killed it — $4k travel against a $3–5k total cap. Resolution: regional league, revisit at grade 11."
**Weak:** `dropped_moves` lists items with no reason attached.
**Broken:** Both empty, on a family with a tight budget and a rural address. Score 0 — the constraints demonstrably did no work.

**Fix if low:** **Fix the prompt**, or **Change the schema** if there's nowhere to record it.

---

## The grade

All four checks roll into one **Fitness grade:**

| Letter | Meaning |
|---|---|
| **A** | Ready. Hand it to R5/R6. |
| **B** | Small fixes; usable. |
| **C** | Real gaps; fix before relying on it. |
| **D–F** | Not usable; rework. |

**Checks 1, 2 and 4 carry the grade.** Check 3 behaves closer to pass/fail: a strategy that breaks the budget or the kid is unusable however elegant the rest is.

**Example read for Maya:** *"Fitness B. One clear spike, grown from her own bots, constraints applied at selection — but `tensions` is empty despite a tight budget (check 4), so we can't see what was traded away. Fix: R4 prompt."* One line tells you what's wrong and what to do.

---

## What R4 is NOT graded on (on purpose)

- **Which gaps exist, or how big they are** → the **Gap Analyst**. R4 only filters; inventing a gap is a Gap Analyst failure showing up here.
- **When things happen — semesters, dates, sequencing across years** → **R6**.
- **Which specific program, and what it costs** → **R7**.
- **Whether the family can afford a named option** → the **guardrail module**. R4 applies the constraint at selection; the module enforces it on the actual recommendation.
- **The target-vs-stretch split** → **R5**. R4 tags moves core/stretch; turning that into two coherent plans is a different step.
- **Any number** — odds, tiers, score targets. R4 states none by design; one showing up is a bug.
- **How any of it reads to a parent** → **R9**.

**Where R4's failures surface:** almost always as *someone else's* problem. A strategy with no spike looks like a busy roadmap (R6's fault?) or a thin card (R9's fault?). When a plan feels scattered, grade R4 before rewriting anything downstream.

---

## Open questions for Nick

1. **Empty tensions on a constrained family** — hard fail, or just a low check-4 score? We lean hard fail: it means the constraints did no work.
2. **A cap on moves** — we cap activities at 2–4 once committed. Should R4 have an explicit max *moves* for a young student, or is "produces a spike" enough?
3. **Pacing notes** — they live here now (R1 is forbidden from making them). Confirm R9 may never render a pacing note as a prediction about the child.
4. **Join-don't-found** — confirm this is an absolute rule, or are there cases where founding is genuinely right (e.g. nothing exists locally)?
5. **Constraints at selection vs. validator filtering** — see the design note. Which does Nick prefer?

---

*Covers R4 (strategy). It reads the Gap Analyst's map and hands moves to R5 (two paths), R6 (plan) and R7 (recommendations) — each graded the same way.*
