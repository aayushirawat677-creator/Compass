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

---

# Rules 32–42 — from the first real run

Everything above came from reading output. **These came from running it.** On 18–21 Sep 2026
Neerav's intake went through all ten agents with the live prompts, real modules and real gates,
and every step was graded blind against its rubric. Nine of eleven findings below are things
no amount of reading the prompts would have surfaced.

## 32. One fact, one place
- **Found:** the generated plan ran 9,200 words against a 4,036-word benchmark — 20 pages
  where 12 were wanted. The excess was almost entirely repetition: the business-fair
  registration dates appeared three times, the tennis-clinic rationale three times, roadmap
  stage bodies restated the task rows printed directly beneath them.
- **Rule:** a date, price, programme name, contact or rationale appears exactly ONCE, in the
  section that owns it. Elsewhere, point to it. Never restate.
- **Lands in:** `PROSE` contract — inherited by profile, gap, strategy, plan, writer.

## 33. Never narrate our own inputs to a parent
- **Found:** the draft told the reader "the intake does not say X" in nine places, and the
  profile lead opened with "Everything here comes from what the family and he said in the
  intake."
- **Rule:** "the intake does not say X" is a note to ourselves. The reader gets the action it
  implies — "confirm X". Provenance lives in the `flags` field and nowhere else.
- **Lands in:** `PROSE` contract.

## 34. No markdown in any string
- **Found:** four `**bold**` markers printed literally in the finished PDF. The Outcome Card
  takeaway reached the parent as `**One thread, carried the whole way**`.
- **Rule:** no `**`, no `_`, no backticks, no bullet characters inside a string. Emphasis is
  the template's job.
- **Lands in:** `PROSE` contract.

## 35. THE OUTPUT SHAPE CONTRACT — the largest single finding
- **Found:** four of nine gate verdicts on the first run were WRONG, and every one traced to
  shape drift. R1 returned `constraints` as a list of `{item, value}` pairs where the code
  reads `constraints.location` — that crashed the retrieval layer. R6 nested tasks one level
  deeper than `gate_plan` looked. R7 returned `primary`/`alternates` where the pipeline reads
  `recommendations`, so `gate_recs` passed a recommendation whose own escalate flag was true.
  Every prompt named its keys; none named its container types.
- **Rule:** a new shared `SCHEMA` contract. Return every key named in the spec even when
  empty; return each in the container type the spec names; never rename, abbreviate or nest
  deeper; no prose outside the JSON.
- **Lands in:** `SCHEMA` contract, plus an explicit shape block in PROFILE and PLAN_GOALS.
- **Note:** a false PASS is worse than a false FAIL. `gate_recs` was the only gate that let
  bad work through, and it was the one whose shape assumption was wrong.

## 36. Identity must be carried, and the cover must be read
- **Found:** the finished plan never named the child. Its cover read "Student name to be
  confirmed — the intake does not carry one." The name was in the intake; R1's schema had no
  field for it, so it was dropped before the writer ever saw it. The writer behaved correctly,
  flagging rather than inventing. The critic then missed it across all twelve of its findings —
  it audited the body closely and never read the cover.
- **Rule:** R1 returns an `identity` object (first_name, last_initial, grade, school, location,
  parent, class_of), copied verbatim. The writer uses the real name. The critic runs a cover
  and identity sweep FIRST, and any placeholder reaching the reader forces `escalate`.
- **Lands in:** PROFILE shape spec, WRITER, CRITIC section 0b.

## 37. Target colleges come from the family, never from inference
- **Found:** the run could not complete. The intake never asks which colleges the family is
  aiming at; R1 correctly refused to invent them; retrieval had no target and `gate_retrieval`
  escalated at step 3. The only college names anywhere in the intake were the mother's alma
  mater and the stepfather's employer.
- **Rule:** `intended.colleges` is a list. Empty if the intake names none, plus a
  flags_to_confirm entry. Never infer a target from a parent's own degree — a mother's Columbia
  degree is a fact about her, not a target for him. An empty list correctly stops the run; an
  invented one produces a confident plan aimed at schools nobody chose.
