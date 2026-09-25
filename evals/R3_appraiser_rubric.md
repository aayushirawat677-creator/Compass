# R3 — Appraiser rubric (v2)

**This grades the `appraisals` array produced by the `appraiser` step (pipeline 4b).**
One object per activity: `{type_knowledge, appraisal, ceiling, disposition, becomes,
transfers, confidence, needs_family_input, family_question, operator_questions}`.

It does **not** grade how any of it reaches the family — that is R9's `threads` and the
roadmap, graded by the writer rubric. Run it blind: the grader sees the activity, the
admit pattern and the appraisal, not who produced it and not the sibling activities.

*v2 changes: rewritten to the RUBRIC_STANDARD shape (4 checks, ★ weighting, a gate, one
outcome check, fix levers). Adds the cache-leak gate, which did not exist when v1 was
written, and the ceiling-vs-appraisal layer split from #59.*

---

## The big idea, in one minute

Every other step takes the family's activities as given. **This is the only step allowed
to say an activity will not repay five years**, and therefore the only one whose mistake
takes something from a child rather than merely wasting their time.

The failure that matters: a verdict a parent cannot argue with. We have never met this
child and the family has. An appraisal whose reasoning is invisible is not a judgment they
can correct — it is one they must either accept or ignore.

**What it reads in:** the activity as the intake describes it, `admit_pattern_json` for
the student's real six schools, the two-layer cache, and any live lookup.
**What it outputs:** the `appraisals` array. Nothing parent-facing.

---

## The checks

Scored 0–3. ★ marks the two that carry the grade.

### 1 ★ The ceiling is structural, and named (the GATE)
It names the **property of the activity** that caps it — no outside body vouches for the
result, no artefact anyone else uses, nobody judging who is not a relative — rather than
asserting a level. A reader who disagrees knows exactly which claim to attack.

**This is the gate.** If the ceiling is asserted rather than explained, every other check
is grading a conclusion with no reasoning under it. Stop and report.

*3* — the capping property is named and is genuinely a property of the activity.
*2* — named but generic ("it is informal").
*0–1* — a level asserted ("local"), or a tier framework stated as how admissions works.

`FIX_PROMPT`

### 2 ★ The verdict is measured against THIS student's schools — and it is the outcome check
Did the step do its job? Its job is not to rank a child's interests; it is to say **how far
each thread can credibly go for these six schools, and what to do about the answer.**
`admit_pattern_json` must be used, not merely present: the ceiling sits beside what admits
to the named schools actually held in that domain.

*3* — the disposition follows from the ceiling set against the real admit pattern, and a
different school list would plausibly have produced a different verdict.
*2* — the pattern is present and unused; the verdict would be the same for any list.
*0–1* — a generic tier opinion, or a ranking of what the child enjoys.

`FIX_PROMPT` · `BAD_INPUT` if `admit_pattern_json` arrived empty — **check the input before
rewriting the prompt.** An empty retrieval reads exactly like a lazy appraiser.

### 3 A conversion uses the history; a hard call reaches the family
Two defects that travel together. A conversion route must be credible *because of* the
prior years and say how — a route a student with no history could take equally well is a
**replacement**, and grading it as a conversion hides that something was taken away.
And a `convert` or `retire` on a long-running or high-hours thread carries
`needs_family_input` with a question a parent can answer without knowing our vocabulary.

*3* — both hold.
*2* — the route uses the history but the family is not asked, or the reverse.
*0–1* — a replacement dressed as a conversion, and no question raised.

`FIX_PROMPT` · `ASK_PARENT`

### 4 Layer separation holds — nothing about this child in the cached layer
`type_knowledge` is cached against the activity TYPE and will be applied to every future
family that matches it. `appraisal` is about this one. A child-specific fact in the cached
layer is not a scoring error; **it is a defect that propagates to strangers.**

*3* — `type_knowledge` would be true for any student with this activity.
*2* — borderline phrasing, no actual child facts.
*0* — names, figures, hours or circumstances belonging to this student. Any occurrence
caps the whole appraisal at C regardless of the other checks.

`CHANGE_SCHEMA` · `FIX_PROMPT`

---

## The grade

One Fitness letter for the appraisal.

**A** — both ★ checks at 3, none below 2. *Example read:* "The ceiling is the absence of
any outside judge, measured against what admits to these six held in venture; the
conversion keeps the trading and adds the judging; the family is asked whether that feels
like building on it or taking it over."

**B** — sound judgment, one of: the ceiling explained but thinly; the admit pattern present
and unused; the transfer real but generic; confidence overstated.

**C** — the verdict may be right but would not survive a parent asking "why?". Or a
conversion that does not use the history. Or any child-specific fact in `type_knowledge`.

**F** — any one of:
- **A predicted outcome.** "This will impress admissions officers." Nobody can know it.
- **An invented threshold.** "A business needs $10k revenue to count." Tested against our
  own corpus — 2,617 posts, 756 mentioning a venture — and once post length is controlled
  the relationship between reported traction and a top-25 admit disappears (70.7% vs
  72.2%, p=0.82). **Any number put on traction is fabricated.** [#59]
- **A tier framework stated as how admissions works.** Consultancies publish them; no
  college does. It is a vocabulary and must be named as one.
- **`retire` on something the student loves**, to buy hours for something they do not. If
  it is the thing they would keep if they could keep only one, that outranks the ceiling.
- **A hard verdict the family never sees.** Deciding alone what we could have asked.

---

## What it is NOT graded on

| Excluded | Owned by |
|---|---|
| Whether the plan honours the appraisal | `gate_honours_appraisal`, and R6's rubric |
| How the verdict is worded for a parent | R9 — and note the appraiser's vocabulary (`reach`, `disposition`, `converts`) must never reach the PDF [#75] |
| Whether the activity is scheduled well | R6 |
| Whether the cache was hit or missed | `appraise.coverage()`, a module — unit tests, not a rubric |
| Schema completeness | the validator |

---

## Open questions

**For Aayushi:** confidence is currently self-reported by the step. Should a `low`
confidence verdict be blocked from producing a `retire` at all, rather than merely flagged?
That is a product decision about how much the engine may do on thin evidence.

**For whoever runs it first:** this rubric has never been applied to real appraiser output.
Calibrate it in both directions before trusting a score (standard, rule 7) — run it against
an appraisal you believe is good as well as one you believe is bad.

---

## The question that separates A from B

**Would a parent who disagreed with this verdict know exactly which sentence to argue with?**

If yes, the reasoning is visible and therefore correctable — which is the whole point.
