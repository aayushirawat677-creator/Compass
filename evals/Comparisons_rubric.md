# Profile Comparisons — Grading Rubric (v1)

*How we grade the two-page supplement that shows real applicant outcomes. Written to discuss and refine, not final.*

---

## The big idea, in one minute

**What the Comparisons step does.** It takes 3–5 anonymised profiles of real recent applicants to the schools on this student's list and turns them into cards: what they had, where they got in, where they didn't. It answers one question: **"What does each level of credentials actually buy?"** Nothing else.

**Why it exists, and this is the important part.** The Strategic Plan **cannot honestly state this student's odds.** The corpus is self-selected, and a published admit rate belongs to the school, not the child. **This supplement is the honest substitute for a probability** — instead of asserting a number, it shows four real applicants and what their credentials bought. Calibration by receipts.

**Two kinds of card — never blend them:**
- The **Outcome Cards** (plan, pages 3 and 5) are about **this student, projected**.
- These cards are about **other, real applicants, whose outcomes already happened.**

A comparison card must never read as a prediction for this child.

**What the supplement is made of** (three parts):
- **The tier strip** — three cells explaining what gold, purple and green mean. This is the entire "how to read it" section; there is no separate page for it.
- **The cards** — four, each a real applicant, sorted by outcome ceiling.
- **The takeaways** — one dark box per card, one sentence, pointing back at the plan.

**The tier system is the spine, and it is relative.** A card is tiered by **which of THIS student's bands the applicant's strongest admit falls into** — not by the school's absolute prestige. Gold = admitted in the student's Far Reach band. Purple = Reach, rejected from Far Reach. Green = Target. The tier words are the **same words the plan uses**, deliberately: a parent reading both should see one vocabulary.

**The sort order does the narrative work.** Best case → strong case → "even this wasn't enough" → "this is what you're actually building toward." That is why there is no synthesis section, and why writing one is a defect rather than an addition.

**It gets ONE grade: a Fitness grade** — could a parent read it cold in ninety seconds and walk away calibrated?

**How to read a low score — every miss points to one fix:**
- **Fix the prompt** — the data was there and the cards were built badly.
- **Bad input** — too few real profiles, or none matching the student's bands.
- **Change the schema** — no slot for the committed school, or for the tier mapping.

Running example: **Maya, Grade 9** — robotics spine, CS track, CMU in her Reach band, Georgia Tech in her Target band.

---

## What the Comparisons step outputs

It produces **one thing: a supplement object**, rendered as a two-page PDF beside the plan.

**Intro block**
- `eyebrow` · `title` · `deck` (ONE sentence)
- *supports check 5 · a deck of two sentences is the first sign the document is growing into a second plan*

**Tier strip**
- three cells: `tier` · `colour` · `one_line_meaning`
- *supports checks 2 and 5 · this replaces a "how to read these cards" page entirely*

**Cards** — four, sorted by outcome ceiling descending
- `tier` · `tag` · `name` · `stats[4]` · `credentials[4-6]` · `admitted[]` · `rejected[]` · `committed` · `takeaway`
- *supports every check · `rejected[]` is not optional and not secondary — see check 3*

**Tier mapping record** ★
- for each card: which of the student's bands the strongest admit fell into, and why
- *★ the addition that makes check 2 gradeable. Without it you cannot tell a correct tiering from a lucky one. · used by the reviewer*

**Design note (decided):** the tier is computed from **this student's band placements**, which means the same real applicant could be gold in one student's supplement and green in another's. That is correct and intended — the document is calibration *for this family*, not a ranking of applicants. Flag for Nick if he'd rather tiers be absolute and comparable across families.

**Rule that still holds:** these cards describe **other people**. Nothing here is a projection, a promise, or a statement about this student.

---

## Scoring scale (same for every check)

| Level | Score | Means |
|---|---|---|
| **Strong** | 3 | Does the job fully. |
| **Okay** | 2 | Mostly there, small gaps. |
| **Weak** | 1 | Real problems, needs work. |
| **Missing / Broken** | 0 | Not done, or wrong. |

