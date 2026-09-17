# R9 Writer — Grading Rubric (v3)

*How we grade the document the parent actually reads. Written to discuss and refine, not final.*

*v3 change: rewritten to the R1 v2 format. v2 had merged "prose discipline" with "specificity" and added the outcome check; that holds.*

---

## The big idea, in one minute

**What R9 does.** R9 takes the finished, validated plan and turns it into the document. It answers one question: **"How do we say this to a parent?"** Nothing else.

**Two kinds of thinking — R9 does neither of the deciding ones:**
- Every factual decision is already made. R9 chooses **words**, not content.
- If something looks wrong while writing it, that is an upstream failure surfacing here. Flag it; don't fix it quietly, and don't write around it.

**R1's rubric hands this step a debt.** R1 is graded only on "don't overclaim" — the whole *"does this sound like my kid"* question was deliberately moved here, because the parent reads R9's words, not R1's object. **If a parent ever says "that's not my child", the two grades tell you where to look:** R1 accuracy low = the *facts* overreached; R1 fine but R9 flagged = the *wording* was wrong.

**What the document is made of** (the sections R9 populates): cover · profile · the two Outcome Cards · course targets · the roadmap · this year's recommendations · parent actions · the final note.

**Two failure modes, pulling opposite ways.** **Thin** — one-line summaries where the parent needed detail. And **invented richness** — filling space with claims nobody decided. The way to be long is to be *specific*, never to pad.

**Who reads it.** One parent, once, about their own child, probably at night, probably worried. That sentence generates most of the tone rules below.

**R9 gets ONE grade: a Fitness grade** — would this document actually work for the family it was written for?

**How to read a low score — every miss points to one fix:**
- **Fix the prompt** — R9 had the plan and wrote it badly.
- **Bad input** — the plan was thin, so the document is thin. Check upstream before rewriting R9.
- **Change the schema** — a section has no slot for something the parent needs.

Running example: **Maya, Grade 9** — robotics spine, perfectionist who hates failing publicly, tight budget, rural. Her mother's stated worry: *"she gives up on things she's not immediately good at."*

---

## What R9 outputs

R9 produces **one thing: the StrategicPlan document object**, which the renderer turns into the PDF. This is the only parent-facing artifact in the system.

**Profile section**
- `title` · `lead` · `blocks[]` (each: `subhead` · `thesis` · `body`) · `flags`
- *supports checks 3 and 4 · **this is R9's writing, not R1's object** — a distinction that matters: grading this and calling it R1 sends someone to fix the wrong prompt*

**Outcome cards (target / stretch)**
- `label` · `title` · `subtitle` · `stats[]` · `credentials[]` · `bands` · `takeaway`
- *supports checks 2, 4 and 5 · substance comes from R5; R9 words it*

**Roadmap · course targets · this year · parent actions**
- *supports checks 1 and 2 · substance from R6 and R7*

**Final note**
- two paragraphs answering the parent's stated worry
- *supports check 1 · **the worry is why they came**; a final note that summarises instead of answering has missed the point of the document*

**Numbers carried in** ★
- the set of figures R9 was handed, so any percentage in the output can be checked against it
- *★ makes check 5 mechanically gradeable — supports check 5 · used by the validator*

**Design note (decided):** R9 may not drop a plan item it finds hard to write honestly. It renders and flags, so the Critic and a human see it. Silently omitting an awkward item hides an upstream defect and makes the plan quietly incomplete. Flag for Nick if he'd rather R9 self-censor.

**Rule that still holds:** R9 states **no number it was not handed**, and never a number as the student's personal chance.

---

## Scoring scale (same for every check)

| Level | Score | Means |
|---|---|---|
| **Strong** | 3 | Does the job fully. |
| **Okay** | 2 | Mostly there, small gaps. |
| **Weak** | 1 | Real problems, needs work. |
| **Missing / Broken** | 0 | Not done, or wrong. |

---

## The five things we grade

### 1. The parent knows what to do — and their worry is answered  *(the outcome check)*

**Plain meaning:** After reading, is the next action unmistakable, and did the document respond to what this family actually asked?

**Why it matters:** The document exists to produce action and relief. A plan that is accurate, warm and inert has failed — and it fails invisibly, because every other check passes. The stated worry is the thing the parent typed when nobody was watching; not answering it is the clearest possible signal that this was written for a generic family.

**What we look for:**
- Parent actions ordered by deadline, none of them leaning on the child.
- The final note answers the worry **in the parent's own terms**, without repeating the sensitive part of it back at them.
- It is clear what needs no action yet.

**Strong:** The worry is *"she gives up on things she's not immediately good at"* → the note explains that the first competition is deliberately low-stakes with a second attempt available, and why that ordering was chosen. It answers.
**Weak:** A warm closing paragraph that summarises the plan and never touches the worry.
**Broken:** The plan is read, and the parent doesn't know what to do in October. Score 0.

**Fix if low:** **Fix the prompt.**

---

### 2. Faithful

**Plain meaning:** Does it say only what the plan decided?

**Why it matters:** An invented program or number here is indistinguishable from a real one to the reader — R9 is the last step, so nothing downstream will catch it. It also breaks the whole architecture: every upstream guardrail is pointless if the writer can add facts at the end.