- **Lands in:** PROFILE shape spec. **Also an intake change:** the form must ask.

## 38. Length is a hard constraint, because a section is a page
- **Found:** cutting 5,700 words to 4,100 did not reduce the page count at all. Each section
  starts on a fresh page, so a section running four lines long costs a whole page, and the page
  it spills onto carries fifty words and looks broken. Five sections were each doing this.
- **Rule:** a per-section word budget totalling ~3,700, stated in the writer prompt as a defect
  of the same order as a wrong number. Plus the three section shapes that hold it:
  roadmap = three 35–45-word stage cards and one detailed year; this_year cards = two-sentence
  body then specification lines (`Primary — name · age fit · format · price`), with contact and
  plan-by untouchable; course = at most 4 target bullets and 3 stretch bullets, targets only.
- **Lands in:** WRITER. Also `render.py` CSS was tightened (body 11px/1.55 → 10.5px/1.42,
  narrower page margins) so a few long lines no longer cost a page.

## 39. Exactly one thread at core intensity
- **Found:** strategy returned twelve selected moves with no spike. The gate caught it, the
  retry came back with six — but still four of them marked `core`, which is the same failure
  one level down.
- **Rule:** whatever is marked `core`, there is ONE of it. Everything else is steady, maintain
  or subtracted. If two candidates both look core, the one with existing evidence wins and the
  other becomes its support.
- **Lands in:** STRATEGY.

## 40. Three rules that keep the Gap Analyst in its lane
- **Found:** graded C — the lowest score of the run. It counted the student's activities itself
  and got it wrong; it used categories outside the defined set; it made fit and priority
  judgments that belong to strategy; and its gaps carried no school stamp, so nothing
  downstream could reconcile them.
- **Rule:** count nothing yourself — every number was handed to you. The category set is
  closed: at_or_above / missing / lower_level, and an activity that exists at any level is
  `lower_level`, never `missing`. No fit or priority judgments anywhere, including in
  `grade_context`. Stamp every gap with its school and major.
- **Lands in:** GAP.

## 41. A task without a date is a wish
- **Found:** after the roadmap was cut to fit, the grade-8 rows had become stubs — "Register
  him.", "Check the next fair window." Technically dated, useless to a parent.
- **Rule:** each task is a full sentence saying what happens and why it falls in that week,
  roughly 12–20 words. The current year gets dated rows; grades 9–12 get none.
- **Lands in:** PLAN_GOALS shape spec, WRITER roadmap shape.

## 42. Two gate bugs, and one gate that was never switched on
- **Found:** `gate_draft` was defined in `gates.py`, documented in `GATES.md` and drawn on the
  orchestration diagram — and `pipeline.py` never called it. The writer's output reached the
  critic ungated. When finally run by hand it failed a correct document twice, on two bugs of
  its own: its percentage regex allowed one decimal place, so "15.64%" read as an unauthorised
  "64%", and its odds check fired on the phrase "not his odds" — the rule being obeyed.
  `gate_plan` and `gate_recs` had the shape bugs in #35.
- **Rule:** gates are code and get the same scrutiny as code. A gate nobody runs is worse than
  no gate, because the diagram says it is there.