Tiering is a **gate**: if cards are tiered by absolute prestige rather than this student's bands, the spine of the document is wrong and the rest is not worth grading.

---

## The five things we grade

### 1. Calibration lands  *(the outcome check)*

**Plain meaning:** Could a parent read this cold, in about ninety seconds, and come away knowing what each level of credentials actually buys?

**Why it matters:** This is the entire purpose. A supplement that is accurate, well-designed and leaves the parent no better calibrated has failed — and it fails invisibly, because every other check can pass. The test is not whether the cards are correct; it is whether the *arc* is legible without reading a word of analysis.

**What we look for:**
- The cards are sorted by outcome ceiling, so the arc reads top to bottom without prose.
- The gap between tiers is visible in the credentials, not just the colour.
- A reader could say, after skimming, what the Target tier cost and what it bought.
- No synthesis is needed to get there — if one would help, the sort order is wrong.

**Strong:** Gold card shows two publications and two paid summers; green card shows five publications and NASA, and still lands at Georgia Tech. The parent sees the ceiling without being told.
**Weak:** Four cards of roughly equal strength. Nothing is calibrated because nothing contrasts.
**Broken:** A parent finishes it unsure why one applicant got in and another didn't. Score 0.

**Fix if low:** **Fix the prompt**, or **Bad input** if the profiles genuinely don't span the bands.

---

### 2. Tiering is relative to this student's bands  *(the GATE)*

**Plain meaning:** Is each card tiered by where the applicant's strongest admit sits **on this student's list** — not by general prestige?

**Why it matters:** The tier is the only thing connecting this document to the plan. Get it wrong and the vocabularies diverge: the parent reads "Reach" in one document and "Reach" in the other, meaning different things, and quietly loses the ability to compare them. It also inverts the message — a card that looks like a triumph in absolute terms may be a Target outcome for this family, which is precisely the calibration the document exists to deliver.

**What we look for:**
- The mapping is recorded per card, with the band it fell into.
- The tier words match the plan's band names exactly.
- Where a profile's strongest admit isn't on this student's list at all, it is mapped by the nearest band, and that judgment is stated.

**Strong:** An applicant admitted to CMU is purple, because CMU sits in Maya's Reach band.
**Weak:** The mapping is right but unrecorded, so nobody can check it.
**Broken:** Cards tiered by prestige — an Ivy admit marked gold when no Ivy is on Maya's list. Score 0, and the run stops.

**Fix if low:** **Fix the prompt**, or **Bad input** if the plan's band placements weren't supplied.

---

### 3. The rejections are as visible as the admits

**Plain meaning:** Does each card show where the applicant did **not** get in, with the same weight as where they did?

**Why it matters:** The rejections are the calibration. An admits-only card is a highlight reel, and it teaches the parent the opposite of what we intend — that these credentials guarantee the outcome. The most useful card in a pack is usually the one showing a superb profile that was rejected from five top schools.

**And a specific hazard:** our own tone rules would strip this if left unscoped. **Honest rejection data about other applicants is calibration, not negativity about this child.** The Critic carries an explicit carve-out for exactly this; if a reviewer or a future rule sands these lists down, the document loses its reason to exist.

**What we look for:**
- Admitted and rejected columns of equal prominence, never a footnote.
- The committed school marked.
- Notable waitlists shown, annotated as such.
- Takeaways that say the sobering thing plainly where the outcomes show it.

**Strong:** "A $4.5M startup, an IEEE publication and a patent — rejected from Stanford, Columbia, Penn, Cornell and Duke."
**Weak:** Rejections listed but visually subordinate.
**Broken:** Rejections omitted, or softened into "considered elsewhere". Score 0.

**Fix if low:** **Fix the prompt.**

---

### 4. Source discipline

**Plain meaning:** Was the source data rewritten, and were its conclusions ignored?

