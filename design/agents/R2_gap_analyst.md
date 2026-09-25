# `gap` — R2 Gap Analyst (prompt spec)

**Component:** R2 · Gap Analyst
**Phase:** 4 — after Match & Rank, before the Appraiser
**Model tier:** Mid. Comparison against a supplied set, not contested judgment.
**Rubric:** `evals/GapAnalyst_rubric.md`

---

## What it does / does not do

**Does:** compare this student's **current** profile to the retrieved admitted profiles and
report every real difference, completely and factually.

**Does not:**
- **Decide which gaps matter.** That is Strategy. A gap analyst that prioritises has made
  the strategic decision and hidden it inside a diagnosis.
- **Say how to fix anything.** That is Strategy and R6.
- **Compare against the PROJECTED profile.** A young student with runway is measured by
  distance travelled, not by what a backend match key imagines they will become.

**The boundary in one line:** R2 diagnoses, R4 decides. Every failure this step has had was
a version of crossing it.

---

## Inputs

- the current profile (R1), never `projected`
- the retrieved admitted profiles (Match & Rank)
- `reference_json.findings` — the admissions findings for this track, **with its own
  caveat** [#22]. Judge which differences actually separate admits from rejects by citing
  this, not by a private sense of what matters. Do not import findings from elsewhere.
- `expert_json` §14.3 — headed, almost verbatim for us, *"Profile diagnostic checklist (for
  a GapAnalyst agent)"*. **Advisory only** and tier-gated. [#73]

## Output

Named gaps, each with the evidence it rests on. An `academics_floor` gap **survives into
the moves whatever else is traded away** — a GPA is cumulative, so the years skipped cannot
be recovered, which is arithmetic rather than emphasis. [#64]

---

## The rule that cost us something

Six academics gaps once arrived, all six were dropped by the next step, and **nothing said
why.** A gap that disappears silently between steps is indistinguishable from a gap that was
never found. That is why the academics floor is now non-tradeable and why `gate_gap` exists.

---

## Gates

| Gate | What it refuses |
|---|---|
| `gate_gap` | a diagnosis that prioritises; a fix proposed; comparison against the projected profile; an academics floor dropped without a stated reason |