- **Lands in:** `gates.py` (regexes fixed; `gate_plan` now walks the plan at any depth;
  `gate_recs` reads every shape R7 returns and honours a rec's own escalate flag) and
  `pipeline.py` (gate_draft wired in after the writer).

## 43. Write about the child, not about our file on him
- **Flagged on:** the generated plan, after the length and structure were already right.
  Aayushi: *"check the writing part on the profile and overall, it is way overboard. dont put
  what you are thinking on the pdf."*
- **What it was doing:** narrating the system's reading of a record instead of describing a boy.
  "The one thing in his record that is entirely his own is a Pokemon card business." "Five other
  activities sit alongside the business, each recorded at a different level, and two of his
  stated interests have nothing attached to them yet." Both are true, both are about our file.
  The same facts, written correctly: "He started it on his own, without anyone assigning it."
  "He competes across several areas — and tends to place when he does."
- **Rule:** say the thing, never how we came to know it, how complete it is, or what we were
  able to do with it. Banned in any sentence a parent reads: on record · recorded · no record ·
  stated · verbatim · as listed · as given · supplied · attached · not assessed · to be
  confirmed · evidence · the intake · what the plan can use. Anything that genuinely needs
  confirming is named once, as an action, in the flags box or the parent-action list.
  And one idea per sentence — three clauses with two qualifiers is two sentences, or a cut.
- **Lands in:** the shared `PROSE` contract, so profile, gap, strategy, plan and writer all
  inherit it.
- **Note:** this is the rule that separates the generated plan from the hand-written one. The
  structure, the facts and the length were already matched; the voice was the whole remaining
  gap.

## 44. Per-school admit pattern — the fix for "not assessed", and the calibration mechanism
- **Flagged on:** every school on the Two Paths card came back `sufficient: false`, fit "not
  assessed". The step was handed one corpus-wide tally — 67 students across six schools — and
  asked to assess fit school by school. It refused, correctly. A wiring failure, not a prompt one.
- **Fix:** `modules.admit_pattern_by_school()` — per college: how many admits we actually hold,
  their GPA and test bands, which credential types appear among them and how often, and the
  rung each credential typically reached. Wired into the Two Paths payload; the corpus-wide
  tally rides along separately.
- **It also answers the calibration question** Nick raised — *did we aim too high or too low?*
  For Neerav's six schools we hold 79–280 admits each. School/club level is modal for every
  credential type; national sits at roughly 10–20% of admits who hold that credential. So a
  national result is a real differentiator rather than the baseline, our target plan sits at
  the modal admit, and our stretch sits about one rung above it. That is the number to aim at:
  **the middle of the distribution, not the tail.**
- **One precision bug worth recording.** The first version read the level from the whole post,
  so "National Honor Society" and "international student" made *every* credential national at
  *every* school — a confidently wrong calibration that looked authoritative. The level is now
  read from a ±140-character window around the credential itself, with those phrases stripped.
  A calibration number that is wrong is worse than none.
- **Honest limit:** a level is only counted when the applicant stated one, and many do not.
  Modal level means modal *among those who said*.

## 45. Live research is the mechanism, not the fallback
- **Aayushi:** *"the program registry that we have is only for the debate. So if you are looking
  for any recommendation which is out of debate, then go to the live web search… Don't worry
  about the cost."*
- **Was:** the agent got an empty catalog, tried anyway, and research only ran afterwards if it
  escalated — a wasted call and a weaker recommendation.
- **Now:** when the registry has no rows for a task's activity, the pipeline researches FIRST and
  hands the verified findings over as the catalog. The after-the-fact pass stays as a second
  chance. Search depth is a setting (`RESEARCH_MAX_SEARCHES`, default 8) rather than a constant,
  and it is set for thoroughness.
- **Unchanged:** verification. A researched option still has to be real and bookable, or it
  escalates. Spending more does not lower the evidence bar.

## 46. Q8 exists — the engine was not reading it
- **Aayushi:** *"there is a question where it specifically asks… which colleges he intends to go.
  So look into that."* She was right. **Q8: "Has [child] mentioned any schools they like — even
  casually?"** is in the live intake form; real answers in the export read "NYU, Stanford,
  Berkeley, Chicago", "Michigan, Texas, Wisconsin, Duke, Vanderbilt, Indiana", "mit", "no".
  Our intake record simply never carried it, so the run stopped at step 3 every time.
- **Fix:** `schools_child_mentioned` (Q8), `college_ambition` (Q1) and `alumni_connections` (Q45)
  are now intake fields; `gate_intake` fails at step 0 with a specific message rather than
  letting the run die at step 3; R1 maps Q8 into `intended.colleges`; `data/INTAKE_FIELD_MAP.md`
  documents the mapping and the questions still unmapped.
- **The three traps, now written into the prompt:** a parent's own alma mater (Q45) is a hook and
  never a target; an ambition band (Q1) says how high, not where; a field of study is a major.
  Each of these was a plausible wrong answer to "which colleges", and R1 fell for the first one.

# Rules 47–51 — the positive structure

Rules 1–46 were almost all prohibitions. Given a list of things not to do and a hard
word budget, a model complies the cheapest way available: by deleting substance. That
is how a five-year plan became a date ledger for one year. These five say what a plan
must CONTAIN.

## 47. Capacity is computed, and homework is in it
- **Aayushi:** goals have to fit the hours the child actually has left. She worked the
  arithmetic out loud: 24 hours, minus school, minus sleep, minus leisure, minus what
  he already does — what remains is what a new goal may cost.
- **`modules.capacity_budget()`** computes it per grade: sleep, school and commute,
  homework, meals and downtime, then subtracts the hours already committed, read from
  the profile's own activity hours. So dropping a low-value activity returns its hours
  to the budget — subtraction is a real planning move, not a tidy-up.
- **Homework was missing from her arithmetic**, and it is the line that grows: ten
  minutes per grade per night, so an hour more per day by grade 11 than grade 8. Left
  out, every plan overcommits, worst in the years that matter most. For Neerav: 16.8
  free hours a week at grade 8, 13.5 by grade 12.
- **Summer is a separate pool** — no school, no homework, roughly 45 hours a week. The
  budget switches rather than scales, which is why the big commitments live there.
- **A correction made on the way.** The first version tapered sleep with age. That
  exactly cancelled the homework growth and made the budget look flat, so the claim
  "it tightens every year" was false as coded. Teens need 8–10 hours at every one of
  these ages, so sleep is now held constant and the budget genuinely tightens.
- **R1 must carry `hours_per_week` per activity.** It was in the intake and dropped in
  the profile, so the budget had nothing to subtract.

## 48. The arc, the goals, and what a task is not
- **Stages are relative to the student's grade.** Explore runs from now to grade 9,
  Solidify is always grade 10, Specialize is always 11–12. A grade 7 child explores
  for three years; a grade 9 child for one. Labels are two or three plain words and a
  colour — a visual band, not a paragraph.
- **Every grade gets its own goals, every goal its own tasks**, current grade through
  12. Not just this year. 3–5 goals for the current grade, 2–4 for later ones.
- **Target and stretch, at two levels.** A stretch GOAL is its own bullet in the
  semester or year it belongs to, never folded inside a target goal. A target goal may
  carry a stretch TASK beneath it. Both goals and tasks carry `track`, and the renderer
  colours each.
- **A task is a step sized to a term, not a diary entry.** "Enter one local tournament
  in whichever format he liked best" is a task. "Sept 22 — he decides what he is
  selling and sketches the booth" is a calendar, and it is what a plan looks like when
  it has no goals above it. Dates belong on the recommendation cards.
- **Levels, never ranks.** Taking part at a level is target; placing at it is stretch.
  No source we hold publishes a national ranking, so none is ever stated.

## 49. Three tiers, and the lead-time rule
- **Every recommendation shows free, budget and premium**, each with what it is, who it
  is for, format and cost, plus a budget check naming the family's ceiling when an
  option exceeds it. Where no free option exists, the card says so rather than dropping
  the tier. A single option is an instruction, not a recommendation.
- **`plan_by` is when to ACT, not the deadline** — weeks earlier, with the reason.
  **Never recommend something already inside its lead time.** If today is too close to
  the next occurrence, name the one after it with its date. A fair three days away is
  not a recommendation; it is a reason the family feels behind.
- **No quantity targets, ever.** Not revenue, sales, followers or hours raised. Any
  number a family can manufacture proves nothing, and inventing one is the failure the
  rule exists to stop. The outcome is verifiable instead — sell to customers outside
  the family and record what it made — and the figure comes back from the student
  afterwards. That also turns it from a number we invent into one we learn.
- **What counts, per category:** a deliverable, or a real outside body that can vouch.
  Research needs a paper or a recognised programme; arts a competition or a real
  institution; sports varsity or district/state/national; service a named organisation;
  venture registration and a ledger, or a role inside something that already exists —
  joining something real usually beats founding something small.

## 50. Plan → document reconciliation
- We already reconcile the Outcome Card against the plan in both directions (#17). The
  equivalent check for the roadmap never existed. So when the writer was told to cut,
  it cut R6's goals, and nothing noticed. **That is why the five-year plan could vanish
  silently between two steps.**
- **`gate_document`** fails the run when a goal in the plan never reaches the document,
  or when a whole grade does. Failure message: "the writer cut the plan, not the prose."

## 51. The budget ledger — sum the year, not the item
- **Aayushi:** the total of everything we recommend has to sit under the ceiling the
  parent gave. `constraint_guardrail` only ever checked one recommendation at a time,
  so four options could each be affordable and total nearly twice the limit. Nobody was
  adding them up.
- **`modules.budget_ledger()`** totals the year and the summer separately against their
  own ceilings, and enforces geography at the same time: an in-person option outside
  the family's stated region is dropped, and reported separately because it is not a
  money problem — dropping something else does not make it possible.
- **Three bugs found while testing it**, all of which would have blocked legitimate
  options: a stated range is a ceiling at its TOP ("$2,000–$5,000" means they can go to
  $5,000); a per-hour ceiling only compares against a per-hour price, never against a
  semester fee; and summer items must be detected to be charged to the summer ceiling.
- **`gate_budget`** retries rather than escalates: the fix is ours — drop or substitute
  the expensive item — not the parent's.

## 52. The calibration evidence reaches the steps that decide
- **The bug:** `admit_pattern_by_school` (#44) was computed just before Two Paths, at
  step 6. Gap is step 4 and Strategy is step 5. So the step that MEASURES the distance
  and the step that DECIDES what to do about it were the only two working without the
  evidence — and Plan, which sizes the goals, got it only by accident of ordering.
- **Fix:** computed once straight after retrieval, then handed to Gap, Strategy, Two
  Paths and Plan alike. Three lines of payload and one moved computation.
- **The rule all four now share:** aim at the MODAL level among admits who held that
  credential; the stretch is one rung above it. A credential a tenth of admits reached
  is a differentiator, not a baseline — putting it in the target plan states it as a
  requirement, which is both false and discouraging. Where a school's `sufficient` is
  false, say the distance cannot be measured there rather than borrowing another
  school's pattern.
- **This is the answer to "did we aim too high or too low."** It is the only check we
  have, and until now it reached one step out of four.

## 53. The critic could not see the contracts it enforces
- The critic is the enforcement layer, and it carried none of the five shared contracts —
  only its own numbered checks, written months of rules ago. So every rule added since
  (#32–#52: one-fact-one-place, no self-narration, no markdown, the plan's shape, levels
  not ranks, no quantity targets) was unenforced at the last gate before the PDF.
- **Fix:** CRITIC now carries EVIDENCE, TONE, PROSE, PLANNING_STRUCTURE and CARD_GRAMMAR
  verbatim, with one line above them: *the checks are the failures we have already seen;
  the contracts are the standard.* An audit of contract injection across all ten prompts
  also found gap, strategy, two_paths, projected and plan_recs missing the output-shape
  contract, and writer missing the plan's shape. All filled.

## 54. Four gates failed correct work on spelling, not substance
Found by running the whole pipeline on the new prompts. Every one of these rejected
output that was right:
- **`gate_gap`** held the category set with hyphens (`lower-level`) while the prompt
  specifies underscores (`lower_level`). A correctly categorised 66-gap map failed on
  punctuation.
- **`gate_strategy`** counted moves — "more than 6 is no spike" — while the prompt had
  been changed to require exactly one move at core intensity. Seven moves with one core
  is a spike with support; four moves all marked core is not. It was measuring the wrong
  thing.
- **`gate_plan`** knew only the old `current_year` shape and failed a correct five-year
  plan for not being a one-year plan.
- **`gate_document`** compared the plan's `8` against the document's `"Grade 8"` and
  reported all five grades missing.
- **The pattern, and the rule:** every time a prompt's contract changes, its gate is part
  of that change. A gate compares MEANING, never spelling — normalise both sides first.
  Four false failures in one run is what happens when prompt and gate drift apart, and a
  false failure costs a retry on every run until someone looks.

## 55. Three kinds of non-task
- **Found:** reading the grade-8 page, almost every row was something other than a task.
  *Research assignments handed back* — "Find out how a business his age registers and files
  here", "Find his high school's league", "Tell us which organisations ran the chess
  tournaments". The engine already knew the first: R7's free tier named the San Jose business
  tax registration and the Santa Clara County fictitious-name filing. That answer sat in the
  recommendations output and never reached the task. *States, not actions* — "Keep the ledger
  current", "Let it run", "Keep the same slot without growing it": nothing happens on any given
  day. *Decisions* — "Decide whether he wants a second fair": that is what a task produces.
  Plus one goal, "Go into grade nine with a week that fits", carrying course selection, French,
  dropping three activities, a question back to the parent, ping-pong and tennis.
- **Rule:** a task is ONE ACTION A PERSON CAN START. A task beginning "find out" / "confirm
  how" / "check whether" is resolved from the inputs, or its question goes in a new
  `needs_lookup` field for the recommendation step — never into the text a parent reads. A
  continuing commitment states what continuing looks like, with a check on it. A decision is
  written as the step that makes the decision possible. And one goal, one subject: if you
  cannot say what it is for without the word "and", split it.
- **Lands in:** PLAN_GOALS. Adds `needs_lookup` to the task schema.

## 56. The word budget ate the plan
- **Found:** R6 produced good tasks and the document printed fragments. Mean task length fell
  19.5 → 11.4 words, below the 12–20 floor rule #41 had already set. R6 wrote "Register for the
  Children's Business Fair – San Jose, run by Acton, at childrensbusinessfair.org — closes
  Oct 17, $50 booth fee"; the page read "Register for the Children's Business Fair." Three
  proper nouns vanished. `gate_document` (#50) passed it, because it checks that every goal is
  PRESENT and never that it still carries anything.
  The cause was arithmetic in my own prompt: roadmap was budgeted at 500 words for 60 tasks.
  At the 12-word floor that is 720 words of task text alone. The budget was unsatisfiable, so
  the model satisfied it the only way available — by deleting substance. This is the mechanism
  behind "the more rules I give you, the worse the PDF gets": a prohibition with no room left
  to obey it is an instruction to cut the content.
- **Rule:** the roadmap is a table of the plan, not a prose section, and has NO word budget —
  its length is whatever the plan needs. The budget is what you cut *from*: the prose sections.
  A task row is a full sentence, 12–20 words; every proper noun, price, age limit, named
  organisation and registration deadline R6 put in a task survives into the row. Only a diary
  date moves out; a registration deadline is what makes the row actionable and stays.
- **Lands in:** WRITER (budget rebalanced, roadmap exempted, compression banned),
  `gates.py` — `gate_document` now checks task-row length and fact survival, not just presence.
  Run against the failing document it reported: *48 of 60 rows under 12 words; 3 facts lost.*
- **Also:** the roadmap row spec named `{title, tasks}` while the template reads `row.goal`,
  `row.track` and `row.why_now` — #35 again, in my own spec, so every goal lost its why-now
  line. Spec corrected. And `cover.grade` carrying "Grade 8" into a template that supplies the
  word printed "Grade Grade 8" in every running header; normalised in `render.py`.
- **Result:** 11 pages, 62 of 62 rows rendered, mean 19.5 words, both gates PASS.

## 57. The term repeated is the term not organised
- **Found:** reading grade 8, the same goal carried two rows both tagged FALL — "Register
  the business" and "Open a ledger" — and the courses goal carried three tagged SPRING. The
  term was being stated four times down one goal and the grouping left to the reader. v10
  never does this: every goal there has at most one row per term. Worse, the current year is
  the one the family acts on, and goal-major ordering makes them assemble "what happens this
  fall" from five separate places.
- **Rule, two parts:**
  * THE CURRENT YEAR IS ORGANISED BY SEMESTER. `Fall 2026` / `Spring 2027` / `Summer 2027`
    are containers; the goals with work in that term sit inside, each with a track chip
    (DEBATE / VENTURE / SERVICE / ACADEMICS / SUMMER) and its tasks as plain bullets. Tasks
    carry no term field — the block above them already says it.
  * LATER GRADES keep the goal as container, with AT MOST ONE ROW PER TERM. Two same-term
    tasks merge into one row.
- **And the failure the fix created:** a goal spanning two terms printed its full title and
  its why-now line again in each. That is #32 on a new axis. A goal now states itself once,
  in the term it starts; later terms carry its short form, a `continued` marker and no
  why-now. Handled in the template, not the prompt — it is a rendering concern and the
  writer should not be asked to track what it has already said.
- **Lands in:** WRITER roadmap spec (two shapes, one per grade class), `render.py` (term
  blocks, track chips, continued-marker dedup), `gates.py` — `gate_document` walks
  `terms[]` and fails a later-grade goal with two rows of the same term.
- **Evidence:** run against the previous document the new gate reported the defect in 9 of
  20 goals across all five grades. Against the rebuilt one, PASS. 12 pages.
- **Fifth spelling bug in a gate.** The fact-survival check demanded the exact string:
  the plan said "Acton Children's Business Fair", the document said "the Children's Business
  Fair, run by Acton", and the gate called the name lost. It now matches on distinctive
  tokens rather than the literal phrase. Every gate bug so far has been this same mistake —
  comparing spelling where the rule is about substance. [#54]

### 57a. One layout, all five grades
I first applied the semester shape to the current year only, and left grades 9-12 goal-major
on the reasoning that a year four away does not need term detail. That was wrong, and it was
a judgement I made silently rather than surfacing. A parent reading grade 11 should not have
to learn a second layout to read it; less detail is a legitimate difference between grades,
a different format is not. All five grades now use `terms[]`, with the later years carrying
fewer goals and shorter task lists inside the same shape. `gate_document` fails any grade
that is not term-organised — which is how the previous document was caught.

## 58. Making the rules reach the steps that need them
Rules #55-#57 were written into the writer alone, which is where the defects showed up. That
is not where several of them belong. This pass pushed them to the right steps and fixed three
inconsistencies the edits had left behind.

- **The term contract is now shared.** `PLANNING_STRUCTURE` carries "the term is the unit of
  time, and the unit of reading", so R4, R5, R6, R7, the writer and the critic all have it.
  Six of ten prompts; profile, gap, projected and comparisons do not plan and do not get it.
- **R6 must stamp every task with one of four terms.** The document is assembled by grouping
  on that field, so a missing or invented term silently drops a task out of the reader's view.
  Previously the field was described but not constrained.
- **A contradiction in the writer.** The roadmap spec still said "each task tagged by term"
  two bullets below the rule that the term is now a heading. Removed.
- **A boundary that did not exist.** The roadmap and `this_year` both cover the current year
  and both are now term-organised, so without a line between them the writer says everything
  twice — and `this_year` ran over budget in both runs, which was the symptom. The roadmap
  owns what happens and when; `this_year` owns which programme and what it costs. Stated.
- **The critic got a structure section.** Sections 1-9 read the document sentence by sentence,
  which is why four rounds of review never caught a layout problem. Section 10 reads the
  roadmap as a shape first and reconciles it against the plan row by row.

### What running the critic found
First run of R8 on a real document with the contracts in it. Verdict **escalate**, 30 findings.
Section 10 worked: it reconciled all 5 grades, 19 goals and 62 rows, confirmed none missing and
none under 12 words. The serious findings were not structural at all —
  * an invented closing date ("registration closes that day" for Sept 26; nothing supplied it),
  * two cohort claims stated as "a majority of admits" where the corpus says 23-31% and 21-37%,
  * `n` stripped from all 14 cohort figures although the source supplies it for every one,
  * an invented "Far Reach" band the tiering module never produced.
The structure held and the evidence contract leaked. That is the opposite of what the last four
rounds suggested, and it is only visible because the critic finally ran.

**One false positive, and it is a design question.** Section 10 flagged all 17 multi-term goals
for repeating their title and why-now in every term. True of the JSON, false of the PDF — the
renderer collapses repeats to a short form with a `continued` marker. The critic reads JSON and
judges a document; those are different artifacts. Told it so explicitly. The general rule: when
a defect is fixed deterministically in the template, the critic has to be told, or it reports it
forever and its real findings get lost in the noise.

## 59. The appraiser — asking whether an activity is worth the years
Until now no step was allowed to ask whether an activity the family already does could ever
amount to anything. R1 describes and is forbidden from judging; Gap was narrowed in #40 for
straying into exactly this; Strategy takes the activities as given. So a thread with a low
ceiling was carried to grade 12 by default, and a student spent five years on something an
admissions reader would find nothing in. Those are years they do not get back.

### What was measured first
The idea rests on a claim we had never tested: that ventures with traction do better. Against
our own corpus — 2,617 valid posts, 756 mentioning a venture, 540 with a traction signal — the
raw numbers look supportive (68.5% top-25 admit with traction vs 65.3% without). They are a
confound. Post length alone moves the outcome from 51.6% to 71.1% across quartiles, and once
matched on length the traction effect is gone:
    Q2 62.8 vs 57.1 (p=.51) · Q3 69.3 vs 66.7 (p=.75) · Q4 71.6 vs **78.3** (p=.34)
    pooled Q3+Q4  70.7% (n=427) vs 72.2% (n=126)  **p=0.82**
It reverses in the longest quartile. Third hypothesis in a row that measurement killed, after
the major/retail rule and the corpus admit-rate idea. **So the step reasons and cites; it never
asserts a traction threshold, and the rubric fails any output that invents one.**

### Where it sits, and why there
After Gap, before Strategy — not before Gap, which was my first placement and was worse.
Sitting after Gap it gets `admit_pattern_by_school`, so a ceiling is set beside what admits to
*this student's six schools* actually held in that credential rather than against a generic
tier opinion. Strategy consumes the verdicts immediately as a fifth move, CONVERT.

### Two layers, and only one of them is cacheable
The TYPE — what a solo resale venture reaches, what transfers out of it, the routes — is true
for every student who has one. THIS STUDENT is never cacheable. So the agent runs on every
activity of every student, every time; `data/activity_ceilings.json` only saves it from
re-researching layer 1, and starts empty. Nothing is blocked on having a dataset first, which
was the right objection to my first framing of this as data-file-first.

### CONVERT
Not "stop doing this". The early grades build the skill; a later grade spends it somewhere with
outside validation. A conversion that does not USE the history is a replacement dressed as one
— the gate rejects it, because the history is the very thing that makes the student a credible
candidate for the new thing.

### The family decides the hard ones
A convert or retire on the student's longest-running or highest-hours thread sets
`needs_family_input` and writes a plain question. The plan is built as the activity stands
until they answer. We have never met this child; they have.

### What running it found
Five activities, cold cache, 3-5 searches each. Gate PASS, low confidence flagged on chess.
  card business  district  convert   ask  -> DECA/FBLA event ladder, or a shop role at grade 10
  ping-pong      school    keep_as_interest
  chess          state     carry     ask  (tenure and hours are both null — asked rather than guessed)
  cooking        district  convert   ask  -> FCCLA Culinary STAR / ProStart, which run the rungs above
  theater        school    keep_as_interest
The agent **corrected the seed cache entry**: I had written that an operating business can be
entered directly into a youth pitch competition; it checked the actual competition rules, found
they ask for an idea or plan rather than a live operation, and rewrote the route so the history
makes the entrant credible instead. The cache working as designed on its first run.

### Three bugs the run found
- `gate_appraisal` crashed on `hours_per_week: "4-6"`. Same range-parsing bug as the budget
  ledger. Takes the top of a range now. **Fifth** gate bug, and the second of this exact kind.
- The layer-separation guard rejected the pronoun "his" and threw away all five cache entries
  — "a student carries his trading history into the role" is generic prose. A pronoun is not a
  fact. It now matches child-specific FACTS: a grade number, an hours figure, a tenure, a named
  target school. All five stored after the fix.
- The agent reported the payload never carried the student's grade, so every timing judgment was
  relative to nothing. True — the wiring didn't pass it. Fixed, and `conversion.grade` is now
  constrained to an integer with the dependency in `grade_note`, because the agent wrote a
  paragraph into a field the plan schedules on.
