# R6 Plan (Goals & Tasks) — Grading Rubric (v3)

*How we grade the schedule the system builds. Written to discuss and refine, not final.*

*v3 change: rewritten to the R1 v2 format. v2 had cut seven checks to four by moving term-placement to the validator and folding the summer ladder into staging; that holds.*

---

## The big idea, in one minute

**What R6 does.** R6 takes the moves R4 chose and lays them across the student's remaining grades as goals and tasks. It answers one question: **"When does each of these happen?"** Nothing else.

**Two kinds of thinking — R6 does neither of the interesting ones:**
- R4 decided **what**. R7 decides **which program**. R6 decides **when**, and whether the family can carry it.
- R6 never reopens the strategy. If a move looks wrong while scheduling it, that is an R4 failure surfacing here — flag it, don't quietly drop it.

**What the plan is made of** (two parts):
- **The current year** — split into Fall / Spring / Summer, with dated tasks a parent can act on.
- **The multi-year arc** — grades beyond this one, deliberately coarse.

**The rule that shapes everything: the horizon.** Only the current year gets dated, specific tasks. Later grades stay at the level of goals, because no date or program that far out can be confirmed — and **the plan says so to the parent**, rather than leaving later years looking thin. Inventing a named program for grade 11 is a defect, not thoroughness.

**R6 gets ONE grade: a Fitness grade** — is this schedule real enough for R7 to source against and for a family to actually run?

**How to read a low score — every miss points to one fix:**
- **Fix the prompt** — R6 had the moves and scheduled them badly.
- **Bad input** — R4 gave no dependency order, or no capacity was carried through from R1.
- **Change the schema** — no slot for terms, or for the horizon disclosure.
- **Ask the parent** — weekly hours were never collected.

Running example: **Maya, Grade 9** — robotics spine, dance, tight budget, rural, perfectionist who needs a second attempt; four years of runway.

---

## What R6 outputs

R6 produces **one thing: a plan object.** The roadmap page a parent reads is written later by R9 from this.

**Current year** — the only part with dates
- `terms`: Fall / Spring / Summer, each with `goals`, and each goal with `tasks`
- each task: `term` · `text` · `by_when` · `which_move` (the R4 move it serves)
- *supports checks 1 and 2 · used by R7 (which sources each task), R9*

**Multi-year arc** — grades beyond this one
- per grade: `stage` (explore / commit / deepen) · `goals` · **no dates, no program names**
- *supports checks 2 and 3 · used by R9*

**Capacity record** ★
- `weekly_hours_assumed` · `threads_per_grade` · `light_windows` (seasonal)
- *★ so "carryable" is gradeable rather than a vibe — supports check 4 · used by the validator*

**Horizon disclosure** ★
- the one plain sentence explaining why later years are less specific
- *★ added because later years without it read as laziness rather than honesty — supports check 3 · used by R9*

**Design note (decided):** the current year is split into **three terms**, not two semesters. Summer is where the escalation actually happens (explore → a real job → a major program), and folding it into "spring" buried the deadline that matters most. Flag for Nick if the school calendar makes this awkward.

**Rule that still holds:** **no program names, prices or contacts in this object** — that is R7. A named program here is a horizon violation and a lane violation at once.

---

## Scoring scale (same for every check)

| Level | Score | Means |
|---|---|---|
| **Strong** | 3 | Does the job fully. |
| **Okay** | 2 | Mostly there, small gaps. |
| **Weak** | 1 | Real problems, needs work. |
| **Missing / Broken** | 0 | Not done, or wrong. |

---

## The four things we grade

### 1. The next 90 days are actionable  *(the outcome check)*

**Plain meaning:** After reading this, does the parent know what to do **this month** — what to book, by when, and what needs no action yet?

**Why it matters:** This is the only part of the plan the family can act on. Grade 11 is a hypothesis; this term is a decision. A plan that is beautifully staged across five years and vague about October has failed at the one thing it was for — and that failure is invisible in a rubric that only checks structure, which is exactly why this check exists.

**What we look for:**
- Every current-term task carries a date or a clear "by when", with a few weeks of slack.
- Ordering reflects which deadlines actually close first, not narrative tidiness.
- It is explicit where **no action** is needed yet — that is information too.
- The current year reads at a visibly different altitude from grade 11.

**Strong:** "Book the counselling meeting by early October — before course selection opens." Dated, with the reason the date matters.
**Weak:** "Build study habits" in the current term, at the same altitude as a grade-11 goal.
**Broken:** A current-term deadline that has already passed by the time the plan is delivered. Score 0.

**Fix if low:** **Fix the prompt.**

---

### 2. Faithful to the strategy, and staged correctly

