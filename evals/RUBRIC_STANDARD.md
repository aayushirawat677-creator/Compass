# The Rubric Standard — how we grade a rubric

*The meta-rubric. Every rule below traces to a real failure made while writing the Compass
rubrics, not to theory. Apply it before any rubric is used to make a decision.*

---

## Why this exists

A bad rubric is worse than no rubric. It produces numbers that look like measurement, so people
stop looking. Three times in one day a Compass rubric certified something wrong: it graded the
writer while calling it R1, it passed a stale band scheme it had itself allowlisted, and it failed
a correct plan because a regex didn't know the word "internship". None of those were caught by
reading the scores. They were caught by reading the rubric.

**A rubric is a measuring instrument, and instruments need calibration.**

---

## The eight rules

### 1. Name the subject precisely — which artifact, from which step
*The single most damaging failure. A rubric labelled "R1" that reads the rendered PDF is grading
**R9's writing** and sending someone to fix the wrong prompt.*
- Every rubric states: **this grades `<object>` produced by `<step>`.**
- If the step has no parent-facing output, say so — and say who does.
- **Test:** could a reader tell, from the rubric alone, exactly which JSON key it reads?

### 2. Four to five checks, and say which ones carry the grade
*Seven checks weighted equally is a rubric claiming nothing matters most — so a step can fail the
thing that counts and still score well.*
- 4–5 checks. Mark the 2–3 that carry it (★).
- More than five means two are duplicates or one is a schema property (rules 4 and 5).
- **Test:** if the step failed only its ★ checks, would the grade actually be bad?

### 3. Have a gate where failure makes everything downstream meaningless
*Not every rubric needs one. Where one exists, scoring the rest is grading a fiction.*
- A gate fails → stop, report, don't compute the rest.
- Examples: intake missing the basics (R1) · retrieval returned nothing usable (Match Key) ·
  fit asserted rather than computed (R5) · something unverified presented as verified (R7).
- **Test:** is there a failure that makes the other checks not worth reading? Then it's a gate.

### 4. Include exactly one outcome check — did the step do its JOB?
*The most common blind spot. Every check can pass while the step fails at the only thing it was
for. A strategy that follows every rule and produces five mediocre threads. A document that is
faithful, kind and specific — and leaves the parent with nothing to do.*
- One check asks the outcome question, in the step's own terms, and is usually ★.
- **Test:** could something score full marks and still be useless? Then the outcome check is missing.

### 5. Prefer absence-of-defect and structural checks. Phrase-presence is a last resort
*"Does the document contain 'two to four activities'" is satisfied by pasting the sentence in.
Count the threads instead.*
- Best: **absence** of a defect (no judgment on the profile page) — a real property of the artifact.
- Good: **structural** (count the threads; check summers escalate; verify every credential has
  plan work behind it).
- Last resort: **phrase presence** — and never for something a writer can satisfy verbatim
  without changing behaviour.
- **Test:** could a lazy writer pass this check without improving the output? Then rewrite it.

### 6. Every sub-3 check names a fix lever
*A grade without a remedy is a complaint. The lever is the deliverable.*
- `FIX_PROMPT` · `ASK_PARENT` · `CHANGE_INTAKE` · `CHANGE_SCHEMA` · `BAD_INPUT`
- **`BAD_INPUT` matters more than it looks.** Module bugs surface as agent failures: an empty
  catalog reads as a lazy recommendation agent; a broken tally reads as a hallucinating analyst.
  **When an agent scores low, check its inputs before rewriting its prompt.**

### 7. Calibrate in BOTH directions
*A false pass certifies a defect. A false fail sends someone to rewrite something already correct —
and after a few of those, people stop trusting the rubric, which costs more than either.*
- Before trusting a check, run it against **known-good** output as well as known-bad.
- A check that fires on correct work is a defect in the rubric, not the work.
- **Real example:** "summers escalate" failed a plan that said *internship* because the pattern
  looked for *job / paid work*. The plan was right; the check was narrow.

