# R5 Two Paths (Target & Stretch) — Grading Rubric (v3)

*How we grade the target/stretch fork. Written to discuss and refine, not final.*

*v3 change: rewritten to the R1 v2 format. Still flags the bigger problem — **this step does not exist in the engine yet.** The pipeline runs `strategy → plan → recommendations → writer`, so nothing produces the fork and the **Writer is inventing both cards**. That is why the stretch card kept drifting into four different-sounding achievements instead of the same student pushed harder.*

---

## The big idea, in one minute

**What R5 does.** R5 takes the moves R4 chose and produces **two coherent versions of the same plan** — Target and Stretch. It answers one question: **"What does this student look like at the end, on each path?"** Nothing else.

**Two kinds of thinking — R5 does neither of the obvious ones:**
- R4 decided **what** to do. R6 decides **when**. R5 decides **how hard**, and what that costs.
- R5 is not a second strategy pass. It never revisits which gaps matter; it takes the same moves and asks what they look like at two intensities.

**What the fork is made of** (three parts):
- **Target variant** — the core moves at their stated intensity. The realistic path.
- **Stretch variant** — the *same threads*, earlier and harder, plus the stretch-tagged moves.
- **The delta** — what is harder, and what it costs in hours, money and risk.

**The line that must not blur — and it is the whole reason this rubric exists.** Tiering has two halves from two different sources:
- **How selective a school is** → its **published admit rate**. A module supplies it. It is **constant across both variants**. Harvard is 3.59% whether or not Maya improves.
- **How well this student fits that school's admit pattern** → **R5's job**, computed against corpus admits with n.

**The student's FIT moves. The school does not.** Any output implying a school became less selective because the kid got stronger is the defect the entire numbers architecture exists to prevent.

**R5 gets ONE grade: a Fitness grade** — are these two variants coherent and honest enough for R6 to schedule and R9 to render?

**How to read a low score — every miss points to one fix:**
- **Fix the prompt** — R5 had what it needed and reasoned badly.
- **Bad input** — retrieval was thin, so fit can't be computed.
- **Change the schema** — no slot for the delta or the fit evidence.

Running example: **Maya, Grade 9** — robotics spine at regional level, GPA 3.9, CMU CS target, tight budget, rural.

---

## What R5 outputs

R5 produces **one thing: a two-variant object.** The parent eventually sees it as the two Outcome Cards, but **R9 writes those** — R5 produces the substance, not the words.

**Target variant**
- `achievement_profile` (what she has at grade 12 on this path) · `course_targets` · `moves_included`
- *supports checks 2 and 4 · used by R6, R9*

**Stretch variant**
- same shape, plus `moves_added` (the stretch-tagged ones) and `intensified` (which threads move up a level)
- *supports check 2 · used by R6, R9*

**Fit assessment, per school** ★
- `school` · `pattern_coverage` (which of the admit pattern's credentials this profile covers) · `n` (how many admits it rests on) · `sufficient` (false → say the data is thin, don't guess)
- *★ the addition that makes check 1 gradeable. Without `n` a fit claim is an opinion wearing a number's clothes. · used by R9*

**The delta** ★
- `what_is_harder` · `extra_hours_per_week` · `extra_cost` · `added_risk`
- *★ so the stretch path is never a free upgrade — supports check 4 · used by R9, and by the parent making the actual choice*

**Design note (decided):** R5 states **no admit rates**. It receives them from the module and may cite them, but never computes, adjusts or re-bands one. The two axes stay in separate fields so they cannot be accidentally merged in rendering. Flag for Nick if he'd rather R5 own banding entirely.

**Rule that still holds:** the Stretch variant is the **same student**. If it introduces a thread the Target variant doesn't have and R4 never selected, it isn't a stretch plan — it's a different kid, and there is no plan behind it.

---

## Scoring scale (same for every check)

| Level | Score | Means |
|---|---|---|
| **Strong** | 3 | Does the job fully. |
| **Okay** | 2 | Mostly there, small gaps. |
| **Weak** | 1 | Real problems, needs work. |
| **Missing / Broken** | 0 | Not done, or wrong. |

Fit-is-computed is a **gate**: if fit is asserted rather than measured, we stop — everything on the cards is decoration.

---

## The four things we grade

### 1. Fit is computed, not asserted  *(the GATE)*

**Plain meaning:** Does the fit claim rest on actual admit data, with a count behind it?

**Why it matters:** Fit is the only number on the card that is genuinely about *this student*. If it's asserted, the card looks quantitative and is entirely opinion — the worst combination, because a parent reads a number and stops questioning it. And there is no way to tell a computed fit from an asserted one by reading the output, which is precisely why it's a gate.

**What we look for:**
- Every fit claim carries `n` — the number of admits it rests on.
- Below the threshold, it says the data is thin rather than producing a number anyway.
- Coverage is expressed against the actual admit pattern for that school and major, not a general impression of selectivity.

