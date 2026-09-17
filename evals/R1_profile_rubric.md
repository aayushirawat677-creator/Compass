# R1 Profile — Grading Rubric (v2)

*How we grade the student profile the system builds. Written to discuss and refine, not final.*

*v2 change: tightened to four checks. The "how it's worded / opinion level" dial moved out of R1 and into R9 (the writing agent), because the parent reads R9's words, not R1's object. See "What R1 is NOT graded on."*

---

## The big idea, in one minute

**What R1 does.** R1 reads everything the parent typed in the intake and turns it into a clean picture of the kid: what they've done, who they are, what helps them, and what's missing. It answers one question — **"Who is this student?"** Nothing else.

**Two kinds of thinking — R1 does one of them:**
- R1 does the **reading**: *"what is this kid?"* — finding the spine, reading the temperament. This is R1's whole job.
- R4 does the **deciding**: *"is it good enough? what should they do?"* — that's a different agent.

R1 **describes**; R4 **decides and recommends.** Hold that line and the rubric stays clean.

**What the profile is made of** (five parts):
- **Spine** — the one thing the kid does on their own, without being told. The center of everything.
- **Texture** — the other real activities (sports, dance, clubs). Kept, but supporting.
- **Temperament** — the kid's personality: how hard we can push, what they fear, how they work.
- **Tailwinds** — advantages that help (family/legacy connections, a 504 that gives extra time).
- **Flags** — missing info, or things to confirm (a claimed award, a health note like ADHD).

**R1 gets ONE grade: a Fitness grade** — is this good enough for the rest of the system (R4/R6) to build a plan on? That's it. (The grade for whether the parent *feels* the profile is warm and "sounds like my kid" belongs to R9, the writing agent — see the end.)

**How to read a low score — every miss points to one fix:**
- **Fix the prompt** — R1 had the info and didn't use it.
- **Ask the parent** — the info wasn't in the intake; ask for it (show in the app).
- **Change the intake** — we never asked for it; add the question.
- **Change the schema** — the profile has no slot to hold it.

Running example: **Maya, Grade 10** — loves robotics (builds bots at home), also does dance, is a perfectionist who hates failing in front of people, family budget is tight and they live in a rural area.

---

## What R1 outputs

R1 produces **one thing: a profile object.** It has **no parent-facing output** — the profile the parent reads in the PDF is written later by R9 from this object. So everything here is *internal*, consumed by R4 (strategy), R6 (planning), and R9 (writing).

The object below is the current five parts **plus four additions** (marked ★) that came out of the rubric discussion — mostly so R4 can judge depth and so the checks are actually gradeable. Each part notes which check it supports and who downstream uses it.