**Why it matters:** Two distinct failures. **Verbatim reproduction** carries distinctive phrasing from an anonymised source into a document with our name on it. And **trusting the supplied synthesis** imports someone else's optimism as if it were evidence — third-party summaries routinely draw conclusions the raw outcomes don't support, and they are written to be persuasive.

**What we look for:**
- Every line paraphrased. Bombastic framing dropped; the outcome stated plainly.
- Any "Strategic Synthesis" or "Key Takeaways" block in the input **ignored**, with conclusions formed from the raw admit/reject lists instead.
- Concrete numbers kept — dollar amounts, citation counts, placements, acceptance rates. They are the most admissions-readable content on the card.
- Incidental clubs and hobbies discarded rather than padded in.

**Strong:** "Two research papers — a first-author NLP workshop paper with citations, and a solo-author journal piece."
**Weak:** Source phrasing lightly edited but recognisable.
**Broken:** The supplied synthesis reproduced as the takeaways. Score 0 — we have published someone else's conclusions as our analysis.

**Fix if low:** **Fix the prompt.**

---

### 5. It stayed a supplement

**Plain meaning:** Is this still two pages of cards — or has it started rebuilding the plan?

**Why it matters:** This is the failure mode the format invites. Every addition feels justified: a little context here, a synthesis there, a "where the student sits today" box. Four pages later it competes with the plan instead of supporting it, and the parent now has two documents making overlapping claims — which is worse than having one.

**What we look for:**
- Two pages. Roughly 80% cards by ink on the page.
- **No** cover page, **no** "how to read these cards" page, **no** synthesis page, **no** "where the student sits" box.
- One-sentence deck. One-sentence takeaways — two at the absolute maximum.
- Card grammar followed: four stats, 4–6 credentials, minor items consolidated.

**Strong:** Two pages, intro block under an inch, four cards, nothing else.
**Weak:** Three pages because the takeaways ran to three sentences each.
**Broken:** A synthesis page summarising what the cards mean. Score 0 — the cards already did that, and now they compete.

**Fix if low:** **Fix the prompt.**

---

## The grade

| Letter | Meaning |
|---|---|
| **A** | Ready to send beside the plan. |
| **B** | Small fixes; usable. |
| **C** | Real gaps; fix before sending. |
| **D–F** | Not usable; rework. |

Gated on check 2. **Checks 1, 3 and 4 carry the grade** — calibrated, honest about rejections, and not repeating someone else's conclusions.

**Example read for Maya:** *"Fitness B. Tiering correct against her bands, rejections prominent, sources rewritten — but the four profiles are too similar in strength (check 1), so the arc doesn't calibrate anything. Fix: prompt, or pull a wider spread of profiles."*

---

## What the Comparisons step is NOT graded on (on purpose)

- **Whether this student's plan is any good** → **R4 / R6**. This document comments on other applicants, never on the plan's quality.
- **This student's projected profile** → **R5** and the Outcome Cards. Never blend the two.
- **Any odds for this student** → nothing states them, here or anywhere. This supplement exists precisely because they can't be stated.
- **Whether the source profiles are representative** → a data question. It surfaces here as **Bad input**, and the fix is the profile set.
- **Page layout and pagination** → the **validator** and the render step.

---

## Open questions for Nick

1. **Relative vs absolute tiers.** See the design note: the same applicant can be gold for one family and green for another. Correct, we think — but confirm, because it makes cards non-reusable across students.
2. **How many profiles, and who picks them?** Four is the format. Whether they're selected for spread (to calibrate) or for similarity (to compare like with like) changes the document's job.
3. **What happens when the profile set doesn't span the bands** — ship a thinner supplement, or don't ship one at all? A supplement with three green cards calibrates nothing.
4. **Refresh cadence.** Outcomes age: a Class of 2024 profile calibrates differently than a Class of 2029 one. How often is the set replaced?

---

*Covers the Profile Comparisons supplement. Reads the plan's band placements and a set of real applicant profiles; ships beside the plan as the evidence behind it.*