**Strong:** "Covers 4 of the 5 credentials present in most CMU-CS admits (n=38)."
**Weak:** "Strong fit for CMU" with no basis stated.
**Broken:** A fit claim for a school with 3 matched admits, presented with the same confidence as one with 40. Score 0.

**Fix if low:** **Fix the prompt**, or **Bad input** if retrieval genuinely returned too few admits.

---

### 2. Same kid, two intensities

**Plain meaning:** Is Stretch recognisably Maya pushed further — or a different applicant?

**Why it matters:** The parent is choosing between two paths for *their child*. If Stretch contains threads Target doesn't, they aren't choosing an intensity, they're being shown a stranger — and there's no plan underneath it, because R4 never selected those moves. This is also the failure that happens automatically when nobody owns this step: a writer asked to produce a "stronger" card invents four more impressive-sounding things.

**What we look for:**
- Every Stretch credential is a Target credential at a higher level, or a move R4 explicitly tagged stretch.
- The spine is the same in both.
- The number of threads doesn't balloon — Stretch is deeper, not wider.

**Strong:** Target = regional robotics + team member; Stretch = national qualification + team lead. One thread, two levels.
**Weak:** Stretch adds a research project R4 never selected.
**Broken:** Stretch has a different spine. Score 0 — it is not a version of this plan.

**Fix if low:** **Fix the prompt.**

---

### 3. Selectivity is never dressed up as fit

**Plain meaning:** Does the output keep "how hard is this school" and "how well does she match" as two separate things?

**Why it matters:** This is the single most consequential honesty failure in the product. A parent who believes their child's improvement changed a school's admit rate has been misled about how admissions works — and they'll make real decisions on it. It is also seductive: "Stretch moves Harvard from far reach to reach" is a satisfying sentence, and it is false.

**What we look for:**
- R5 states no admit rate of its own.
- Fit and selectivity sit in separate fields, so rendering cannot merge them by accident.
- Nothing implies a school moved because the student improved.

**Strong:** "CMU admits about 11% of applicants (class of 2029). On the Stretch path Maya covers 5 of 5 common admit credentials rather than 3."
**Weak:** "Stretch improves her odds at CMU" — vague enough to be read as the rate changing.
**Broken:** "The stretch plan moves CMU from Reach to Target." Score 0.

**Fix if low:** **Fix the prompt.**

---

### 4. The delta is priced, and both variants survive the guardrails

**Plain meaning:** Does it say what Stretch actually costs — and does Stretch still respect money and hard-nos?

**Why it matters:** A stretch path that appears free is a trap. The parent picks it, the term arrives, and the hours or the money aren't there — and the whole plan collapses at once. Money and hard-nos are limits in **both** variants: Stretch may raise effort, it may not quietly raise the budget.

**What we look for:**
- `what_is_harder` plus concrete extra hours, cost and risk.
- Stretch stays inside budget and hard-nos.
- Stretch doesn't contradict the temperament conditions R1 recorded — "earlier and harder" must not mean "one-shot and high-stakes" for a kid who needs a route back.

**Strong:** "A year earlier in math, one more AP, and a summer program chosen because it offers aid — about four more hours a week from grade 10."
**Weak:** Stretch described entirely in outcomes, with no cost stated.
**Broken:** A $6k institute against a $3–5k cap, justified as "the stretch version". Score 0.

**Fix if low:** **Fix the prompt**, or the **validator** if it shipped past the guardrail.

---

## The grade

| Letter | Meaning |
|---|---|
| **A** | Ready. Hand to R6/R9. |
| **B** | Small fixes; usable. |
| **C** | Real gaps; fix before relying on it. |
| **D–F** | Not usable; rework. |

Gated on check 1. **Checks 2 and 3 carry the grade.**

**Example read for Maya:** *"Fitness C. Variants share a spine and the delta is priced — but fit is asserted rather than computed against the admit pattern (check 1, the gate), so the bands are decoration. Fix: R5 prompt, and check retrieval depth."*

---

## What R5 is NOT graded on (on purpose)

- **Which moves were chosen** → **R4**. R5 takes them as given.
- **When any of it happens** → **R6**.
- **Which specific program** → **R7**.
- **The published admit rate itself** → the **rate table module**. R5 never computes one.
- **How the cards read to a parent** → **R9**. R5 supplies substance, not sentences.

---

## Open questions for Nick

1. **The band grid — the real product decision.** A school's band is fixed under the published-rate model. Do we show (a) school + fixed rate + a fit indicator that changes between plans, or (b) keep the v10 "moves up a band" arrows and redefine the band as FIT? (b) preserves the look but risks a parent reading it as the odds changing — the exact conflation check 3 forbids.
2. **May Stretch add a genuinely new thread**, or only intensify existing ones? We lean: only intensify, plus moves R4 already tagged stretch.
3. **Where does R5 sit** — after R4 and before R6, so R6 schedules whichever variant the family picks? That is our assumption.
4. **Does the family choose a variant**, or do we ship both and let them decide informally? This changes whether R6 schedules one plan or two.

---

*Covers R5 (the two paths). Reads R4's moves and the admit pattern; hands two variants to R6 and R9.*
