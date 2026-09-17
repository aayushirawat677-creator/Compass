# R8 Communication Critic — Grading Rubric (v3)

*How we grade the last check before the PDF. This rubric grades the grader. Written to discuss and refine, not final.*

*v3 change: rewritten to the R1 v2 format. v2 had merged actionability with attribution, and scope with verdict; that holds.*

---

## The big idea, in one minute

**What R8 does.** R8 reads every string in the finished document and flags what is wrong with **how it is written and presented**. It answers one question: **"Is this ready to send to a family?"** Nothing else.

**Two kinds of thinking — R8 does neither, deliberately.** It does not decide what the plan should say (R4), and it does not write it (R9). It **checks**, and it reports. Quote the line, name the rule, say why, give a fix hint — and stop. A Critic that rewrites has become a second writer nobody is grading.

**Why it needs its own rubric.** R8 is the enforcement layer for every rule in this system. **Miss things and defects ship. Flag good content and people waste time rewriting what was right — and then they learn to ignore it.** Both failures are costly, and only the first one is visible. The second kills the Critic slowly.

**What a finding is made of** (five parts): the quoted line · the rule it breaks · why it breaks it · a fix hint that doesn't do the rewriting · **the agent responsible**.

**How we actually measure it — and this is the hard part.** Recall and precision **cannot be judged by reading R8's output**. Reading its findings tells you whether they look sensible, not whether it missed anything. They need a **seeded-defect test set**: take a known-good plan, inject one defect at a time — a pejorative word, a fabricated rate, a founder credential, an itinerary on the card — and record what it catches and what else it flags. **That test set is the real deliverable behind this rubric**, and without it checks 1 and 2 are unscoreable.

**R8 gets ONE grade: a Fitness grade** — is it catching enough, quietly enough, to be trusted?

**How to read a low score — every miss points to one fix:**
- **Fix the prompt** — add the missed rule family, or scope an over-broad one.
- **Change the schema** — no slot for the responsible agent.
- **Bad input** — the test set is stale and no longer reflects the rules.

Running example: **Maya's plan**, with four defects seeded — "perfectionist who struggles" (tone), an 11% figure nobody supplied (fabricated number), "founds a robotics club" (join-don't-found), and a card credential written as a term-by-term itinerary.

---

## What R8 outputs

R8 produces **one thing: a verdict object.** It is internal — the parent never sees it — but it is the last gate before the PDF.

**Verdict**
- `pass` | `rewrite` | `escalate`
- *supports check 4 · used by the pipeline, which blocks on escalate*

**Findings**
- `section` · `quote` (the actual line) · `rule` (which one) · `why` · `fix_hint` · **`agent`** ★
- *★ `agent` is the addition that makes a finding actionable. "Tone is off in the profile" sends someone to R1 — and the profile text is R9's. A finding without an owner routes the fix to the wrong prompt, which is worse than no finding. · used by whoever does the fixing*

**Design note (decided):** R8 flags and stops. It never returns an edited document. A Critic that rewrites produces text nobody reviewed, and hides the defect rate — you can no longer tell whether R9 improved or R8 patched over it. Flag for Nick if he'd rather it propose rewrites for a human to accept.

**Rule that still holds:** R8 changes **no** strategy, **no** number, and **no** recommendation. It is graded on how things are said, and on whether a claim is *presented* as verified — never on whether it is true in the world.

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

### 1. Recall — does it catch what's actually there?

**Plain meaning:** Of the defects present, how many did it find?

**Why it matters:** Everything R8 misses ships to a family. And the misses are not random: fluent, confident text is the hardest to flag, which means **fabricated numbers are the easiest class to miss and the most expensive to ship.** A Critic with good tone recall and poor number recall feels like it's working right up until it isn't.

**What we look for:**
- Measured against the seeded set, **per rule family** — tone, fabricated numbers, join-don't-found, itinerary-on-card, horizon violations, unverified recommendations.
- ≥90% overall, and **100% on fabricated numbers and unverified recommendations** — the two a family acts on.

**Strong:** Catches all four of Maya's seeded defects, and names the rule for each.
**Weak:** Catches the tone defect and the itinerary; misses the fabricated 11%.
**Broken:** Passes a document containing an invented program. Score 0.

**Fix if low:** **Fix the prompt** — add the missed family to the checklist.

---

### 2. Precision — does it leave right things alone?

**Plain meaning:** How often does it flag content that was correct?

**Why it matters:** The under-watched half, and the one that kills the Critic. Every false positive costs a rewrite of something that was already fine — and after a few, people start skipping the findings, at which point recall stops mattering because nobody is reading. **We have already hit this twice**: a check that flagged "internship" as vague when internship was exactly the right word, and an auditor that failed two correct rubrics for using prose instead of constants.

