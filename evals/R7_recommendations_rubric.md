# R7 Recommendations — Grading Rubric (v3)

*How we grade the real-world options the system hands a parent. Written to discuss and refine, not final.*

*v3 change: rewritten to the R1 v2 format. v2 had merged three overlapping "does it fit" checks into one and promoted verification to a gate; that holds.*

---

## The big idea, in one minute

**What R7 does.** R7 takes ONE task from the plan and finds real options a family can actually book. It answers one question: **"Where, specifically, does this happen?"** Nothing else.

**This is the highest-stakes step in the system, and it isn't close.** Every other step can be merely wrong. A parent *acts* on this one: they phone the number, pay the fee, put the date in the calendar, and drive their kid there on a Saturday. A fabricated program costs a family money and a child a term.

**Two kinds of thinking — R7 does the sourcing:**
- R4 decided what. R6 decided when. R7 finds **which**, and proves it exists.
- R7 never changes the task. If the task looks wrong while sourcing it, flag it — don't substitute a different one.

**What a recommendation is made of** (three parts):
- **The primary** — the real, verified option, with everything needed to book it.
- **A fallback** — at least one genuine alternative, including the free or school-based route where one exists.
- **The fit reason** — why this suits *this* kid. The judgment the profile page was forbidden from making lives here.

**Never a placeholder. Never an invention.** "A local debate program" is a failure. So is a plausible-sounding program that doesn't exist. **An honest escalation is a correct answer** — the system is built to say "we couldn't verify this, a human should look" and that outcome is a success, not a gap.

**R7 gets ONE grade: a Fitness grade** — could this family act on it today, and is everything in it real?

**How to read a low score — every miss points to one fix:**
- **Fix the prompt** — R7 had the catalog and used it badly, or invented rather than escalating.
- **Bad input** — the catalog row was incomplete, or the region has no coverage.
- **Ask the parent** — a constraint we needed (radius, format preference) was never collected.
- **Change the schema** — no slot for verification status or source.

Running example: **Maya, Grade 9** — robotics spine, rural address, tight budget, needs a low-stakes first competition.

---

## What R7 outputs

R7 produces **one thing per task: a recommendation object.** The parent sees it on the "this year" cards, written by R9.