**What we look for:**
- No program R7 didn't return. No number R9 wasn't handed. No new claim about the kid.
- Where the plan is thin, the document is honest about it rather than filling the space.

**Strong:** A section with two real items stays at two, and says the rest comes later.
**Weak:** A credential on the card that no plan task produces.
**Broken:** A named program with a price that appears nowhere upstream. Score 0.

**Fix if low:** **Fix the prompt**, or **Bad input** if the plan itself was empty.

---

### 3. Tone and dignity  *(the "sounds like my kid" check)*

**Plain meaning:** Would this parent recognise their child, and finish it without wincing?

**Why it matters:** This is the trust surface of the whole product. A parent who feels their child has been judged stops reading and doesn't come back — and they are right to. Every difficult thing in this document was told to us in confidence, by someone hoping we'd help.

**What we look for:**
- Neutral or lightly positive throughout. Calm, not hyped.
- **No prediction of a bad outcome** about the child, in any form.
- The warm plain word over the clinical one: "aims high", not "perfectionist".
- A difficulty the parent shared is reframed as *how she works best*, never stated as a flaw.
- **No sensitive cause named** — family structure, household stress, money anxiety — even where it genuinely shaped the plan.
- No faint praise, no absolutes.

**Strong:** "She does her best work when there's a route back from a mistake — a retake, a second attempt."
**Weak:** "A perfectionist who struggles with failure."
**Broken:** "A big competition as a first step would end with her quitting by winter." Score 0 — a prediction about the child, and the parent's own fear quoted back as our forecast.

**Fix if low:** **Fix the prompt.**

---

### 4. Every sentence earns its place

**Plain meaning:** Is anything here that could be deleted without losing information?

**Why it matters:** Padding is not neutral — it buries the parts that matter and signals that nobody read it back. Two specific habits do most of the damage: restating the thesis inside the body, and abstract praise that floats above the facts. Both make a document longer and less trustworthy at once.

**What we look for:**
- **No thesis echo** — the body adds information, it doesn't summarise itself.
- **No throat-clearing openers**; the heading already said it.
- **No internal process talk** — the parent doesn't need our pipeline explained.
- **No abstract praise.** Write the mechanism as a chain from stated facts.
- **Claims name their specifics or get cut.** Cards carry achievements with level and scale, never the itinerary that produces them.

**Strong:** "Builds bots alone at night, and has taken them to a regional competition."
**Weak:** "A curiosity fed by hands-on making." Too vague to picture.
**Broken:** "She reads a room and communicates with rare maturity." Asserted, unfounded, and says nothing. Score 0.

**Fix if low:** **Fix the prompt.**

---

### 5. Numbers presented honestly

**Plain meaning:** Is every number what it actually is?

**Why it matters:** Numbers are the part a parent trusts most and questions least. A percentage beside a university name will be read as "my child's chance" unless the sentence makes it impossible to read that way. Getting this wrong is not a rounding issue — it changes what the family believes about how admissions works, and they make real decisions on it.

**What we look for:**
- Rates appear as the **school's own published rate, with its class year**.
- **Never** phrased as the student's chance, odds or probability.
- Cohort statistics stay in the backend — they never appear on the Outcome Card, which is about this child.
- No number R9 wasn't handed.

**Strong:** "CMU admits about 11% of applicants (class of 2029)."
**Weak:** "Her chances at CMU are around 11%."
**Broken:** "Only 35% of this cohort ran a venture" printed on Maya's card. Score 0 — analytics on a page that is supposed to be about her.

**Fix if low:** **Fix the prompt.**

---

## The grade

| Letter | Meaning |
|---|---|
| **A** | Ready to send to a family. |
| **B** | Small fixes; usable. |
| **C** | Real gaps; fix before sending. |
| **D–F** | Not usable; rework. |

**Checks 1, 2 and 3 carry the grade** — useful, faithful, and kind. A document that is accurate but inert has failed; so has one that is warm but invents a fact.

**Example read for Maya:** *"Fitness B. Faithful, well-toned, numbers labelled correctly — but two profile blocks restate their own thesis (check 4) and the final note summarises rather than answers the stated worry (check 1). Fix: R9 prompt."*

---

## What R9 is NOT graded on (on purpose)

- **Whether the plan is any good** → **R4 / R6**. R9 renders what it's given; a thin document from a thin plan is an upstream grade.
- **Whether a recommendation is real** → **R7** and the research step.
- **Whether a number is correct** → modules. R9 is graded on presenting it honestly, not on computing it.
- **Section structure and field placement** → the **validator**.
- **The underlying facts about the kid** → **R1**. See the split at the top: overclaimed facts are R1's; sharp wording is R9's.

---

## Open questions for Nick

1. **May R9 drop an item it can't write honestly**, or must it render and flag? See the design note — we lean render-and-flag.
2. **A reading-level target** for the parent-facing text? Worth setting explicitly rather than leaving to taste.
3. **The final note** — should answering the stated worry be a hard requirement (fail if absent), given it's the reason the family came?
4. **Length** — is there a point where a document becomes too long to be read once, at night, by a worried parent?

---

*Covers R9 (the writer). Reads the validated plan; produces the only thing a family ever sees. Checked last by R8.*