**What we look for:**
- Measured on a **known-good** plan. ≤1 false positive.
- Rules are scoped, not keyword-matched.
- **The comparison-supplement carve-out:** honest rejection data about *other* applicants is calibration, not negativity about this child. A Critic that can't tell those apart will sand down the most valuable page in the pack.

**Strong:** Reads the known-good plan and returns nothing.
**Weak:** Flags "she struggled with the first competition and came back" as negative tone — it is a recovery story, and the point of the sentence.
**Broken:** Flags the rejection list in the Profile Comparisons supplement as negative. Score 0 — that is the evidence the document exists to show.

**Fix if low:** **Fix the prompt** — scope the rule.

---

### 3. Findings are actionable and attributed

**Plain meaning:** Can someone act on each finding without re-deriving it — and do they know whose prompt to open?

**Why it matters:** A finding that doesn't quote the line makes the reader hunt for it. A finding that doesn't name the rule makes them argue about whether it's a problem. And a finding that doesn't name the **agent** sends them to the wrong prompt — we did exactly this, grading R9's profile text and labelling it R1, which would have sent someone to rewrite a prompt that was working correctly.

**What we look for:**
- The offending line quoted verbatim.
- The rule named.
- A fix hint that points at the problem **without doing the rewriting**.
- The **responsible agent** identified — and correctly.

**Strong:** *"'A perfectionist who struggles with failure' — profile block 3 — tone rule: clinical word where a plain one exists. Agent: R9. Hint: state how she works best instead."*
**Weak:** "Tone feels off in the profile." Unactionable and unowned.
**Broken:** Attributes a writing defect to R1. Score 0 — it routes the fix to a prompt that isn't broken.

**Fix if low:** **Fix the prompt**, or **Change the schema** to add the `agent` field.

---

### 4. Responds at the right level

**Plain meaning:** Does the verdict match the severity — and does R8 stay inside its remit?

**Why it matters:** The verdict is the only part the pipeline acts on. Under-reacting ships a defect; over-reacting blocks a document over a comma and trains everyone to override the block. And a Critic that drifts into changing content has stopped being a check: there is now unreviewed text in the document and no record of who wrote it.

**What we look for:**
- **escalate** for anything a family would act on — a fabricated program, an invented number, an unverified recommendation.
- **rewrite** for tone and prose problems.
- **pass** only when nothing material remains.
- No edited document returned; no number changed; no strategy altered; no "drop this recommendation" — that is R4 and R7's call.

**Strong:** Fabricated phone number → escalate. Two thesis echoes → rewrite.
**Weak:** Marks a fabricated rate as "rewrite" — it will get patched rather than investigated.
**Broken:** Returns a corrected plan instead of findings. Score 0.

**Fix if low:** **Fix the prompt.**

---

## The grade

| Letter | Meaning |
|---|---|
| **A** | Trustworthy. Act on its verdicts. |
| **B** | Small fixes; usable. |
| **C** | Real gaps; verify its output by hand. |
| **D–F** | Not usable; its findings can't be relied on. |

**Checks 1 and 2 carry the grade, and they trade against each other** — a Critic that catches everything by flagging everything is useless, and so is a quiet one that misses fabrications. Grade them together or you will optimise one into the ground.

**Example read for Maya:** *"Fitness C. Recall 92% and verdicts correct — but 6 false positives on the known-good plan (check 2), mostly over-broad negativity matching, and findings don't name the responsible agent (check 3). Fix: R8 prompt + schema."*

---

## What R8 is NOT graded on (on purpose)

- **Whether the strategy is good** → **R4**. R8 checks how it's said, not whether it's right.
- **Whether a number is correct** → modules. R8 checks whether it was *presented* as verified.
- **Whether a program is real** → **R7** and the research step. R8 catches a claim of verification, not the underlying fact.
- **Whether the plan is complete** → the **validator** and the runtime gates.
- **Writing the fix** → **R9**. R8 hints; it does not draft.

---

## Open questions for Nick

1. **Who builds and owns the seeded-defect test set**, and how often is it refreshed as rules change? Without it, checks 1 and 2 cannot be scored at all — this is the biggest open item in the eval system.
2. **Does `escalate` block the PDF outright**, or ship with the finding attached for a human? We lean block for fabrications, attach for everything else.
3. **Per-family recall targets** — 100% on fabricated numbers and unverified recommendations, 85% on tone? Worth setting explicitly so we know what "good" means.
4. **Should R8 ever propose a rewrite** for a human to accept, rather than only hinting? See the design note.

---

*Covers R8 (the critic). Reads R9's document; last gate before a family sees anything. Graded against a seeded-defect set, not by reading its findings.*