**Primary option**
- `name` · `organisation` · `specific_session` (the actual class or event, not the org's whole catalogue) · `ages` **and** `age_fit_ok` (checked against this student, explicitly) · `format` · `location` · `price` **or** `price_note` ("call to confirm — not published") · `deadline` · `contact` (phone/URL)
- `verified` (true only if catalog-verified or research returned verified:true) · `source`
- *supports checks 1 and 2 · used by R9, and by the parent directly*

**Fallback options**
- same shape, each with `choose_this_if`
- *supports check 2 · used by R9*

**Fit reason**
- one or two sentences: why this format suits this kid, traced to something in R1
- *supports check 4 · used by R9*

**Escalation** ★
- `escalate` · `what_is_missing` · `what_was_tried`
- *★ the addition that makes "honest gap" a first-class outcome rather than a silent hole. Without it, a model with nothing to say invents something. · used by the human reviewer*

**Design note (decided):** when the catalog has no coverage, R7 **escalates rather than searching itself**. A separate research step runs the live web lookup with verification and merges results back. Keeping the two apart means a recommendation is always traceable to either the catalog or a verified lookup — never to a model's recollection. Flag for Nick if he'd rather R7 search inline.

**Rule that still holds:** **anything not verified is escalated, never shipped.** There is no third option.

---

## Scoring scale (same for every check)

| Level | Score | Means |
|---|---|---|
| **Strong** | 3 | Does the job fully. |
| **Okay** | 2 | Mostly there, small gaps. |
| **Weak** | 1 | Real problems, needs work. |
| **Missing / Broken** | 0 | Not done, or wrong. |

Verification is a **gate**, and it overrides: **anything unverified presented as verified caps the whole grade at F**, regardless of the other three checks.

---

## The four things we grade

### 1. Nothing unverified is presented as verified  *(the GATE)*

**Plain meaning:** Is everything here either checked, or honestly marked as not checked?

**Why it matters:** This is the only defect in the system that reaches a family as an *action*. They call a number that doesn't connect, or drive to a program that doesn't exist, or miss a real deadline because they were holding a fake one. It also destroys trust in everything else at once — a parent who finds one invented program reasonably assumes the rest is invented too, including the parts that were right.

**What we look for:**
- Every shipped option is catalog-verified or came back `verified:true` from research.
- Where nothing could be verified, `escalate` is set with what was missing and what was tried.
- No claim of having checked something that wasn't checked — including soft versions ("widely regarded as").

**Strong:** Catalog has no summer robotics option → escalates → research returns a verified session → shipped with its source URL.
**Weak:** A real organisation named, but the specific session invented.
**Broken:** A plausible program name with a phone number that doesn't connect. **Score 0, and the whole grade is F.**

**Fix if low:** **Fix the prompt.**

---

### 2. Bookable today

**Plain meaning:** Could the parent act on this without a second search?

**Why it matters:** A recommendation that requires the parent to go and research it has handed the work back. That is the work they are paying us for — and in practice it means it doesn't happen, so the plan quietly stalls at the first task. The age band matters more than it looks: it is the single most common reason a family turns up and is turned away.

**What we look for:**
- Name, organisation, the exact session, format, location.
- **The age band stated AND checked out loud against this student.**
- Price, or an honest "call to confirm — not published".
- The deadline, and how to make contact.
- At least one real fallback, including the free or school-based option where one exists.

**Strong:** "Ages 8–14 — a clean fit for a 13-year-old; in person at 1040 Park Ave or online; call (408) 904-9649 to confirm the fall price, not posted online; enrol before classes fill. Free alternative: ask whether her school fields a team."
**Weak:** Organisation named, no age band, no deadline, no contact.
**Broken:** One opinionated pick, unbookable, no fallback. Score 0.

**Fix if low:** **Fix the prompt**, or **Bad input** if the catalog row was incomplete.

---

### 3. Inside the family's limits

**Plain meaning:** Does it respect budget, travel radius and hard-nos?

**Why it matters:** A recommendation outside the limits isn't ambitious, it's a waste of the parent's attention — and it signals we weren't listening, which is worse than the wasted minute. For a rural family a "nearby" option two hours away is effectively a no.

**What we look for:**
- Never over the stated budget for that category.
- Inside the travel radius, with the real distance considered rather than the city name.
- Nothing on a hard-no list.
- A conflicting option is **flagged for human confirmation**, not shipped with a caveat.

**Strong:** Picks the regional league over the national circuit for a rural family with a $3–5k cap, and says why.
**Weak:** An option at the top of the budget with no acknowledgement that it uses the whole year's allowance.
**Broken:** A $6,000 program against a $3–5k cap. Score 0.

**Fix if low:** **Fix the prompt**, or the **validator** if it shipped past the guardrail.

---

### 4. Says why it fits this kid

**Plain meaning:** Does it explain, concretely, why this option suits Maya rather than any student?

**Why it matters:** This is where the whole system's knowledge of the child finally becomes visible to the parent. Everything upstream — the temperament read, the preference-vs-behaviour signal, the constraint work — is invisible until it shows up as "we picked this *because* of her." It is also the check that distinguishes a plan from a directory listing.

**What we look for:**
- One or two sentences, concrete, traced to something R1 actually recorded.
- The reason is about fit, not quality — "it's well-reviewed" is not a fit reason.
- Where the fit reason is about temperament, it is framed as a strength, never as a limitation.

**Strong:** "Team-based, and she preps with partners rather than competing alone — which is how she says she works best."
**Weak:** "A great program for aspiring engineers." True of everyone.
**Broken:** "Low-stakes, because she can't handle pressure." Correct reasoning, and a sentence no parent should read. Score 0.

**Fix if low:** **Fix the prompt.**

---

## The grade

| Letter | Meaning |
|---|---|
| **A** | Ready. A parent could book it today. |
| **B** | Small fixes; usable. |
| **C** | Real gaps; fix before relying on it. |
| **D–F** | Not usable; rework. |

Gated on check 1, **with an override: any unverified claim presented as verified is an F.** A beautiful recommendation a family cannot book is worse than an honest gap.

**Example read for Maya:** *"Fitness C. Primary verified and well-reasoned, constraints respected — but the age band is never checked against her and there's no fallback (check 2). Fix: R7 prompt."*

---

## What R7 is NOT graded on (on purpose)

- **Whether the task was worth doing** → **R4**. Sourcing a pointless task well is R4's failure surfacing here.
- **When it happens** → **R6**.
- **How it reads on the page** → **R9**.
- **Any odds or tier** → modules.
- **Whether the catalog is any good** → that's a data problem, not an agent problem. It surfaces here as **Bad input**, and the fix is the catalog.

---

## Open questions for Nick

1. **Does an escalation block the PDF**, or ship with a visible "we're still confirming this" note? We lean: ship with the note for one task, block if several.
2. **Catalog staleness** — how long before a verified row must be re-checked? A season for prices and dates; a year for the organisation existing?
3. **A local service with no verifiable named provider** — is "category + what to look for + a few real choices" acceptable as a primary, or always an escalation?
4. **Who owns catalog coverage by region?** R7 can only be as good as its catalog, and right now coverage is one metro area.

---

*Covers R7 (recommendations). Reads one task from R6; hands bookable options to R9 — and is the last step before a parent acts.*
