# Compass Engine — Feedback & Change Log

Running record of every correction, rule, and design decision Aayushi raises while
reviewing real outputs (starting with Neerav's plan). The point: fix it **once in the
engine** (prompts / modules / render), not per-kid. When she says "pull these out,"
this is the checklist to fold into `compass/prompts.py`, `compass/modules.py`,
`compass/render.py`, and the rubric docs.

Format: each entry = what she flagged → the durable rule → where it lands in the engine.

---

## 1. Profile (R1) must REPORT, never JUDGE
- **Flagged on:** Neerav profile, block 2 ("supporting cast"). The line "protect these,
  don't expand them" and "adding hours would pull time from the one thread" are
  *judgments/instructions* — they don't belong on the profile page.
- **Rule:** The profile page describes who the kid is and what the parent said. Any
  verdict about whether an activity *matters* for the target college is a backend /
  strategy-council / baseball-card-matching decision — NOT a profile statement. R1
  describes; R4 + backend judge.
- **Engine change:** `PROFILE` prompt in `prompts.py` — strengthen the "you describe, you
  do NOT judge" rule to explicitly cover activities: report each non-spine activity with
  its facts and results; never tell the family to keep/drop/protect/expand anything.
  Push the "does this help the target college?" question to STRATEGY.

## 2. Accuracy: state facts at the exact level the intake supports
- **Flagged on:** "trading ping-pong for tennis" (overstated), "wants French" (misframed).
- **Verified against intake:** ping-pong last year; **considering** a switch to tennis,
  not done (Q31, Q56). French = a stated wish for an **undergrad elective**, not a current
  activity (Q46). Chess = won medals at tournaments (Q37_followup). Cooking = **top-5
  finalist, district level, medal** (Q37_followup). Two elementary-school musicals (Q31).
- **Rule:** never state a claim more strongly than the evidence — "considering X" stays
  "considering," a future wish stays a wish. (This is already the R1 "no overclaiming"
  check; the engine honored it for the business but not here.)
- **Engine change:** reinforce in `PROFILE` prompt; add to R1 rubric examples.

## 3. Business claim — confirmed accurate (no change needed)
- "Actual customers, a few thousand dollars a year, saving toward a semester of tuition"
  verified against Q30 (his own voice). Good grounding; keep as the model for how tightly
  every claim should trace to a quote.

## 4. Temperament block: neutral tone, no derogatory predictions, no "verdict on the kid"
- **Flagged on:** Neerav profile, block 3. Lines like "shuts down under one-shot formats"
  and "a big competition as a first step would end with him quitting by winter" are strong,
  opinionated, and read as insulting the kid / making the parent feel bad.
- **Rule:** Report the temperament the parent stated (creative, leader, team player, driven,
  learns by talking, does best with structure and a way to recover). Translate each trait
  into a **positive or neutral** working-style statement — never a negative prediction or a
  judgment. A challenge the parent named (sensitive, perfectionist, hesitates, needs
  encouragement) is reframed neutrally as *how he works best* (structure, support, a path to
  recover), never stated as a flaw or used to predict failure. Never write that he'll quit,
  fail, or fall apart. Keep the parent's dignity and the kid's dignity intact.
- **Engine change:** `PROFILE` prompt — replace "TEMPERAMENT -> PACING: turn each trait into
  what it means for pacing" with a describe-only instruction: state temperament in the
  parent's terms, translate to a neutral/positive working-style note, and **do not predict
  outcomes or pass judgment**. The pacing *decision* (start low-stakes, etc.) moves to the
  STRATEGY/roadmap step, where a plan instruction belongs — not the profile page.

## 5. GLOBAL TONE RULE (applies to every string in every plan)
- **Rule (from Aayushi, verbatim intent):** The *source facts* come from the intake and are the
  ground truth. The *inferences/insights* we draw from them must be correct, and the **tone must be
  neutral or lightly positive — never opinionated, judgmental, condescending, or insulting**. A
  negative the parent shared is rephrased into a **neutral** statement, never highlighted as a flaw
  or a red flag. Not overly excited / hype either — keep it calm and even.
- **Corollaries:**
  - No red flags to the parent. Never frame anything as a weakness, a risk, or a reason he'll fail.
  - Don't mention things that don't matter for admissions or that only worry the parent (e.g.
    divorce / two-home schedule / "tires quickly / can't carry many" → say instead "a focused set
    of commitments he can sustain"). Remove "deliberately few," "the trim comes later," etc.
  - No outcome predictions about the kid ("would quit by winter," "well-rounded rejection").
  - Don't over-claim an advantage; state it at the level the intake supports (see #6).
- **Engine change:** this becomes the CRITIC step's core mandate (`CRITIC` prompt) — scan every field
  for negative/opinionated/hype/red-flag language and require a neutral rephrase — AND a tone line in
  every generating prompt (PROFILE, STRATEGY, PLAN_*, WRITER). Add a checklist of banned framings.

## 6. First-gen accuracy — first-gen AMERICAN ≠ first-gen COLLEGE (do not misapply the hook)
- **Flagged on:** block 4 said "first-gen applicants appear ~1.5× more among admits than rejects"
  and applied it to Neerav. But his **mom is a Columbia graduate** and **stepfather is a Stanford
  scientist** — so he is NOT a first-generation *college* student. The Top-10 "first-gen" hook almost
  certainly means first-gen *college*, which does not apply to him. Applying it is an incorrect
  inference (exactly the hallucination Aayushi wants avoided).
- **What IS true & fine to state:** he is a **first-generation American** (immigrant family) — national
  origin / background, a genuine diversity point. And the parents' degrees give a real **legacy/alumni
  tie at Columbia** + a Stanford research household — those are the actual advantages.
- **Fix applied:** block 4 now states first-gen American as background (no odds multiplier) and leads
  with the Columbia/Stanford household + Columbia legacy tie. Removed the 1.5× claim.
- **Engine change:** the dataset/corpus must distinguish first-gen-college vs first-gen-immigrant, and
  the GAP/STRATEGY steps must only apply the first-gen-college hook when the parent education actually
  fits. Add a guard: never attach a first-gen-college advantage to a kid with college-graduate parents.
- **OPEN QUESTION for Aayushi:** does your Top-10 dataset define "first-gen" as first-gen *college* or
  first-gen *immigrant*? That decides whether any first-gen multiplier can be cited for Neerav.

## 7. Every sentence must earn its place — cut redundancy and throat-clearing
- **Flagged on:** profile page. Three failure patterns, all systematic:
  1. **Thesis echo.** Every block's body closed by restating its own thesis ("not two separate
     hobbies" / "these aren't two pastimes"; "tends to place when he competes" twice; "team
     player" 4× in one block). The subhead+thesis IS the summary — the body must add new
     information, never summarize itself.
  2. **Throat-clearing openers.** "Set apart from the business, here is what his parent
     describes of the rest of his week"; "A note on what isn't on record yet…" — the section
     label already says this. Start with the content.
  3. **Internal process talk shown to the parent.** "…that's a question the strategy step
     weighs against the colleges he's aiming at." The parent doesn't need our pipeline
     explained. Route the decision to the backend silently; don't narrate the handoff.
- **Engine change:** WRITER prompt — "the body may not restate the subhead or thesis; no
  opening meta-sentence; never mention agents, steps, or how the plan was produced." Add to
  CRITIC as a cut-check: flag any sentence whose removal loses no information.

## 8. Word choice: never a word that reads as criticism of the child
- **Flagged on:** "the way he thinks is **argumentative**" — in ordinary English that means
  quarrelsome; a parent reads it as an insult. Also faint praise: "with **actual** customers,"
  "so there is **some** comfort on a stage" — both imply the bar was low.
- **Rule:** describe the trait with the warm/neutral word, not the clinical or pejorative one
  ("thinks by debating," not "argumentative"). Never use intensifiers that imply surprise that
  the kid cleared a bar. No hedge that damps a real achievement.
- **Engine change:** CRITIC gets a banned/replace word list; WRITER gets the positive-framing rule.

## 9. Don't leave good intake material unused
- **Flagged on:** the intake said "strong sense of justice and fairness" (the single best support
  for the law / public-affairs direction), "kind," "very socially adept, makes friends easily,
  people seek him out" — none of it reached the page, while filler sentences did.
- **Rule:** before adding any connective/summary sentence, check whether an unused, grounded
  intake fact would be more valuable in that space. Prefer evidence over commentary.
- **Engine change:** PROFILE prompt — require coverage of the stated character traits; WRITER —
  "prefer a concrete fact from the intake over a summarizing sentence."

## 10. Vague > concrete is a bug (the travel example)
- **Flagged on:** "a curiosity fed by travel he already writes about" — Aayushi: "what does this
  mean? It doesn't give any value." The problem was vagueness, not the fact.
- **Rule:** name the specifics or cut the sentence: "travelled to India, France, and on safari in
  Africa, and wrote about the India trip himself." A fact too vague to picture gets deleted.
- **Engine change:** WRITER — "every claim names its specifics; if you can't, drop the claim."

## 11. Soft skills / team orientation are a first-class asset — surface them
- **Raised by Aayushi:** "prefers working in a group" means he's a team player; leadership and
  communication are soft skills that matter for admissions, so highlight them.
- **Rule:** treat stated social/leadership traits (prefers teams, learns by discussion, socially
  adept, makes friends easily, sought out by peers, "Leader" tag) as load-bearing profile
  evidence, not colour. Name the asset plainly.
- **Engine change:** PROFILE prompt — add a required "social & leadership" signal to the
  temperament capture; WRITER — surface it as a strength, not a passing clause.

## 12. …but do NOT chain unsupported inferences off a trait (the "team player → good at sports" trap)
- **Flagged during the same discussion.** Proposed link: team player ⇒ therefore good at/suited to
  sports. **Rejected on evidence:** every competitive activity in his intake is INDIVIDUAL —
  ping-pong, tennis (considering), chess, the cooking competition. His actual collaborative
  evidence is theater (two musicals, ensemble) and, prospectively, debate (a squad activity).
- **Rule:** a trait may only be linked to an activity the intake actually evidences. Never infer a
  second fact from a first ("social ⇒ athletic", "leader ⇒ captain", "smart ⇒ good at math").
  One inference step from stated evidence, maximum, and it must be checkable against the intake.
- **Engine change:** PROFILE + WRITER — "each claim traces to one intake quote; no chained
  inference." CRITIC — flag any sentence asserting a capability the intake never states.

## 13. Backend signal: stated preference vs revealed behaviour is a MATCHING input
- **Observed on Neerav:** he *states* a strong preference for groups, but every activity he
  currently competes in is solo. That mismatch is genuinely useful — it argues for steering him
  toward team formats (debate squad, team events) where he'd likely do better and stay longer.
- **Rule:** this is a STRATEGY/council input, never a profile-page statement (per #1). The profile
  reports the preference; the backend uses preference-vs-behaviour gaps to rank recommendations.
- **Engine change:** add a `preference_vs_behaviour` signal to the profile's structured output
  (backend-only, not rendered), consumed by STRATEGY when selecting activity formats. Place the
  "this suits how he works" reasoning on the RECOMMENDATION card, where a judgment belongs —
  not on the profile page.

## 14. No abstract virtue-statements — spell out the concrete mechanism instead
- **Flagged on:** "the ability to lead a room, read people, and communicate well is one of the
  harder things to teach, and he already has it," and "the same collaborative instinct behind his
  stage work." Aayushi: these don't make sense and aren't important — they're asserted praise
  floating above the facts, not something the intake supports.
- **Rule:** never praise a kid in the abstract ("reads a room," "a natural communicator," "rare
  maturity," "hardest thing to teach"). Take the stated facts and write the chain out plainly,
  fact → consequence, so the parent can follow each step:
  *makes friends easily + others seek him out → gets along with people → works well in a group →
  can lead one*; and *learns by listening → is clear when he speaks*.
  Every link must be traceable to something the parent actually said.
- **Engine change:** WRITER — "state the mechanism, not the compliment; each asset is written as a
  short causal chain from stated intake facts." CRITIC — flag abstract praise and any sentence that
  asserts a quality without the underlying fact next to it. Add to the banned-phrasing list.

## 15. Read the positive trait OUT of a working-condition — but keep the condition
- **Raised by Aayushi:** the "how he learns" facts (clear instructions, visible milestones, a
  chance to retake) are being reported flatly as needs, when they actually evidence real
  strengths: he keeps a goal in view and works toward it (vision + follow-through), he aims high,
  he takes a second attempt rather than settling — i.e. he's diligent.
- **Rule:** when the intake states a condition someone works well under, name the strength it
  implies, in neutral language ("aims high," not "perfectionist"; "works toward visible
  milestones," not "needs milestones"). Write it as a capability, not a requirement.
- **ACCURACY GUARD (important):** do NOT upgrade this into unconditional resilience. Neerav's
  intake also carries the parent's stated worry — *"quits when the first step is a cliff"* — so
  "he recovers from any setback / doesn't quit" would contradict the source AND undercut the
  plan's own low-stakes-first logic. Keep the condition attached: *given a route back, he takes
  it.* True, positive, and consistent with the strategy.
- **General form:** a positive reframe may not delete the qualifier that makes it true. Check the
  reframe against the parent's stated worry before shipping it.
- **Engine change:** PROFILE — emit both the trait and its condition; WRITER — render the strength
  with the condition intact; CRITIC — flag any strength claim that contradicts the stated worry
  field, and any absolute ("always," "never quits," "any setback").

## 16. The projected card ("baseball card") must not state odds it cannot compute — OPEN DESIGN ISSUE
- **Found by tracing Neerav's card back to source.** The card is the most authoritative-looking
  element in the plan — percentages beside real university names — and was the least grounded
  thing in it.
- **What WAS real:** the cohort frequencies from the corpus (n=491 admits in his direction:
  service 60%, research 51%, internship 44%, venture 35%, debate 26%). These drove the four
  credentials, correctly and traceably. The strategic framing came from the Top-10 findings.
- **What was AUTHORED but rendered as if computed:**
  - the band percentages (Far Reach <15% / Reach 15–35% / Target 35–60% / Likely 60%+) and
    which college sat in which band — a judgment, not a calculation;
  - the stat row (GPA 3.8+, 1500+/34+, 6–8 APs, calculus by 12th) — estimates, not figures
    observed in the 491-admit cohort;
  - the college list itself — plausible for his direction and region, not retrieved.
  - `neerav_render.py` imports only `render`; it never called `modules.py` or the pipeline, so
    the existing `tiering()` was never invoked.
- **This violates our own EVIDENCE contract** ("assert only numbers you are handed; never
  compute, round, estimate or add one"). Prose was policed all session; the numbers were not.

### The structural problem
An **admits-only dataset has no denominator.** Admit rate = admits / applicants, and we hold only
admits. So a personal probability of admission is *not computable from this data at any point* —
not with better prompts, not with more rows. Any percentage we print beside a school name that
implies "his chance" is fabricated by construction.

### What the card CAN honestly claim (admits-only)
1. **Observed admit-pattern stats** — median/range of GPA, testing, rigour, math ceiling among
   the matched admits. Computable. Replaces my estimated stat row. Always carry `n`.
2. **Credential frequencies** — "service appears in 60% of admits in this direction." Already
   computable and already correct; keep.
3. **Pattern coverage / fit** — how much of the admit pattern his projected profile covers
   ("hits 4 of the 5 credentials present in ≥50% of admits here"). Expressed as a qualitative
   band — Strong fit / Developing fit / Stretch — never a percentage.
4. **School selectivity, cited separately** — the school's OVERALL published admit rate from
   IPEDS. A real external fact, labelled as the school's rate, explicitly not his.
5. **Suppression** — no school shown below `MIN_ADMITS_PER_SCHOOL` (5); say the data is thin
   instead of guessing.

### The fix
- Keep the visual (bands + cards); change what a band MEANS: fit to the admit pattern, not odds.
- Show selectivity as a separate, clearly-labelled IPEDS figure.
- Every card states `n`, the cohort it rests on.
- Renderer copy must change too: the current lead ("The realistic plan, turned into odds. Each
  percentage is a condition…") asserts exactly the thing we cannot support.
- **Engine change:** EVIDENCE contract gains a NUMBERS & ODDS clause (below); the card content
  must come from `modules.py`, never from a writing agent; `neerav_render.py`-style hand-authored
  plans must not bypass the pipeline.
- **DECISION NEEDED from Aayushi:** confirm the dataset is admits-only. If it also holds
  rejects/waitlists per school (the peer-discovery columns suggest it may), a real rate becomes
  computable for schools clearing the n-threshold, and option 4 changes.

## 17. The target/stretch card is the OUTPUT of the plan — derive it, don't invent it
- **Flagged by Aayushi:** the cards on pages 3 and 5 must be built from the goals, tasks and
  recommendations produced after gap analysis. They are "what this student's profile looks like
  at grade 12 **if they complete this plan**" — target card from the target plan, stretch card
  from the stretch plan.
- **Consequence:** every credential on a card must trace to selected moves/goals in the plan;
  every stat must trace to the course-plan targets. A credential with no task behind it is a
  promise the plan never keeps. Conversely a major goal with no credential on the card means the
  card under-sells the plan. The two must reconcile both ways.
- **Ordering:** gap analysis -> strategy (moves) -> goals/tasks/recs -> THEN the card. Never
  author the card first and back-fill tasks to match it.

### 17a. CORRECTION — derived from the plan, but written as ACHIEVEMENTS, not as the itinerary
- **First attempt got this wrong.** "Derive from the plan" was implemented as *cite the tasks*,
  producing credentials like "the class this fall, one novice tournament in spring, the summer
  session, the team in 9th, format in 10th, captain in 11th." That is the roadmap repeated — it
  duplicates pages 6–7 and violates #7 (no redundancy).
- **The card is the DESTINATION, not the route.** It shows what he HAS at the moment he applies:
  a résumé at grade 12, credentials carrying level, scale and duration, the way an admissions
  reader would file him. The route lives on the roadmap pages and appears on the card nowhere.
- **Test for a credential:** could it sit on an activities list or a résumé line?
  * YES — "State-qualifying debater; team captain, 2 years." "A five-year resale business with a
    documented growth figure and sales at public events."
  * NO — "Takes the Little Loudspeakers class in fall, then a novice tournament in spring."
- **Write for level and scale:** duration (five years), level reached (state, national), role
  (captain, led a team), and what an outside party verified (a judge, a placement, a figure).
  Vague virtue words ("a real credential", "a sustained role") are weak — name the thing.
- **Derivation is still required**, and is checked in the Critic: each achievement must be
  EARNED BY work in the plan. It just isn't written as that work.
- **Engine change:** WRITER — credentials are résumé-shaped outcomes at grade 12; never a
  schedule, never a task list, never a grade-by-grade recap. CRITIC — flag any credential that
  names a term, a grade or a program as a step, and any credential with no plan work behind it.

## 18. Rejects aren't "mixed up" — the unit is the APPLICATION, not the student (this fixes #16)
- **Raised by Aayushi:** "one student is rejected by multiple schools and accepted by multiple
  schools" — asked for a simple method.
- **The insight:** that is not messy data, it is the correct shape, and it is what supplies the
  denominator that #16 said we lacked. The corpus schema is already application-level
  (`post_id`, `college_raw`, `result`), so one ROW is one application. Rejection is a property
  of a (student, school) pair, never of a student. **This reverses #16's conclusion: a real
  rate IS computable.**
- **THE METHOD (simple, 5 steps):**
  1. **Never aggregate to the student for a school question.** Work in application rows.
  2. **Bucket the result** into admit / deny / other (waitlist, defer, withdrew).
  3. **Dedupe (student, college)** so a repeated row cannot inflate n.
  4. **rate(school) = admits / (admits + denies)** over the matched cohort only.
     'other' is excluded from both numerator and denominator, and reported separately.
  5. **Suppress below a decision threshold** (default 20). Thin data is stated as thin, never
     estimated around.
- **The one distinction that must never blur:**
  * "What does an admit look like?" (credentials, GPA/test ranges) -> **admits only**.
  * "How often does someone like this get in here?" -> **admits + denies**.
  Answering either from the other pool is the bug.
- **Honest labelling:** this is the rate *within our cohort in our data* — not the school's
  published rate, and not an individual's probability. Our corpus is self-selected, so it runs
  optimistic; say whose rate it is every time it appears.
- **Implemented:** `modules.cohort_rates()` and `modules.admit_pattern()` in `compass/modules.py`.
  Verified on synthetic data: duplicates don't inflate n, thin schools suppress, and one student
  correctly contributes an admit at one school and a deny at another.
- **Still to do:** run it against the real corpus (not present in this workspace) and replace
  Neerav's hand-authored band percentages with computed ones.

---
_(Add new entries below as they come up.)_

## 19. Two different "baseball cards" — name them apart, and write the visible one concisely
- **Clarified by Aayushi.** The system has two card-shaped objects and the shared nickname is
  what caused every mix-up so far:
  1. **MATCH KEY** — pipeline step 2, backend only, never rendered. A search query in the shape
     of a card; its sole job is retrieving real students admitted to the intended colleges. Done
     once matching completes.
  2. **OUTCOME CARD** — the target and stretch cards on pages 3 and 5. Content comes entirely
     from the gap analysis, strategy, goals and tasks. Produced by the WRITER at step 7.
- **Pipeline order ≠ page order.** The Outcome Card is among the LAST things computed (it cannot
  exist until the goals and tasks do) but appears EARLY in the PDF because that is what a parent
  wants first. Page position is UI and implies nothing about when content was produced. The
  roadmap is the reverse: computed earlier, printed later.
- **Naming bug found and fixed:** Neerav's visible card was labelled "TARGET PLAN · CLASS OF 2031
  · PROJECTED" — borrowing the backend step's own name on a page a parent reads. Now
  "TARGET PLAN · BUSINESS / LAW · CLASS OF 2031". Rule: the word "projected" never appears on
  anything a family sees.
- **CARD GRAMMAR** (adopted from the Profile Comparisons prompt, so both card types read alike —
  a parent sees them side by side):
  * Headline: one short phrase, most distinctive fact first, outcome in it where possible.
  * Stats: exactly 4, values short.
  * Credentials: 4–6; the HEADING is the credential stated flat with its level/scale/duration,
    the body is one or two short sentences. Heaviest first. Minor items consolidated into one
    line, never a bullet each.
  * Takeaway: one sentence, two maximum.
- **Also corrected:** the card leads said the percentages were "odds". Per #18 they are cohort
  rates within our data — relabelled, and shortened.
- **Engine change:** applied to PROJECTED (now explicitly the Match Key, with the distinction
  spelled out) and to WRITER's card section (naming + card grammar).
- **Still open:** the Outcome Card should become its own pipeline step with its own rubric rather
  than living inside WRITER; and the Profile Comparisons supplement needs a Critic carve-out so
  rule #5 doesn't strip other applicants' rejection lists (honest calibration, not negativity).

## 20. The Outcome Card is about THE KID ONLY — no cohort statistics, no academics repeat
- **Flagged on:** credentials carrying "only ~35% of this cohort ran a venture at all" and
  "service appeared in ~60% of the cohort". Aayushi: this is analytics, not Neerav. A parent
  reading this card wants to see **what their child's profile looks like in 2031** — nothing else.
- **RULE — no cohort/corpus statistics anywhere on the Outcome Card.** Percentages, frequencies,
  "compared to admits", "rarer than X" all belong to the BACKEND (gap analysis, strategy
  reasoning) where they do their real work of choosing what goes in the plan. They never appear
  on the card. The card states the student's own achievements, full stop.
- **RULE — never repeat the stat row in a credential.** The 4 stats (GPA, testing floor, rigour,
  math ceiling) already cover academics. A credential like "Floor cleared: 3.8+, 1500/34,
  calculus" is a duplicate and wastes one of only four slots. Academics live in the stat row;
  credentials are for everything else.
- **RULE — name the LEVEL of the achievement, concretely.** Not "a real argument credential" but
  what an admissions reader would actually see: state qualifier, top-ten in the state, national
  qualifier, top-ten in the country, Best Delegate, a committee award, a medal. The calibration
  for what level to aim at comes from the retrieved admitted profiles (backend); the card states
  it as this student's own result.
- **RULE — build each credential out of THIS student's real material.** Neerav cooks and has
  medalled at it, so his service credential is a cooking-based food-security programme he ends up
  running, not generic volunteering. Personalise from the intake, don't reach for a template.
- **DOMAIN INSIGHT from Aayushi (important, and it changes the plan):** an informal cash business
  carries little admissions weight. Unless it is **registered and filing**, it doesn't read as a
  real venture. So the entrepreneurial thread must be routed into things that do carry weight:
  register the business, and place him in an **early internship / a role inside an existing
  organization** where his pricing, sourcing and negotiation experience is actually used.
- **Applied to Neerav's plan (rule #17 — the card must be earned):** added a Grade 9 Model UN
  track, a Grade 10 "register the business" task, a Grade 10 summer internship placement, and
  made the Grade 8 service task cooking-linked. The four target credentials are now debate
  (state + captain), registered business + internship, cooking-led food-security programme, and
  Model UN with an award — each with plan work behind it.
- **Engine change:** WRITER card section — forbid cohort statistics and stat-row repetition,
  require a named achievement level, require personalisation from the intake. STRATEGY — when a
  student's venture is informal, generate the formalisation + internship/organization moves.
  CRITIC — flag any cohort statistic on the card, any credential duplicating the stat row, and
  any credential with no level named.

## 21. PLANNING CONTRACT — merged from the v10 plan (what v10 did better) + what our engine did better
Source: side-by-side of Aayushi's `Compass_Strategic_Plan_Neerav_v10_1.pdf` against our generated
plan, plus the unused `Tabroom-circuits.csv`. Adopted as a fourth shared contract, `PLANNING`.

### Taken FROM v10 (we were worse)
- **HORIZON RULE.** Only the current year gets named programs, prices, dates, contacts. Later
  grades stay at goals-and-tasks, and v10 *says so to the parent*: "It stays at goals and tasks
  here on purpose — specific programs and dates come later, when we can confirm them." We
  committed to named programs past the verifiable horizon.
- **EXPLORE, THEN COMMIT.** v10's thesis: "A strong profile isn't built by committing at 13."
  G8-9 sample several formats; G10 reviews, commits, drops the rest; G11-12 deepen and lead. We
  declared debate "his one spike" in grade 8 — locking in at 13, against the plan's own logic.
- **JOIN, DON'T FOUND** (stated 3× in v10): "Join something that exists — don't start one";
  "go deeper, don't start something new"; "real results matter more than a founder title"; and
  the business is "not a nonprofit made just for applications." Our card had him FOUNDING a
  cooking programme — the exact move v10 warns against.
- **CAP THE LOAD.** v10 G10: "Keep two to four activities." A number the family can hold.
- **SUMMER LADDER**, stated: freshman explore / short programme -> sophomore a real job ->
  junior a major programme + applications, business constant underneath.
- **NAMED BODIES AND PATHWAYS.** v10 uses Public Forum, Congress, Mock Trial, MUN, DECA, NSDA
  nationals, PSAT/NMSQT, National Merit, EA/ED, UCAS, Oxbridge PPE, Wharton, Ross. We wrote "a
  state qualification", "a pitch competition" — generic stand-ins where real names existed.
- **TABROOM WAS NEVER OPENED** (it was in the session the whole time). It gives the real ladder
  for a San José student: MSPDP / Middle School -> **GGSA (27 tournaments, the busiest CA
  circuit)** -> Coast Forensic League (16) -> NSDA -> NatCir (384) / TOC bids (110).
- **PARENT PARENTHETICALS** that answer unasked questions: "8th-grade grades don't count";
  "freshman summer can be light"; "colleges notice if he eases up."
- **OPERATIONALISED ALTERNATIVE ROUTE**: UCAS by mid-Oct, admissions tests, academic personal
  statement, "debate is the interview training." We name-dropped Oxbridge and stopped.
- **INSIGHT MUST REACH THE OUTPUT.** v10 puts Columbia in Reach *because* his mother is an alum,
  and says so. We identified the legacy tie in the profile and never let it touch a band.
- **HONEST NOTE with a concrete anchor**: "these rates come from students who chose to share
  strong results, so they run a little optimistic — even for the four hardest schools, only about
  one in four got in. The school names are examples, not a fixed list."
- **MUN correction:** it IS in v10 — as a grade-8 format to *sample*. We promoted an exploration
  option into a grade-12 credential with an award. Right item, wrong year, wrong weight.

### Kept FROM our engine (we were better) — do not lose these
- Current-year operational depth: real contact, phone, price or "call to confirm", registration
  dates, explicit age-fit check, and a `plan_by` per card.
- Current year split into Fall / Spring / Summer terms with dated tasks.
- Parent actions ordered by deadline with slack built in.
- The EVIDENCE / TONE / PROSE contracts: no judgment on the profile page, no red flags, no
  chained inference, causal chains instead of abstract praise, sensitive causes never named.
- Outcome Card as achievements, card grammar, no cohort statistics on the card.
- Application-level rate method (`cohort_rates`) and the cohort-rate labelling.

### Process failure behind most of the above
An example offered in conversation was transcribed into the output as if it were a finding, while
three reference files sat unopened in the session. Encoded in EVIDENCE: **a suggestion is a
hypothesis to verify against the intake and reference data, never content to transcribe.**

- **Engine change:** new `PLANNING` contract injected into STRATEGY, PLAN_GOALS, PLAN_RECS and
  WRITER; two new EVIDENCE clauses (use the reference data; examples are hypotheses); CRITIC
  section 8 enforcing all of it.

## 22. THERE WAS NO RETRIEVAL LAYER — agents could not use evidence they were never given
- **Found by Aayushi asking:** "is there no prompt where you need to retrieve relevant data file
  and read it when required?" There was not. Three concrete defects:
  1. **`catalog_json: []`** — `pipeline.py` passed the recommendation step an EMPTY catalog on
     every single run. The step whose whole job is naming real programs had nothing to name.
     That is the true origin of the `[CATALOG]` placeholders.
  2. **Tabroom and the findings report were not data sources at all** — no setting, no loader,
     passed to no step. "I forgot to open Tabroom" was the surface story; the engine had no way
     to open it.
  3. **An unexecutable instruction.** PLAN_RECS said "you may web-search, then VERIFY", but
     `llm.ask_json()` is a single-shot call with no tools. A model told to verify with no means
     of verifying produces output that merely READS as verified — worse than no instruction.
- **Fix — a deterministic retrieval layer (`compass/context.py`).** Python assembles the slice of
  reference data each step needs and passes it in; no model is asked to go find anything.
  * `settings.py` registers `CIRCUITS_CSV` and `FINDINGS_JSON`; `MIN_DECISIONS_FOR_RATE = 20`.
  * `data_access.load_circuits()` / `circuits_for(state)` — the real ladder. For California:
    **GGSA 27 tournaments** (busiest local), OCSL 20, Coast Forensic League 16, TCFL 13;
    entry = Middle School 33 / MSPDP; national = NatCir 384, TOC 110, NIETOC 34, NSDA 9.
  * `data_access.load_findings()` / `findings_for(track)` — `data/findings.json`, extracted from
    the real report with its source and caveat attached.
  * `data/catalog.csv` — the verified programs, with age bands, price, deadlines and contacts.
  * Packs: `for_gap`, `for_strategy`, `for_recs`, `for_writer`; all wired into `pipeline.py`.
- **Fix — live research made real (`llm.research_json`).** Anthropic web-search tool with a
  verification system prompt: the org must exist, the page resolve, the age band actually include
  this student, price/dates as published or plainly "not posted". Returns `verified:true` per item
  or `escalate:true` with what was tried. In mock mode / without a key it escalates honestly
  rather than pretending. `pipeline.py` calls it only when the catalog has no coverage.
- **Findings now in the engine (real, sourced, quotable):** academics are a floor (admits AND
  rejects centre on 1540/4.0/11 APs; ~36% of REJECTS scored 1550+); admits list FEWER activity
  areas than rejects (5.8 vs 6.2); hooks — athlete 2.4x, intl award 1.65x, ISEF 1.55x, first-gen
  1.5x; shut-outs over-index on volunteer HOURS. By track: **business = the lowest academic bar
  of any track, LEADERSHIP / DEBATE outweigh research**; **social science = research + debate,
  42% of top-10 admits**. Both directly validate debate as Neerav's spike — from the data, not
  from anyone's impression.
- **Still open:** the report does not say whether "first-generation" means first-gen COLLEGE or
  first-gen immigrant; the guard in EVIDENCE stays conservative until Aayushi resolves it.

## 23. The corpus is STUDENT-level, not application-level — column map was wrong, now fixed
- **Located:** `Peggy /Merged/acceptance_rejected_college_data_verified.csv` (10.5 MB, 2,723 rows)
  and `Peggy /ipeds-explorer/data/ipeds.sqlite` (233 MB).
- **`settings.CORPUS_COLUMNS` did not match the file.** It expected `college_raw`, `result`,
  `gpa_unweighted`, `test_score` — none exist. The real file is **one row per student (post)**
  with outcomes as `"; "`-separated LISTS: `accepted_colleges`, `rejected_colleges`,
  `waitlisted_colleges`, `deferred_colleges`, plus `gpa_band` / `test_score_band` (BANDS, not
  numbers) and `major_category` (STEM | Art/Hum | SocSci | Bus/Fin | Other).
  This is literally the "one student accepted by several and rejected by several" shape from #18.
- **Fixed:** `load_corpus()` now gates on `dedup_keep == Yes` and `post_status` valid, then
  EXPLODES the four list columns into application rows and de-dupes (student, college).
  **Result: 30,414 application rows · 2,613 students · 842 colleges · 15,251 admits / 10,456
  denies** — a real denominator for the first time.
- **`admit_pattern()` rewritten for bands.** GPA/test are recorded as bands, so it reports the
  modal band and the distribution with n. It no longer computes a median that does not exist.
- **FIRST REAL RATES — and they contradict my hand-authored card.** Neerav's direction
  (Bus/Fin + SocSci) = 451 students; filtered to the Target-plan floor (3.8+ and 1500+/34+) =
  186 students, 30 schools clearing n>=20:
  | school | n | rate | my hand-authored band | computed |
  |---|---|---|---|---|
  | Princeton | 50 | 18.0% | Far Reach <15% | **Reach** |
  | Stanford | 58 | 24.1% | Far Reach <15% | **Reach** |
  | Harvard | 63 | 27.0% | Far Reach <15% | **Reach** |
  | Columbia | 52 | 30.8% | *omitted entirely* | **Reach** |
  | UPenn | 77 | 31.2% | Reach | Reach ✓ |
  | Berkeley | 49 | 42.9% | Target | Target ✓ |
  | Cornell | 56 | 57.1% | Reach | **Target** |
  | Michigan | 42 | 64.3% | Target | **Likely** |
  | UCLA | 40 | 65.0% | Target | **Likely** |
  | Georgetown | 38 | 65.8% | Reach | **Likely** |
  I systematically UNDERSTATED the top schools and omitted Columbia — which v10 included, and
  correctly placed in Reach. **v10's honest note is corroborated by the data**: "even for the
  four hardest schools, only about one in four got in" ≈ 18–27% computed.
- **Self-selection is real and must stay on the page.** These are Reddit posters who chose to
  share results, so the rates run optimistic. Every rate ships with that caveat and its n.
- **LIMITATION FOUND — the Stretch card cannot be computed yet.** GPA banding tops out at
  "3.8+", so academics cannot separate the Target profile from the Stretch profile. That
  difference lives in ACTIVITIES, which exist only as free text in `post_body`. Computing a
  Stretch cohort needs an activity-signal extractor over that text (debate / venture /
  leadership / research markers) — the next real piece of work.
- **IPEDS not wired yet:** 233 MB, left in the Peggy folder; point at it with `COMPASS_IPEDS`
  rather than copying. Needs its table schema to write the query.

## 24. Admit rates come from the WEB, not the corpus — division of labour fixed
- **Decision by Aayushi:** pull admit rates from the web rather than computing them from the
  corpus. This is the right call and it resolves #16/#18 cleanly.
- **Why it's right:** the corpus cannot produce an honest rate. It is self-selected (Reddit
  posters who choose to share), AND 32.6% of posts list no rejections at all — measured effect:
  restricting to students who report at least one rejection moves Stanford 24.1% -> 17.0%,
  Harvard 27.0% -> 20.7%, Columbia 30.8% -> 26.5%. Two stacked biases, both upward.
- **THE DIVISION, which must never blur:**
  * **CORPUS** -> "what does an admit LOOK like": profile pattern, activities, credential
    frequencies, hooks. Never a rate.
  * **PUBLISHED TABLE (web)** -> "how selective is the school": official institution-wide
    admit rate, with its class year and source.
- **Built:** `data/admit_rates.json` — 33 schools with rate, class year, admits, applicants,
  source URLs and 13 name aliases; `data_access.published_admit_rate()` and
  `selectivity_band()`; `settings.ADMIT_RATES_JSON`. Bands now describe the SCHOOL
  (<8% Far Reach, <20% Reach, <50% Target, else Likely).
- **How different the truth is:** Harvard 3.59%, Columbia 4.90%, Stanford 3.80%, Cornell 8.41%,
  UCLA 8.98%, Berkeley 11.40%, Georgetown 12.17%, Michigan 15.64%, UC Davis 42.11%,
  San José State 84.61%. Every hand-authored band I wrote, and every corpus-computed band, was
  wrong in a different direction. Cornell is a Reach, not a Target. UCLA is a Reach, not Likely.
- **Prompt change:** EVIDENCE's NUMBERS & ODDS clause rewritten around the division of labour.
  Rates are handed over, never computed; stated as the school's own rate for a named class year;
  "Berkeley admits about 11% of applicants", never "he has an 11% chance". CRITIC gains checks
  for a rate without its class year, a rate worded as personal odds, and any rate sourced from
  the corpus.

## 25. When the data doesn't have it, go and look — generalised
- **Aayushi:** "some data you want and it's not available in the corpus — do the web crawl,
  look into Google or do a web search."
- **Built `llm.research_fact(question)`** — a general verified-lookup for ANY single missing
  datum, not just programs. Prefers the primary source (the institution's own page or its
  Common Data Set), always captures WHICH YEAR the figure refers to, notes source disagreement,
  and returns `found:false` rather than guessing.
- **Built `compass/refresh_rates.py`** — the rate table is now SELF-EXTENDING. Ask for a school
  that isn't in it and `ensure_rate()` looks it up live, verifies it, and writes it back, so the
  table grows as new families bring new school lists instead of being hand-maintained.
  `python -m compass.refresh_rates "Boston University"`.
- **`context.for_writer()`** now passes `published_rates` for every school on the list plus
  `rates_not_on_hand` — an explicit gap list, so a missing figure is escalated, never estimated.
- **The three fallback layers, in order:** reference data in `data/` -> live verified web lookup
  -> honest escalation. Never an invented number, at any layer.

## 26. Rubric grader built — and it scores the current plan 26/37 (70%)
- **`evals/grade.py`** — a runnable harness that scores a finished plan against the rules in
  this log. Every check traces to a defect Aayushi caught by hand; if the grader cannot catch
  it, the rubric is not real. `python evals/grade.py out/<plan>.plan.json`
- **Scores on the current Neerav plan:**
  | step | score |
  |---|---|
  | STEP 1 — Profile (R1) | 7/8 |
  | STEP 7 — Target card | 5/7 |
  | STEP 7 — Stretch card | 6/7 |
  | Numbers integrity | 3/5 |
  | STEP 5/6 — Strategy & plan | 2/6 |
  | STEP 6b — Recommendations | 3/4 |
  | **OVERALL** | **26/37 (70%)** |
- **Real defects it found that I had not:**
  * Profile blocks 1 and 3 still ECHO their thesis in the body (#7) — I fixed this once and it
    came back when I rewrote the bodies.
  * Two credentials name no level: "Food-security volunteering, led with his cooking" and
    "Founded the cooking programme" (#20).
  * The bands are STALE — still the corpus-era scheme (<15 / 15-35 / 35-60 / 60+) and still
    worded "in your dataset", months after rates moved to the published table (#24).
  * A recommendation with no contact (the 9th-grade scheduling card).
- **It confirmed the defect I already knew about:** "join, don't found" fails — the cooking
  programme I wrote from a conversational example directly contradicts the strategy (#21).
- **Strategy & plan is the weakest step at 2/6** — the horizon rule is never stated to the
  parent, no activity cap, no summer ladder. All three are things v10 does and we do not.
- **A grader weakness found while building it:** the first version passed the band check because
  I had allowlisted the OLD band edges. Tightened to require the published-rate scheme and to
  fail corpus-sourced wording. A rubric that grades against the previous rule is worse than none.
- **HONEST LIMITATION:** this grades the ARTIFACT, not the AGENTS. The engine is in mock mode, so
  no agent output exists to score. These numbers say how good the plan is, not how well the
  prompts perform. Per-agent scoring needs a real run (`LLM_MODE=real`) and then grading each
  step's slice of `--dump-state`.

## 27. The Strategy rubric was measuring the wrong thing — rewritten to be structural
- **Aayushi asked what was wrong with the Strategy & Plan rubric. The rubric was.** Four of its
  six checks searched for a specific PHRASE — "two to four activities", "specific programs and
  dates come later", a freshman→sophomore→junior sequence. That is a presence-of-boilerplate
  check, not a quality check: a plan could pass all four by pasting three sentences in without
  changing its strategy, and a genuinely good plan worded differently would fail.
- **Why Profile scored 7/8 and Strategy 2/6:** Profile's checks are mostly ABSENCE checks (no
  judgment, no cohort stats, no pejoratives). Absence of a defect is a real property of a
  document. Presence of a phrase is a string match. The score gap was partly an artifact of how
  the checks were written, not a fact about the plan.
- **RULE: prefer absence-of-defect and structural checks; use phrase-presence only as a last
  resort, and never for something a writer could satisfy verbatim without changing behaviour.**
- **Rewritten (2/6 -> 7/8), now counting and inspecting rather than matching:**
  * activity cap -> COUNTS threads per grade from grade 10 and asserts <= 4
  * summer ladder -> checks the summers actually ESCALATE (a real job/internship, then
    application work), rather than matching a sequence of words
  * horizon -> structural (later years carry no phone/URL/price) + disclosure in ANY wording
  * join-don't-found -> tightened so "we found the class" is no longer a false positive
  * NEW #17 card<->plan reconciliation: every card credential must have plan work behind it
  * NEW constraint check: no recommendation exceeds the stated budget
- **A FALSE FAILURE, caught and fixed:** "summers escalate" failed because my pattern looked for
  job / paid work / employment and the plan says **internship** — which is exactly that rung.
  The plan was right; the check was too narrow. **A rubric needs calibrating in BOTH
  directions: a false fail wastes a real improvement, a false pass certifies a defect.**
- **The one remaining Strategy failure is genuine:** "Founded", "initiative of his own",
  "program of his own" — the cooking programme written from a conversational example still
  contradicts join-don't-found in three places.
- **Score after the rubric fix: 31/39 (79%)**, up from 26/37 — most of that gain is the rubric
  becoming honest rather than the plan improving.

## 28. The grader did not implement the rubrics we wrote — corrected
- **Aayushi:** "these are the rubrics we created earlier, this is different from the rubric
  report." She is right, and the mismatch was structural, not cosmetic.
- **WRONG SUBJECT — the damaging one.** R1's rubric states plainly that R1 has **no
  parent-facing output**: the profile object is internal, consumed by R4/R6/R9, and the profile
  a parent reads is written later by **R9**. My grader read `plan["profile"]` — keys
  `title / lead / blocks / flags` — which is **R9's writing**. R1's real object is
  `spine / activities / temperament / constraints / flags_to_confirm`. So every "R1" score in
  that report was actually grading the writer. **A mislabelled rubric sends you to fix the
  wrong prompt** — that is worse than no rubric.
- **The Gap Analyst was not graded at all.** Six checks in the doc, zero implemented.
- **Wrong scale.** The rubrics score 0-3 (Strong / Okay / Weak / Missing) and roll up to one
  **Fitness grade A-F**. Mine was binary pass/fail with a percentage.
- **No gate.** R1 check 1 (dossier completeness) is a GATE — fail it badly and the run stops
  before anything else is graded. Not implemented.
- **No fix lever.** Every rubric check ends with a remediation: FIX_PROMPT / ASK_PARENT /
  CHANGE_INTAKE / CHANGE_SCHEMA / BAD_INPUT. That is the point of the whole exercise — a grade
  that tells you what to do. Not implemented.
- **Built `evals/grade_agents.py`** — implements R1 (4 checks) and Gap Analyst (6 checks) as
  written: per-agent, on the agent's OWN object, 0-3 scoring, Fitness A-F, dossier gate, and a
  fix lever on every sub-3 check. `evals/grade.py` is relabelled honestly as **R9 writing +
  modules** and now says in its docstring why it cannot grade R1 or the Gap Analyst.
- **First per-agent read (mock objects, so this measures the SCHEMA, not the prompts):**
  R1 Fitness **D (1.25/3)** — no temperament, no activities with signals, no evidence quotes,
  no flags_to_confirm. Gap Fitness **C (2.17/3)** — categories correct and it stays in its lane,
  but no meta block and no gap carries all five handoff fields.
- **SCHEMA GAPS FOUND in the PROFILE prompt vs the rubric's object spec** — the rubric requires
  fields the prompt never asks for: `activities[].disposition`, `activities[].signals`,
  `temperament[].pacing_implication`, `constraint_tensions`, `self_driven_read`.
  Fix lever: CHANGE_SCHEMA, then FIX_PROMPT.
- **CONFLICT SURFACED — and it reconciles.** The R1 rubric (check 4) requires temperament to
  carry a `pacing_implication`; our rule #4 moved pacing OUT of R1. These are not actually
  opposed: **rule #4 was about the parent-facing PAGE**, where a pacing note became a judgment
  and a prediction. The rubric is about the **internal object**. So R1 SHOULD emit
  `pacing_implication` internally for R4/R6 to use, and R9 must never render it as a verdict.
  Worth confirming with Aayushi, then encoding in both prompts.

## 29. R5 is missing from the ENGINE, not just the rubrics
- **Aayushi asked where R5 and R6 were.** R6 existed (`R6_plan_rubric.md`). R5 did not — and
  checking revealed it is absent from the pipeline itself, not merely from the rubric set.
- **The pipeline is `profile → projected → gap → strategy → plan_goals → plan_recs → writer →
  critic`.** Nothing produces the target-vs-stretch split. STRATEGY tags moves core/stretch, and
  then nothing consumes that tag. **The WRITER is inventing both cards** — the same bug class as
  the Outcome Card having no step of its own (#19), and it explains why the stretch card kept
  drifting into "four different achievements" instead of the same student pushed harder.
- **R5's job:** take the selected moves plus the plan and produce TWO coherent variants that
  share a spine — Target at stated intensity, Stretch the same threads earlier and harder — with
  an explicit `what_changed` delta stating the extra cost in hours and money.
- **A DESIGN TENSION THIS SURFACED, and it matters.** Under the published-rate model (#24), a
  school's band is FIXED — Harvard is 3.59% whether or not the student improves. So the v10
  visual where schools "move up a band" between Target and Stretch cannot mean the school became
  less selective. The two axes must stay separate:
  * **selectivity** = the school's published rate — a module, constant across variants;
  * **fit** = how well this student's projected profile covers that school's admit pattern —
    R5's job, computed from corpus admits with n.
  **The student's FIT moves; the school does not.** Any presentation implying otherwise is the
  exact conflation the numbers architecture exists to prevent — R5 check 5 scores it 0.
- **OPEN QUESTION for Aayushi (product call):** do we (a) show school + fixed published rate +
  a fit indicator that changes between plans, or (b) keep the "moves up a band" visual and
  redefine the band as FIT rather than selectivity? (b) preserves the v10 look but risks the
  parent reading it as the school's odds changing.
- **Also open:** where R5 sits — current thinking is after R4 and before R6, so R6 schedules the
  chosen variant. And whether Stretch may add a NEW thread at all, or only intensify existing ones.

## 30. RUNTIME GATES — stopping bad output before it propagates
- **Aayushi:** "rubrics for each step so that nothing goes down to meaningless result."
  That is a different mechanism from the nine rubrics. Rubrics grade a run AFTER it finishes;
  gates run DURING it and decide whether the next step may proceed.
- **The question a gate asks:** not "is this good?" but **"is this good enough for the NEXT step
  to be meaningful?"** A profile with no constraints doesn't score badly — it makes every
  downstream recommendation unbounded. Retrieval returning nothing doesn't weaken the gap map —
  it makes it fiction. **And the PDF still comes out looking complete, which is what makes it
  dangerous.**
- **Built `compass/gates.py`** — eight deterministic gates, one per boundary, wired into
  `pipeline.py` with a single automatic retry that hands the failure back as feedback.
  Four verdicts: PASS · **DEGRADE** (continue but mark the state — never silently) ·
  **RETRY** (re-run once) · **ESCALATE** (stop, no PDF, a human decides).
- **The gates:** intake (no constraints / no direction → ESCALATE) · profile (no spine, no
  constraints carried, any number in the object → RETRY) · **retrieval (no admits or MOCK cards
  → ESCALATE)** · gap (invalid categories, gaps citing no tally frequency, prescriptive language)
  · strategy (nothing selected, or nearly every gap selected — a pass-through not a choice, or
  >6 moves meaning no spike, or moves dropped with no tensions) · plan (no current-year plan, no
  dated task) · **recommendations (placeholder, or anything neither verified nor escalated →
  ESCALATE, never retry — a parent phones the number)** · writer (missing sections, a percentage
  never handed over, personal-odds phrasing).
- **IT CAUGHT A REAL, LIVE BUG ON ITS FIRST RUN.** The very first gated run blocked with
  `retrieval returned NO admits`. Cause: `match_rank` was still written against the corpus schema
  we ASSUMED (`student_id`, a `result` containing "accept"). After the corpus was rewritten to
  explode into application rows (#23) those columns no longer existed — so it returned **zero
  cards from a 30,414-row corpus** and the pipeline carried on with mock cards. Every gap, every
  strategy call and both Outcome Cards would have been computed against **fictional students**,
  and the PDF would have looked entirely normal. The bug was live and invisible; the gate found
  it in one run.
- **Fixed `match_rank` and `_tally`** for the exploded, band-valued corpus. Now: **334 cards ·
  38 real admitted students · modal GPA band 3.8+ (89%) · modal test band 1500+/34+ (79%)**,
  with peer colleges discovered from the admits themselves.
- **The quality trail.** `state["quality"]` records what every gate said, so a degraded run is
  visible as degraded and the trail says exactly where it weakened. A blocked run produces
  **no PDF, by design** — and a blocked run is a success of the system, not a failure of it.
- **Where gates end and rubrics begin:** a gate catches what is mechanically checkable — an empty
  field, an invalid category, a number nobody handed over. It cannot tell you the strategy picked
  the wrong spike or that the profile misread the child. That is what the nine rubrics are for.
  Both are needed; neither substitutes for the other.

## 31. CARD GRAMMAR extracted, and the Profile Comparisons supplement built as a real step
- **Aayushi shared the Profile Comparisons prompt** as the reference for card craft, to work on
  target/stretch. Two things came out of it.
- **A shared `CARD_GRAMMAR` contract**, now inherited by both the WRITER (Outcome Cards) and the
  new COMPARISONS step — because a parent reads both documents side by side and they must read
  alike. It fixes: the tag format; a ONE-phrase name leading with the distinctive fact and the
  outcome ("Five papers, NASA, no MIT"); exactly four stats with short values; 4–6 load-bearing
  credentials, heaviest first, **credential bolded with the explanation following**, minor items
  consolidated into one last line, concrete numbers kept; and a takeaway of ONE sentence (two
  maximum) with the scan-surviving phrase bolded, pointing back in the plan's own vocabulary.
  Voice: operational, not motivational; the reader is sophisticated.
- **`COMPARISONS` step added** — the two-page supplement. It did not exist in the engine at all.
- **IT RESOLVES THE R5 BAND QUESTION (#29).** The plan cannot honestly state this student's odds:
  the corpus is self-selected, and a published rate is the SCHOOL's, not the child's.
  **This supplement is the honest substitute** — rather than asserting a probability, show four
  real applicants and what their credentials actually bought. Calibration by receipts. That
  removes the pressure to dress fit up as odds on the Outcome Card, which was the whole tension.
- **Tiering is relative to THIS student's bands**, not absolute prestige: gold = admitted in the
  student's Far Reach band, purple = Reach (rejected from Far Reach), green = Target. Same
  vocabulary as the plan, deliberately.
- **Sort by outcome ceiling, descending — the ordering does the narrative work**, which is why the
  prompt forbids a synthesis section. Best case → strong case → "even this wasn't enough" →
  "this is what you're building toward."
- **CRITIC CARVE-OUT ADDED (section 0).** Without it, rule #5 would have stripped the rejection
  lists as "negativity" — they are honest calibration about OTHER applicants, and the most
  valuable content in the pack. The tone rules protect this student from being judged; they do
  not soften the evidence. This was flagged when the prompt was first shared and is now enforced.
- **Also encoded:** distrust any synthesis arriving with the source data — read the raw outcomes
  and form conclusions from them, because third-party optimism routinely outruns the outcomes.
  Two pages is a hard constraint; no cover, no how-to-read page, no synthesis page.