### 8. Version the rubric with the rules it enforces
*A rubric grading against last week's rule doesn't just miss — it actively certifies the stale
thing as correct.*
- Rubrics carry a version and a note on what changed and why.
- When a rule changes, the rubric changes in the same commit.
- **Real example:** the band check passed stale corpus-era bands for hours because the old band
  edges were still allowlisted. Tightening it dropped the score from 74% to 70% — the rubric
  getting honest, not the plan getting worse.

---

## Two structural rules that sit above the eight

**Agents get rubrics. Modules get unit tests.** A rubric judges reasoning that could reasonably
go several ways. A module either computes the right answer or it doesn't, and a rubric there is a
slower, vaguer test. Retrieval, tallies, rate lookups, the guardrail, context packs → tests.

**Schema belongs to the validator, not the rubric.** "Are all fields present", "is the summer task
filed under Summer", "does the object have no numbers in it" — a validator checks these in
milliseconds, every run, without judgment. Putting them in a rubric inflates the check count and
crowds out the questions only a human or a model can answer.

---

## The shared shape

Every Compass rubric has the same sections, in this order:
1. **The big idea, in one minute** — what the step does, and the failure that matters
2. **What it reads in** / **What it outputs** — named precisely (rule 1)
3. **The checks** — 4–5, scored 0–3, ★ on those that carry it, gate marked if present
4. **The grade** — one Fitness (A–F), with an example read in one sentence
5. **What it is NOT graded on** — the boundary, naming the step that owns each excluded thing
6. **Open questions** — what is still undecided, addressed to the person who can decide it

Scoring is always: **3 Strong · 2 Okay · 1 Weak · 0 Missing/Broken**, rolling to
**A** ready · **B** small fixes · **C** real gaps · **D–F** rework.

**Why "what it is NOT graded on" is not optional:** it is what stops rubrics sprawling into each
other's territory, and it is where the architecture gets enforced. If two rubrics both claim a
question, the pipeline has an ownership bug — and the rubric is where you find out.

---

## Auditing
`python evals/audit_rubrics.py` checks every rubric against rules 1–8 mechanically.
It cannot judge whether a check is *good* — only whether the rubric is shaped to be honest.

---

## Postscript: this standard's own auditor false-failed on first run

Worth recording, because it is rule 7 happening live on the instrument built to enforce rule 7.

`audit_rubrics.py` was written from this document, then run against all nine rubrics. It failed
**R1 and the Gap Analyst** — the two we agree are the good ones — on three counts:

| flagged | why it was wrong |
|---|---|
| "no weighting (★)" | Both weight in prose: *"Checks 2, 3, 4 are the heart"*, *"the real thinking"*. A rubric is not worse for not using my notation. |
| "no fix levers" | Both carry a lever on every check — written as *"Fix if low: Fix the prompt"*, not the constant `FIX_PROMPT`. |
| "too many checks" (Gap, 6) | A diagnostic step whose job IS completeness legitimately needs more coverage checks than a step that makes one decision. |

Three false fails out of four flags. Had we acted on them, we would have rewritten two correct
rubrics into a house style that added nothing.

**Two lessons, and the second is the uncomfortable one.**

First: the auditor was matching **notation, not substance** — the exact failure rule 5 warns about,
committed by the tool meant to catch it.

Second: **I loosened the auditor three times to make those failures go away.** That is the right
move when a check is genuinely too literal, and it is indistinguishable from the wrong move —
tuning an instrument until it stops complaining. The discipline is that each loosening must be
justified by pointing at the *substance the rubric does have*, not by the fact that the score
improved. All three here were: the weighting, the levers and the coverage checks are demonstrably
present in R1 and Gap. But the risk is real and the honest record of it belongs in this file, so
the next person who "fixes" an auditor has to make the same argument out loud.

**Current state: 0 rule failures across 9 rubrics.** That number means the rubrics are shaped to
be honest. It does not mean they measure the right things — nothing mechanical can tell you that.
