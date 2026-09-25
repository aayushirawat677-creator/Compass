# `appraiser` — R3 Activity Appraiser (prompt spec)

**Component:** R3b · Activity Appraiser
**Phase:** 4b — after Gap, **before Strategy**
**Model tier:** **Top.** This is the only step allowed to say an activity will not repay five
years, and a family may act on it. ~1 call per activity, ~6k in / ~1.5k out.
**Version:** v1 — introduced at rule #59, two-layer cache, tier-gated advice from #73.
**Rubric:** `evals/R3_appraiser_rubric.md` (v2)

---

## Why it exists, and why it runs where it does

Before this step the engine took the family's activities as given and planned around all of
them. That produced plans which spent five years escalating something with no ceiling worth
reaching, and which quietly ignored the question every parent is actually asking: *is this
thing he loves going anywhere?*

**It sits before Strategy, not after.** Aayushi's argument, and it is right: a strategy
built on unappraised activities is a strategy that has already decided. R4 cannot choose
what to invest in without knowing what each thread can reach. Placing the appraiser after
strategy would make it a reviewer of decisions already taken.

---

## What it does / does not do

**Does:** for each activity, establish how far it can credibly go (`ceiling`), decide what
the plan should do with it (`disposition`), and where it converts, name the route
(`becomes`) and what carries over (`transfers`).

**Does not:**
- **Schedule anything.** R6 owns grades and terms. An appraisal that says "in tenth grade
  he should…" has crossed into planning.
- **Predict an outcome.** "This will impress admissions officers" is unknowable and is an
  automatic F on the rubric.
- **Put a number on traction.** Tested against our own corpus — 2,617 posts, 756 mentioning
  a venture — and once post length is controlled, the relationship between reported traction
  and a top-25 admit **disappears** (70.7% vs 72.2%, p=0.82). Any revenue or user threshold
  is fabricated.
- **Decide alone what the family could decide.** See `needs_family_input`.

---

## The two layers, and why the split is load-bearing

```
type_knowledge   about the ACTIVITY TYPE     cacheable, reused across families
appraisal        about THIS CHILD            never cached, never reused
```

`type_knowledge` is written once per activity type and applied to every future family that
matches it. **A child-specific fact that leaks into it propagates to strangers** — which is
why `appraise.py` carries a leak guard that matches child-specific FACTS rather than
pronouns, and why the rubric caps any appraisal containing one at C.

---

## Inputs (user message)

- the activity as the intake describes it — tenure, hours, where, level, the parent's note
- `admit_pattern_json` — what admits to **this student's six schools** held in that domain
- `activity_ceilings.json` — the cached type layer, via `appraise.lookup()`
- `expert_json` — §3.2, §3.3, §15, **advisory only and tier-gated** (#73). The corpus is
  calibrated to Ivy+ (≤10% admit); `expert.tier()` computes the band from the real list, and
  intensity advice applies at full strength only inside it.

## Output

```
{ type_knowledge, appraisal, ceiling, disposition, becomes, transfers,
  confidence, needs_family_input, family_question, operator_questions }
```

`disposition` ∈ `protect` · `keep_as_interest` · `convert` · `retire`

---

## The rules that cost us something

**The ceiling is structural.** Name the property that caps it — no outside body vouches, no
artefact anyone else uses, nobody judging who is not a relative — never a bare level. A
reader who disagrees must know which claim to attack.

**A conversion uses the history.** The route must be credible *because of* the prior years.
A route a student with no history could take equally well is a **replacement**, and calling
it a conversion hides that something was taken away.

**`retire` never wins against love.** If it is the thing the child would keep if they could
keep only one, that outranks the ceiling judgment.

**The hard call reaches the family.** A `convert` or `retire` on a long-running or high-hours
thread sets `needs_family_input` and carries a `family_question` a parent can answer without
knowing any of our vocabulary. `operator_questions` are ours and never reach the PDF. [#69]

**Our vocabulary stays backstage.** `reach`, `disposition`, `converts`, `as it stands` are
how the SYSTEM labels a verdict. They are not how a mother thinks about her son's chess, and
they must not appear in the document. The appraisal reaches the reader **as the plan** — the
business goes to a fair and later into a club; chess is simply never asked to do anything.
That *is* the verdict, expressed as what happens rather than as our reasoning about it.
Printing both is showing our working. [#75]

---

## Gates

| Gate | What it refuses |
|---|---|
| `gate_appraisal` | a verdict with no structural ceiling; a predicted outcome; a traction threshold; child facts in `type_knowledge` |
| `gate_honours_appraisal` | a plan that asks something of a thread the appraiser said to protect |
| `gate_open_questions` | a conversion acted on while its family question is unanswered — note it suspends the CONVERSION, not the ACTIVITY [#11] |
| `gate_expert_use` | advice cited without a rule id, advice overriding a measurement, intensity advice applied outside the tier |

---

## Open question

Confidence is self-reported. Should a `low`-confidence verdict be barred from producing a
`retire` at all, rather than merely flagged? That is a product decision about how much the
engine may do on thin evidence — it belongs to Aayushi, not to the prompt.