**Plain meaning:** Does every goal trace to a move R4 chose — and does the arc go explore → commit → deepen in the right years?

**Why it matters:** Two failures ride together here. A goal with no move behind it is R6 inventing strategy, which nobody reviewed. And wrong staging quietly wrecks a good strategy: **a profile is not built by committing at 13.** Locking the spike in grade 8 forecloses the exploration that finds the real one, and it shows up years later as a kid who quit.

**What we look for:**
- Each goal names the move it serves; no selected move silently disappears.
- **Grades 8–9 sample and confirm** what is genuinely the kid's; **grade 10 reviews, commits, drops the rest**; **11–12 specialise, lead, produce a signature result.**
- **Summers escalate** alongside it: explore or a short program → a real job or sustained service → a major program plus application work, with the spine constant beneath.

**Strong:** Grade 9 tries several robotics competition formats "to find which fits, not to lock one"; commitment lands in grade 10.
**Weak:** Three interchangeable summers, or a new activity that no move called for.
**Broken:** The spike declared and locked in the first year. Score 0 — it contradicts the plan's own logic.

**Fix if low:** **Fix the prompt.**

---

### 3. Honest horizon

**Plain meaning:** Current year specific, later years coarse — and does it *say* why?

**Why it matters:** Both halves fail differently. Over-specifying grade 11 makes a promise nobody can keep: the program may not run, the price will change, and when it does the whole document loses credibility. Under-explaining makes a careful choice look like a thin document — the parent assumes we ran out of effort. The disclosure sentence converts a limitation into a trust signal, which is the cheapest credibility we can buy.

**What we look for:**
- No named program, price, contact or registration date beyond the current year.
- Later years carry real goals, not filler.
- One plain sentence, in the parent's language, explaining the choice.

**Strong:** "This stays at goals and tasks on purpose — specific programs and dates come later, when we can confirm them."
**Weak:** Later years thin, with no explanation.
**Broken:** "Enrol in the CMU summer robotics institute, $4,200, applications open February of grade 11." Score 0.

**Fix if low:** **Fix the prompt.**

---

### 4. Carryable by this family

**Plain meaning:** Can Maya actually run this, in the hours she has, in the weeks she has them?

**Why it matters:** An overloaded plan doesn't fail loudly — it fails by attrition. The family drops the thing that felt least urgent, which is usually the spike, and the plan inverts itself. Capacity is also where a plan can accidentally insult: a lighter stretch must be expressed as a scheduling choice, never as a limitation of the child.

**What we look for:**
- Weekly hours honoured against the real number from R1.
- Activity count capped once committed — typically **two to four** threads.
- Known low-energy windows kept light, with nothing new introduced into them.
- Slack built into deadlines rather than everything landing at once.
- The reason for a lighter period is **never named** if it is sensitive.

**Strong:** One event in the spring window, nothing new added that stretch.
**Weak:** Three new commitments starting in the same month.
**Broken:** "Keep the load light in spring because of his home situation." Score 0 — correct scheduling, wrong sentence, and it is the parent's private life on a page.

**Fix if low:** **Fix the prompt**, or **Ask the parent** if weekly hours were never collected.

---

## The grade

| Letter | Meaning |
|---|---|
| **A** | Ready. Hand to R7. |
| **B** | Small fixes; usable. |
| **C** | Real gaps; fix before relying on it. |
| **D–F** | Not usable; rework. |

**Checks 1 and 4 carry the grade** — a plan that is faithful and well-staged but unrunnable this term has failed at the only part the family can act on.

**Example read for Maya:** *"Fitness B. Staging right, horizon disclosed, capacity respected — but two current-term tasks carry no date (check 1), so the parent can't tell what's urgent. Fix: R6 prompt."*

---

## What R6 is NOT graded on (on purpose)

- **Which moves were chosen** → **R4**. A bad move scheduled well is R4's failure.
- **Which program, what it costs, who to call** → **R7**.
- **Whether the family can afford a named option** → the **guardrail module**.
- **Field placement and structure** — is the summer task filed under Summer → the **validator**. It checks that in milliseconds, every run.
- **Any number or tier** → modules.
- **How the roadmap reads** → **R9**.

---

## Open questions for Nick

1. **The activity cap** — hard validator rule, or a prompt instruction R6 is graded on? We lean validator, since it's countable.
2. **Dated anchors in outer years** — does "test cycle in grade 11" cross the horizon, or is a *category* of timing acceptable where a *program* isn't?
3. **Slack** — how much is right on a current-term deadline: two weeks, a month? It should probably vary by how hard the thing is to book.
4. **Three terms vs two semesters** — see the design note.

---

*Covers R6 (goals and tasks). Reads R4's moves; hands dated tasks to R7 and the arc to R9.*
