# Compass — Rubric Index

One rubric per **agent**. Modules get unit tests instead (see `MODULES_unit_tests.md`).
Every rubric shares the same shape: what the step does · what it reads in · what it outputs ·
0–3 checks with Strong/Weak examples · one **Fitness** grade (A–F) · a **fix lever** on every
sub-3 check · what it is explicitly NOT graded on · open questions for Nick.

| # | Step | Kind | Rubric | Checks | Graded on |
|---|---|---|---|---|---|
| 1 | **R1 Profile** | agent | `R1_profile_rubric.md` (v3) | 4 (ch.1 is a GATE) | its internal profile object |
| 2 | **Match Key** | agent | `MatchKey_rubric.md` (v3) | 3 (+GATE) | the retrieval anchor |
| 3 | Match & Rank | module | `MODULES_unit_tests.md` | — | unit tests |
| 4 | **Gap Analyst** | agent | `GapAnalyst_rubric.md` (v1) | 6 | the gap map |
| 4b | **R4 Strategy** | agent | `R4_strategy_rubric.md` (v3) | 4 | selected moves + tensions |
| 5 | **R5 Two Paths** | agent | `R5_twopaths_rubric.md` (v3) | 4 (+GATE) | target & stretch variants |
| 6a | **R6 Plan** | agent | `R6_plan_rubric.md` (v3) | 4 | goals & tasks |
| 6b | **R7 Recommendations** | agent | `R7_recommendations_rubric.md` (v3) | 4 (+GATE) | one task's options |
| 7 | **R9 Writer** | agent | `R9_writer_rubric.md` (v3) | 5 | the document a parent reads |
| 8 | **R8 Critic** | agent | `R8_critic_rubric.md` (v3) | 4 | its findings, vs seeded defects |
| — | **Profile Comparisons** | supplement | `Comparisons_rubric.md` (v1) | 5 (+GATE) | the two-page evidence pack |

## v3 — all rubrics now match the R1 v2 format
Every rubric is now written the way R1 v2 is, because that format does work the earlier ones
didn't: a **running example (Maya) carried through every check**, the output object specified
**field by field with which check it supports and who downstream uses it**, an explicit
**scoring table**, and each check written as **Plain meaning → Why it matters → What we look for
→ Strong / Weak / Broken → Fix**. Each also carries a **Design note (decided)** recording a real
choice, and **Open questions for Nick** that are decision-ready.

Lengths are now comparable: R1 209 lines · R4 205 · R9 212 · R7 193 · R5 190 · R6 189 ·
R8 174 · Match Key 165.

## What v2 changed (R4–R9 and Match Key)
Every rubric now has **4–5 checks, not 6–7**, a **GATE where one genuinely exists**, and **★ marks
on the checks that carry the grade**. Three things were cut across the board:
- **"Stays in its lane"**, which had been pasted into five rubrics. Where a boundary is real it is
  a validator assertion; as a graded check it was filler.
- **Schema-shaped checks** — term placement, field completeness, "never rendered". A validator
  tests those better and faster than a grader.
- **Double-counted checks** — R7 asked "does it fit" three separate ways; R9 split "don't be
  vague" across two.

And each gained **the outcome check it was missing** — the one that asks whether the step did its
job, not just whether it followed the rules: R4 *does it produce a spike*; R6 *is the next 90 days
actionable*; R7 *is it bookable today*; R9 *does the parent know what to do, and is their worry
answered*; R5 *is fit computed rather than asserted*; Match Key *did retrieval actually work*.
A rubric where every check weighs the same is a rubric that says nothing matters most.

## The supplement is not an afterthought
`Comparisons_rubric.md` covers the two-page Profile Comparisons pack. It matters more than its
length suggests: **the plan cannot honestly state this student's odds** — the corpus is
self-selected and a published rate belongs to the school, not the child — so the supplement is
the honest substitute. Instead of asserting a probability it shows real applicants and what their
credentials bought. Calibration by receipts.

Two consequences worth holding onto: its tiers are **relative to this student's bands**, so the
same applicant can be gold for one family and green for another; and its **rejection lists must
survive the tone rules** (the Critic carries an explicit carve-out) — they are the calibration,
not negativity about the child.

## The fix levers (same across every rubric)
`FIX_PROMPT` · `ASK_PARENT` · `CHANGE_INTAKE` · `CHANGE_SCHEMA` · `BAD_INPUT`
A grade without a lever is a complaint. **When an agent scores low, check its inputs before
rewriting its prompt** — module bugs surface as agent failures.

## Where each boundary sits (the line that keeps the rubrics from sprawling)
- **R1 describes** → **Gap Analyst diagnoses** → **R4 decides** → **R5 forks (target/stretch)** →
  **R6 schedules** → **R7 sources** → **R9 writes** → **R8 checks the writing.**
- Numbers belong to modules at every step. An agent that states a number it wasn't handed is
  a bug, not a style issue.
- The parent-facing "sounds like my kid" judgment lives with **R9**, not R1 — by design.

## Running them
```
python evals/grade_agents.py out/<run>.state.json   # per-agent, on each agent's own object
python evals/grade.py        out/<run>.plan.json    # R9's writing + module numbers
```
`grade_agents.py` currently implements R1 and Gap Analyst. The four newer rubrics
(R4, R6, R7, R9, R8) are written but not yet coded — they need a real run
(`LLM_MODE=real --dump-state`) to grade against, since mock objects would only measure the schema.

## Status
| Rubric | Written | Coded in grader | Has real output to grade |
|---|---|---|---|
| R1 | yes | yes | no (mock) |
| Gap Analyst | yes | yes | no (mock) |
| Match Key | yes | no | no |
| R5 Two Paths | yes | no | **step does not exist in the engine yet** |
| R4 / R6 / R7 / R9 / R8 | yes | no | no |
