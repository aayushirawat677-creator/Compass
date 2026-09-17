# Match Key (Step 2) — Grading Rubric (v3)

*How we grade the retrieval anchor. Written to discuss and refine, not final.*

*v3 change: rewritten to the R1 v2 format. v2 had dropped "stays backend" as a graded check (it's a validator assertion) and promoted retrieval sufficiency to a gate; that holds.*

---

## The big idea, in one minute

**What the Match Key does.** It projects the R1 profile forward just far enough that similarity to grade-12 admits becomes meaningful, then hands that to retrieval. It answers one question: **"Which admitted students is this kid most like?"** Nothing else.

**Naming, because this caused real confusion.** There are two card-shaped objects in this system:
- **The Match Key** (this step) — a **search query in the shape of a card**. Nobody sees it. Once retrieval is done it has no further purpose.
- **The Outcome Card** (pages 3 and 5) — a different artifact built much later from the finished plan.

The word **"projected" belongs to this step** and must never reach a parent. It leaked once, onto a card label, and that is how the confusion started.

**Why the step exists at all.** You cannot match a grade-8 profile directly against grade-12 admits — the kid isn't finished yet. The Match Key bridges that gap.

**The failure that matters, and it is quiet.** A Match Key describing a *generic strong applicant* retrieves generic admits — and every gap downstream is then measured against the wrong people. **Garbage in at step 2 corrupts steps 4, 5 and 6 without ever looking wrong.** The PDF comes out complete and plausible. This is the only step whose failure is invisible all the way to the end, which is why its gate is the strictest in the pipeline.

**The Match Key gets ONE grade: a Fitness grade** — is the comparison set it produced good enough to measure a real kid against?

**How to read a low score — every miss points to one fix:**
- **Fix the prompt** — the key was generic, or cloned one admit.
- **Bad input** — the corpus genuinely has too few admits for that school and major.
- **Change the schema** — no slot for the retrieval result to be inspected.

Running example: **Maya, Grade 9** — robotics spine, builds bots at home, CMU CS target.

---

## What the Match Key outputs

It produces **one thing: a projection object**, used only for retrieval. It is never rendered.

**Projected spine**
- what this student's own thread could look like at grade 12
- *supports check 2 · used by the retrieval module*

**Projected results / rigour**
- the level of result and academic load the pattern tends to show
- *supports check 3 · used by the retrieval module*

**Pattern notes**
- the shape of an admit to this college and major — depth, kind of result — **not one admit's résumé**
- *supports check 3 · used by the retrieval module*

**Retrieval outcome (recorded back)** ★
- `n_admits` · `n_students` · `schools_covered` · `thin_flags`
- *★ the addition that makes check 1 gradeable. Without it you cannot tell a good key from a bad one by looking — only by what came back. · used by the Gap Analyst and the runtime gate*

**Design note (decided):** the Match Key is built **before** the strategy exists, so it is necessarily a guess at the target profile. We considered re-running it after R4 produces the plan, so retrieval reflects the *actual* target — see open question 1. For now it runs once, early.

**Rule that still holds:** everything here is marked projected; **no probabilities, no tiers, no parent-facing language**, and nothing from this object is ever rendered.

---

## Scoring scale (same for every check)

| Level | Score | Means |
|---|---|---|
| **Strong** | 3 | Does the job fully. |
| **Okay** | 2 | Mostly there, small gaps. |
| **Weak** | 1 | Real problems, needs work. |
| **Missing / Broken** | 0 | Not done, or wrong. |

Retrieval sufficiency is a **gate**: if nothing usable came back, stop — the comparison set is the foundation and everything after it is fiction.

---

## The three things we grade

### 1. Retrieval actually worked  *(the GATE)*

**Plain meaning:** Did real, relevant admitted students come back?

**Why it matters:** This is the foundation of every judgment downstream. If retrieval returns nothing — or silently falls back to mock cards — the gap map compares Maya to invented people, the strategy closes invented gaps, and both Outcome Cards describe a fit to a fiction. **And the document looks entirely normal.** We shipped exactly this bug: a schema mismatch made retrieval return zero cards from a 30,414-row corpus for weeks, and nothing in the output revealed it.

**What we look for:**
- Enough matched admits for the target schools to compare against.
- The right major bucket — not just any admit.
- **No mock fallback.** Mock cards must never reach a real family's plan.
- Thin schools are flagged as thin, not quietly averaged in.

**Strong:** 38 real matched admits across her target list, right direction, no thin flags.
**Weak:** 4 admits — enough to run, not enough to trust; must be flagged thin.
**Broken:** Zero admits, or mock cards. Score 0, and the run stops.

**Fix if low:** **Fix the prompt**, or **Bad input** if corpus coverage for that school is genuinely thin.

---

### 2. Anchored in this student

**Plain meaning:** Is the projection built forward from Maya's own thread — or is it a template of a strong applicant?

**Why it matters:** A generic key retrieves generic admits, and the whole plan becomes the plan we'd write for anybody. This is where personalisation is either established or lost, several steps before anyone would notice. It is also seductive to write generically, because a generic key always retrieves *something*.

**What we look for:**
- The projected spine grows what R1 found, not what admits happened to have.
- The student's actual interests are recognisable in it.
- Where the intended major suggests a pattern the kid has no foothold in, that is noted rather than assumed away.

**Strong:** "Home-built robotics grown to a documented competition record" — unmistakably Maya.
**Weak:** "Research, olympiads, leadership" — a strong applicant with no trace of her.
**Broken:** A projection whose spine isn't her spine. Score 0.

**Fix if low:** **Fix the prompt.**

---

### 3. Pattern, not clone

**Plain meaning:** Does it capture the *shape* of an admit to this college and major — or copy one admit's activity list?

**Why it matters:** Cloning one admit narrows retrieval to near-duplicates of that person, which is both a worse comparison set and a hidden bias: whoever happened to be first in the corpus becomes the template. Capturing the pattern keeps retrieval broad enough to be representative.

**What we look for:**
- Depth, level of result and rigour described as a *tendency*, not a checklist.
- No specific competition names or unique achievements lifted from one card.
- The pattern is recognisable to someone who knows the field.

**Strong:** "A sustained technical build with an external result at regional level or above, plus advanced maths."
**Weak:** "FIRST Robotics regional finalist, USACO Silver, and a summer at CMU" — that is one person.
**Broken:** Reproduces an admit's résumé verbatim. Score 0.

**Fix if low:** **Fix the prompt.**

---

## The grade

| Letter | Meaning |
|---|---|
| **A** | Ready. The comparison set is sound. |
| **B** | Small fixes; usable. |
| **C** | Real gaps; the gap map will be shaky. |
| **D–F** | Not usable; stop — everything downstream is fiction. |

Gated on check 1. **Checks 1 and 2 carry the grade.**

**Example read for Maya:** *"Fitness B. Retrieval returned 38 real admits in the right direction and the key is clearly hers — but the pattern notes name a specific competition lifted from one card (check 3), which narrows retrieval. Fix: Match Key prompt."*

---

## What the Match Key is NOT graded on (on purpose)

- **Whether the projection is achievable** → **R4**, once a plan exists. This is a search query, not a promise.
- **Any number or tier** → modules.
- **How it reads** → nobody reads it. It has no parent-facing output at all.
- **"No numbers, never rendered"** → a **validator** assertion, checked every run. Not worth a grader's attention.

---

## Open questions for Nick

1. **Re-run after R4?** The key is built before the strategy exists, so it guesses the target profile. Re-running it once the plan is known would give a sharper comparison set — at the cost of a second retrieval pass. Worth it?
2. **Retrieval effectiveness** — is check 1 better owned here, or by the retrieval module as a unit test? It currently sits in both, as a gate and as a grade.
3. **Thin-data threshold** — what is the minimum matched admits before a school's comparison is worth making at all? It is a product call, not a technical one.

---

*Covers the Match Key (step 2). Reads R1's profile; hands a comparison set to the Gap Analyst. Never seen by a family.*