**Spine** — the one self-driven thing
- `activity` · `evidence_quote` (a real intake quote proving it's self-driven) · `confidence` (high / med / low)
- *supports check 4 (right spine) + check 3 (quote = no overclaim) · used by R4, R6, R9*

**Activities** — spine and every texture item, each with its signals ★
- `name` · `disposition` (maintain / demote) · **`signals`: how long · role · scale/level · result · verified-or-claimed**
- *the ★ signals are the main addition — they're what R4 weighs to judge depth. R1 records them; R1 never decides if they're "enough." · used by R4*

**Temperament** — personality → pacing
- each: `trait` · `pacing_implication` · `source_quote`
- *supports check 4 (pacing) + check 3 (quote) · used by R4, R6*

**Tailwinds** — advantages
- each: `asset` · `how_it_helps` (legacy connection; a 504 = extra time)
- *used by R4, R9*

**Guardrails (carried into the object)** ★
- `budget` · `location / travel_radius` · `free_hours` · `hard_nos` · `accommodations` · `stated_worry`
- *echoed here so the profile is self-contained and constraint-awareness is gradeable — supports check 2 · used by R4, R6, R7, the validator*

**Constraint tensions** ★
- notes where a passion clashes with a limit ("loves travel sport, but tight budget + rural")
- *supports check 4 (flag, don't solve — R4 resolves) · used by R4*

**Self-driven read** ★
- R1's own read of how self-driven vs parent-pushed the kid is
- *exists only to be auto-checked against the system's separate measure — supports check 4's cross-check*

**Flags to confirm**
- missing info · things to confirm · unproven claims · sensitive notes (ADHD / allergy)
- *supports check 3 (unproven → here, not stated as fact) · shown to the parent to fill in*

**Design note (decided):** the guardrails are **echoed** into R1's object (a copy), not just referenced from the intake. It costs a little duplication, but keeps the whole profile in one place, makes constraint-awareness directly gradeable, and matches the append-only state design. Flag for Nick if he'd rather reference them.

**Rule that still holds:** **no numbers in this object** — no chances, tiers, or score targets. R1 describes; the numbers come from modules. A number here is a bug.

---

## Scoring scale (same for every check)

| Level | Score | Means |
|---|---|---|
| **Strong** | 3 | Does the job fully. |
| **Okay** | 2 | Mostly there, small gaps. |
| **Weak** | 1 | Real problems, needs work. |
| **Missing / Broken** | 0 | Not done, or wrong. |

The four checks roll up into one **Fitness grade** (A–F). Dossier completeness is a **gate**: if it fails badly, we stop and go back to the parent before grading the rest.

---

## The four things we grade

### 1. Dossier completeness  *(the GATE)*

**Plain meaning:** Did the intake actually collect the raw material we need? This is about the *form*, not R1's thinking.

**Why it matters:** If key inputs are missing (like grades or test scores), the math steps downstream can't run at all. So this is a gate — fail it badly and we stop, then go back to the parent.

**What we look for:** the basics are present — grade/year, academics (GPA, test scores, AP/rigor if any), the list of activities, and the guardrails the parent gave: **budget, location / how far they'll travel, hours the kid has free, any hard "no"s, accommodations, and the parent's main worry.**

**Strong:** All the basics are there — Maya's GPA, activities, budget and location all captured.
**Weak/Missing:** No test scores and no budget — the plan can't be tiered or costed.

**Fix if low:** almost always **Ask the parent** or **Change the intake** — not R1's fault.

---

### 2. Profile completeness

**Plain meaning:** Did R1 capture what the kid has, in enough detail for R4 to use it? Two parts:

- **Must-haves are present:** a spine (or an honest "no clear spine yet" flag), a temperament read, and the guardrails carried through (budget, location, hours, hard-nos, worry).
- **Each activity is captured with its detail:** for every activity the kid has, we kept the *signals* the intake gave — how long they've done it, their role, how big/serious it is, any result. **Not** "does robotics" — but "has led robotics 3 years, built a competition bot."

**A kid does NOT need to do everything on our activity list.** Depth in one thing beats a little of everything. A dancer with deep dance and no research is **complete**. We grade what's *there*, not against a full menu. (The full list is only used to *prompt* the parent for more during intake.)

**R1 only *captures* the detail — it does NOT decide if it's "enough."** Whether Maya's robotics is deep enough is R4's call. R1's job is to not *drop* the detail, so R4 has something to weigh.

**Strong:** "Robotics — 3 years, team lead, built a bot for a regional competition." Detail preserved.
**Weak:** "Does robotics and dance." The detail the parent gave got flattened, so R4 has nothing to weigh.

**Fix if low:** **Fix the prompt** (R1 dropped detail that was there) or **Ask the parent / Change intake** (never collected).

---

### 3. Accuracy & no overclaiming

**Plain meaning:** Everything in the profile is (a) real — traces back to something the parent actually said — and (b) **not said more strongly than the evidence supports.** Anything unsure goes in **Flags**, not stated as fact.

**Why it matters:** A made-up or exaggerated claim hurts twice. The parent spots it ("we never said that / that's too strong") and loses trust. And the system treats it as real and builds a wrong plan on it. Same mistake, two kinds of damage. This is the most important check.

**Two halves:**
- **Real:** the spine and any strong personality claim point to an actual intake quote. Unproven things (a claimed award, a business with no proof) go in Flags, not stated as fact.
- **Not overclaimed:** the *strength* of a claim matches the *strength* of the evidence. "Nervous about contests she might lose" is supported; turning that into "hates all competition" is overclaiming, even though it's the same topic.

**Strong:** "Perfectionist who fears public failure" — and the intake literally says "she won't try things she might lose at."
**Weak (overclaim):** Intake says "runs a small Etsy shop" → profile says "a successful entrepreneur." Too strong.
**Broken (invented):** "A driven founder who quits when bored" — parent never said either. Score 0.

**Fix if low:** **Fix the prompt** — attach a real quote to every strong claim, keep the wording no stronger than the quote, push anything unproven into Flags.

---

### 4. Reading correctness  *(the real thinking)*

**Plain meaning:** The one place R1 is *allowed* to think. Did it read the kid well?

**What we look for:**
- **Right spine.** The spine is the thing the kid does **on their own** — not the most impressive-sounding one. If Maya *founded* a club because her parents pushed her, but builds robots alone at night, the spine is **robotics**, not the club.
- **Honest confidence.** If it's genuinely unclear which activity is the spine, R1 should say "low confidence," not fake certainty.
- **Cross-check with the self-driven signal.** The system separately measures how self-driven vs parent-driven the kid is. If R1 calls something a strong self-driven spine but that measure says "parent-driven," that's a contradiction we can catch automatically.
- **Temperament turns into pacing.** Each trait comes with what it means for planning. "Fears public failure" → "start with low-stakes practice before real competitions."
- **Notices tension with the family's limits.** If the kid's real passion clashes with a constraint (Maya loves a travel-heavy sport, but budget is tight and they're rural), R1 **flags the tension** — it does not solve it. R4 solves it.
- **Doesn't contradict itself.** Temperament says "avoids competition" but the framing pushes a competitive path — catch that.

**Strong:** Picks robotics as the spine, quotes the "builds bots at home" line, marks dance as texture, turns "perfectionist" into a pacing note, flags the budget-vs-sport tension.
**Weak:** Picks the parent-pushed club as the spine because it "sounds better," gives traits with no pacing meaning.

**Fix if low:** **Fix the prompt.**

---

## The grade

All four checks roll into one **Fitness grade:**

| Letter | Meaning |
|---|---|
| **A** | Ready. Hand it downstream. |
| **B** | Small fixes; usable. |
| **C** | Real gaps; fix before relying on it. |
| **D–F** | Not usable; rework. |

Dossier completeness (check 1) gates it — a bad fail there stops the run.

**Example read for Maya:** *"Fitness B. Complete and accurate, spine is right — but two temperament traits have no pacing meaning (check 4), so R4 can't sequence them. Fix: R1 prompt."* One line tells you what's wrong and what to do.

---

## What R1 is NOT graded on (on purpose)

So the rubric doesn't sprawl into other agents' jobs:

- **The wording / opinion level the parent reads** — whether it sounds warm, too sharp ("that's not my kid"), or too generic ("a motivated student") — is **R9's** job. R9 writes the words the parent sees; R1 only produces the underlying facts. **R1's only duty to trust is "don't overclaim," and that's already check 3.** The full "sounds like my kid" grade lives in R9's rubric.
- **Is the kid strong enough / is the activity deep enough** → **R4**. R1 just captures the detail.
- **What the kid should do to improve** (e.g. "join a real org to show impact") → **R4**.
- **Can the family afford this program / is it in range** → **R7 / the validator**. R1 only *flags* the tension.
- **Any number** — chances, tiers, score targets. R1 states no numbers by design; one showing up is a bug.

**How the "sounds like my kid" concern is split across two agents:** R1 must not *hand R9 an overclaim* (check 3, here). R9 must *word it right* (R9's rubric). If a parent ever says "that's not my kid," the two grades tell you where to look — R1 accuracy low = the *facts* overreached; R1 fine but R9 flagged = the *wording* was too sharp.

---

## Open questions for Nick

1. **The activity list** — confirm it's just the menu we *prompt* the parent with (kid needn't do all of it), not a checklist the profile is scored against. We think yes.
2. **The "must-haves"** for a usable profile — we have: spine (or flagged absence), temperament, and the guardrails (budget, location, hours, hard-nos, worry). Add or drop anything?
3. **One grade for R1** — we're proposing R1 gets a single **Fitness** grade, and the parent-facing "sounds like my kid" grade lives with **R9** (the writer). Agree with that split?
4. **The self-driven cross-check** — check 4 leans on the system's separate parent-driven-vs-self-driven measure. Confirm that's available to compare against R1's spine.
5. **Grade scale** — letters (A–F), or a 0–100 number?

---

*Covers R1 (the student profile). Next agents — R4 strategy, R6 plan, R7 recommendations, R9 writing — get their own rubrics the same way. The wording/tone dial we removed here lands in R9's.*
