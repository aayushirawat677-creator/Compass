# R3 — Appraiser rubric

Grades ONE activity appraisal. Run it blind: the grader sees the activity, the admit
pattern, and the appraisal — not who produced it, not the other activities.

This step is the only one allowed to say an activity is not worth five years. It is
therefore the step whose mistakes are most expensive, because a family may act on it and
a child may drop something they loved. Grade it harder than its size suggests.

---

## What it is for

Every other step takes the family's activities as given. This one asks how far each can
credibly go and what to do about the answer. A good appraisal saves a student years; a bad
one takes something from them on reasoning nobody checked.

---

## A — the bar

1. **The ceiling is structural, not dismissive.** It names the property of the activity
   that caps it — no outside body vouches, no artefact anyone else uses, no judge — rather
   than asserting a level. A reader who disagrees knows exactly which claim to attack.
2. **It is measured against THIS student's schools.** `admit_pattern_json` is used: the
   ceiling is set beside what admits to the six named schools actually held in that domain,
   not against a generic tier opinion.
3. **What transfers is specific and true.** "Inventory, margin and cash-flow literacy most
   students his age do not have" is a transfer. "Business skills" is not.
4. **A conversion uses the history.** The route is credible *because* of the prior years,
   and says how. A route a student with no history could take equally well is a replacement
   and must be graded as one.
5. **Layer separation holds.** `type_knowledge` would be true for any student with this
   activity. `appraisal` is about this one. Nothing child-specific in the cached layer.
6. **The hard call reaches the family.** A convert or retire on a long-running or
   high-hours thread carries `needs_family_input` and a question a parent can answer
   without knowing any of our vocabulary.
7. **Confidence is honest.** `low` when the cache was empty and search returned little.
   A confident verdict on thin evidence is worse than an unconfident one.

## B

Sound judgment, but one of: the ceiling is asserted rather than explained; the admit
pattern is present and unused; the transfer is real but generic; confidence is overstated.

## C

The verdict may be right but the reasoning would not survive a parent asking "why?".
Or: a conversion that does not use the history. Or: the appraisal reads as a ranking of
the child's interests rather than an assessment of what each can reach.

## F — any one of these

- **A predicted outcome.** "This will impress admissions officers." Nobody can know it.
- **An invented threshold.** "A business needs $10k revenue to count." We tested this
  against our own corpus — 2,617 posts, 756 mentioning a venture — and once post length is
  controlled the relationship between reported traction and a top-25 admit disappears
  (70.7% vs 72.2%, p=0.82). Any number put on traction is fabricated. [#59]
- **A tier framework stated as how admissions works.** Consultancies publish them; no
  college does. It is a vocabulary, and must be named as one.
- **`retire` on something the student loves**, to buy hours for something they do not.
  If it is the thing they would keep if they could keep only one, that outranks the
  ceiling judgment.
- **A hard verdict the family never sees.** Deciding alone what we could have asked.
- **Child-specific facts in `type_knowledge`**, which get cached and then applied to
  every future family that matches the type.

---

## The question that separates A from B

Would a parent who disagreed with this verdict know exactly which sentence to argue with?

If yes, the reasoning is visible and correctable — which is the whole point, because we
have never met this child and the family has.
