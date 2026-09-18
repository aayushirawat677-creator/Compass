# Compass — Short Pipeline: Prompts, I/O & Rubrics (v1)

*The lean version of the strategy engine — 8 steps, not 11 agents. For each step: what it does, its input, its output, a paste-ready prompt (for the LLM steps), and a rubric (for the steps that need judging). Deterministic steps get a test note instead of a rubric. Built to be copy-pasted and tested against real intake forms.*

**Running example:** *Maya, Grade 9 — loves robotics (builds bots at home, regional level), also dances, perfectionist who fears public failure, GPA 3.9, tight budget + rural, intended college MIT (CS).*

---

## Pipeline at a glance

```
Intake form (parent + child)
      │
 1 ▸ Profile ............... who the kid is + constraints         [agent · rubric]
      │
 2 ▸ Projected Profile ..... backend "best-case" card (anchor)    [Claude call · light rubric]
      │
 3 ▸ Match & Rank Cards .... pull + rank admit baseball cards      [deterministic · test]
      │
 4 ▸ Gap Analyst ........... current profile vs cards → gaps       [agent · rubric]
      │
 5 ▸ Strategy .............. rank gaps, pick + prioritize moves    [agent · rubric]
      │
 6 ▸ Plan ................. goals + tasks + recommendations,       [agents + module · rubric]
      │                     two paths, college tiering
      │   └─ Constraint Guardrail (deterministic, multi-point) ── every rec within constraints
      │
 7 ▸ Writer ............... turn the plan into the PDF content     [agent · rubric]
      │
 8 ▸ Communication Critic .. control tone / honesty / visuals      [agent · rubric]
      │
   Strategic Plan PDF
```

**Governing rules (true everywhere):**
- **Agents never invent numbers.** Counts, GPA ranges, admit rates, tiers, probabilities all come from deterministic tallies/modules. An agent that states a number it wasn't handed is a bug.
- **Constraints come only from the Profile step (R1).** Every later step *reads and applies* them; none re-derives them.
- **No college tier is assigned off today's status.** For a grade 8/9 kid there's no GPA/SAT yet — tiers are computed *after* the plan, on the projected profile.
- **Verify before you recommend.** Any program that reaches a recommendation must be real/verifiable; if it can't be, escalate to a human.
- **Escalate on thin data.** When the intake is too sparse to determine colleges, or a web-found program can't be verified, hand it to a human rather than guessing.

**Fix levers** (used in every rubric): **FIX_PROMPT** (the agent had the info and misused it) · **ASK_PARENT** (intake lacked it) · **CHANGE_INTAKE** (we never asked) · **BAD_INPUT** (an upstream step handed it something wrong) · **ESCALATE** (needs a human).

---

## 1 · Profile  *(agent)*

**Role.** Read the intake and produce the structured picture of the kid — spine, activities, temperament, tailwinds, flags — plus the constraints. Describes; never judges or plans.

**Input.** The intake form (parent + child answers, transcript/scores if provided).

**Output — `Profile` (JSON):**
```json
{
  "spine": { "activity": "", "evidence_quote": "", "why": "", "confidence": "high|med|low" },
  "activities": [ { "name":"", "disposition":"maintain|demote",
                    "signals": { "duration":"", "role":"", "scale_level":"", "result":"", "verified":true } } ],
  "temperament": [ { "trait":"", "pacing_implication":"", "source_quote":"" } ],
  "tailwinds": [ { "asset":"", "how_it_helps":"" } ],
  "constraints": { "budget":"", "location_radius":"", "weekly_hours":"", "hard_nos":[], "accommodations":"", "stated_worry":"" },
  "intended": { "colleges":[], "major":"" },
  "flags_to_confirm": []
}
```

**Prompt (paste-ready):**
```
You are the profile analyst for Compass, a college-planning system. You read ONE student's
intake and produce the structured picture the rest of the plan is built on. You describe who
the student is — you do NOT judge whether they're strong enough, plan anything, or state any
number (no GPA you infer, no odds, no tiers). A number here is a bug.

FIND THE SPINE. Identify the one activity the student does self-directed, without being told.
Quote the intake to prove it. If none is clearly self-built, set confidence "low" and flag it —
a fabricated spine is worse than an honest "unclear." The most impressive activity is not
automatically the spine; the most self-directed one is.

CAPTURE ACTIVITIES WITH THEIR SIGNALS. For every activity, keep what the intake gave: how long,
their role, the level/scale, any result, and whether it's verified or just claimed. Do not
flatten "led robotics 3 yrs, built a comp bot" into "does robotics." You record the detail; a
later step judges whether it's enough.

TEMPERAMENT → PACING. Turn each personality trait into what it means for pacing (e.g. "fears
public failure" → "low-stakes reps before competitive stakes"), and cite the intake answer.

TAILWINDS. Real advantages, honestly — family/legacy connections, a 504 reframed as an asset.

CONSTRAINTS. Pull the guardrails verbatim: budget, location/travel radius, weekly hours, hard-nos,
accommodations, the parent's stated worry, and the intended college(s) + major.

RULES
- Ground every claim in the intake. Anything unstated goes in flags_to_confirm, never asserted.
- Never state a claim more strongly than the evidence supports ("small Etsy shop" ≠ "successful
  business").
- No numbers, no tiers, no recommendations.

Return only the Profile JSON. Use null / empty arrays rather than inventing content.

INTAKE:
{{intake_json}}
```

**Rubric — one Fitness grade (A–F).** Gated by Dossier completeness.
1. **Dossier completeness** *(gate)* — the intake collected the basics (grade, academics, activities, constraints). Low → ASK_PARENT / CHANGE_INTAKE.
2. **Profile completeness** — spine (or flagged absence), temperament, guardrails present; each activity captured with its signals. Judged on what exists, not a full menu.
3. **Accuracy & no overclaiming** — every claim traces to the intake; nothing invented; strength matches evidence; unproven → flags.
4. **Reading correctness** — right spine (self-directed, honest confidence); temperament→pacing; notices tension with constraints (flags, doesn't solve).
*(Tone/wording is NOT graded here — that's the Writer + Critic.)*

---

## 2 · Projected Profile  *(light Claude call — not a full agent)*

**Role.** Build a **backend, best-case "baseball card"** of *this* kid: if this student did their best and got into their intended college, what would their grade-12 profile look like? **Never shown to anyone.** Its job is to be the **ranking anchor** for pulling the most-similar real admit cards (Step 3). A light hint to the gap analysis at most — don't lean on it.

**Input.** The `Profile` + intended college(s) + major.

**Output — `ProjectedCard` (JSON):** a synthesized best-case profile — projected spine depth/level, the kinds of results/impact, academics, and the "pattern" an admit to that college/major tends to show — all clearly marked as *projected, not real*.

**Prompt (paste-ready):**
```
You are building a BACKEND reference card for Compass. Given a student's real profile and their
intended college + major, project what this SAME student's profile could realistically look like
by grade 12 if they did their best and got in. This card is never shown to the family — it exists
only to help the system find the most-similar real admitted students to compare against.

RULES
- Build FROM this kid's real spine and interests — project the kid they could become, not a
  generic admit. Keep their actual through-line at the center.
- Describe the PATTERN an admit to this college/major tends to show (depth in a spine, level of
  results, rigor) — you are capturing the thread, not a checklist to clone.
- Mark everything as projected. State no admit probabilities or tiers.
- Keep it tight — this is a retrieval anchor, not a plan.

Return only the ProjectedCard JSON.

PROFILE: {{profile_json}}
INTENDED: {{intended_colleges_and_major}}
```

**Light rubric — one check that matters:** **Grounded & realistic** — the projected card is built from the kid's *real* spine/interests (not a generic template), and the projected levels are plausible, not fantasy. A bad projected card ranks the wrong admit cards → wrong gaps, so it's worth a quick check. Fix: FIX_PROMPT.

---

## 3 · Match & Rank Cards  *(deterministic — test, no prompt)*

**Role.** Pull the real admit "baseball cards" from the Reddit corpus and rank them by similarity to the projected card.

**How it works:**
- **Pull by intended college + major.** For each intended college, pull cards of students **accepted** there.
- **Discover the peer set from the cards themselves.** On those same cards, look at the *other* colleges the student applied to / got into / was waitlisted or deferred at. The colleges that similar admits also landed at are a **data-driven signal for peers** — "students like this kid who got into MIT also got into X, Y, Z." Use that to widen the pull to profile-pattern peers, rather than a hand-fixed list. (Waitlisted/deferred at the intended college but accepted at a peer still counts — the thread is the same.)
- **Include:** accepted at the intended college OR at a peer surfaced by that signal.
- **Exclude:** rejected across tier-1 and landed only lower-tier (state/community) — different pattern.
- **Rank** the pulled cards by similarity to the **ProjectedCard** (Step 2); keep the top-similar set.
- **Tally** deterministic counts over the kept set (how many had research, GPA range, level distributions) — these are the numbers agents are allowed to cite.
- **Escalate** when the intake is too thin to determine intended/peer colleges, or too few cards match → human verifies the college set.

**Output.** The ranked admit-card set + the tally + a data-availability flag per college.

**Test (not a rubric):** retrieval correctness (right college/major filter), include/exclude rule applied, ranking stable, tally counts correct, thin-data escalation fires. Unit-tested.

---

## 4 · Gap Analyst  *(agent)*

**Role.** Compare the kid's **current** profile to the ranked admit cards and report **every real difference**, factually and completely. Diagnoses; does not rank by importance or prescribe (that's Strategy).

**Input.** `Profile` (current) + ranked admit cards + tally + grade/years-remaining.

**Output — the gap map:** per target, a list of gaps, each with `category` (at-or-above / missing / lower-level / **unknown-interest**), kid_state vs admit_reference, `level_gap` (school→regional→state→national→international) or academic `magnitude`+`within_range`, `frequency` (from tally), `grade_context`, `evidence_ref`; plus a cross-school roll-up and meta (cards used, thin-data skips).

**Two gap types to name explicitly:**
- **Known gap** — the kid's activity maps to admits but is lower-level, or an activity admits had is missing. Measurable against the cards.
- **Unknown-interest gap** — the kid has a genuine interest (e.g. rockets) that **no admit card shows**. Not a deficit — flag it as an *unmapped interest to develop*; the Plan step researches how to grow it into something with impact.

**Prompt (paste-ready):**
```
You are the gap analyst for Compass. Compare this student's CURRENT profile to a set of similar
ADMITTED students, and report every real difference — completely and factually. You diagnose. You
do NOT decide which gaps matter (that's the strategy step) and you do NOT say how to fix them.

RULES
- Compare the CURRENT profile (the kid may be grade 8/9 with lots of runway), never a projected one.
- Numbers (counts, GPA ranges, frequencies) are GIVEN to you in the tally — cite them, never invent
  or recount them.
- Categorize each difference:
    at-or-above  = kid meets or beats admits here (a strength — report it, it's not a hole)
    missing      = admits had it, kid doesn't
    lower-level  = kid has it, but lower on the ladder school→regional→state→national→international
    unknown-interest = the kid has a real interest NO admit card shows — flag it to develop, don't
                       force-fit it to an admit pattern
- Report ALL real gaps, including small ones (a 0.05 GPA gap) with their size and a within-range
  flag. Do not pre-filter for importance — completeness is your job; a later step ranks.
- Never invent a gap, and never compare against a college with too few cards — flag it thin instead.
- Read grade context: for a young kid, "missing X" is a roadmap item with runway, not a failure.
  Never say "can/can't get in" — you measure distance, not verdicts.

Return only the gap-map JSON.

CURRENT PROFILE: {{profile_json}}
ADMIT CARDS (ranked): {{cards_json}}
TALLY: {{tally_json}}
GRADE / YEARS REMAINING: {{grade}}
```

**Rubric — one Fitness grade.**
1. **Coverage** — a gap read for every target and domain.
2. **Accurate & grounded** — real gaps only, tallies cited not invented, thin schools flagged.
3. **Correct categorization** — at-or-above / missing / lower-level / unknown-interest right; ladder read correctly.
4. **Complete incl. small & strengths** — lists tiny gaps and strengths; no pre-judging (that's Strategy).
5. **Stays in lane** — no ranking by importance, no fixes, no numbers invented, no "can get in."

---

## 5 · Strategy  *(agent — R4)*

**Role.** Rank the gaps for relevance to *this* kid, and select + prioritize the **moves** that close the ones that matter. Understand the *pattern* behind admits and grow the kid's own interest to fit it — don't clone. Selects and orders moves; does not schedule, resource, or set tiers.

**Input.** The gap map + `Profile` (spine, temperament, constraints) + intended colleges.

**Output — selected moves:** each with `which_gap`, `why`, `priority`, `dependency_order`, `intensity` (core | stretch), plus dropped moves (with who/why) and tensions.

**Prompt (paste-ready):**
```
You are the strategy lead for Compass. You are given every gap between a student and similar
admitted students. Decide which gaps actually matter for THIS kid and turn them into a prioritized
set of MOVES. You reason as four voices that disagree on purpose and you report both the plan they
agree on and where they don't:
  STRATEGIST — maximize fit to the admit pattern.
  ADVOCATE  — a plan the kid will actually finish (owns temperament; name what they'll quit).
  BUDGET    — sustainable in the kid's weekly hours (dollar/location limits are enforced later).
  SKEPTIC   — is the evidence real, or is the gap thin?

HOW TO CHOOSE
- Relevance first: keep gaps on the kid's spine/direction and grade-appropriate. Don't chase a gap
  just because an admit had it. A grade-9 kid explores/deepens; don't over-specialize them.
- Grow the kid's OWN interest toward the admit PATTERN — enhance, don't copy. For an unknown-interest
  gap (an interest no admit card shows), decide it's worth developing and pass it on to be researched.
- Fit the kid: don't select a move-type the kid will abandon (temperament) or that blows past their
  rough weekly capacity. Subtraction is a valid move when they're overloaded.
- Set dependency order (build-up before a high-stakes push). Tag each move core or stretch.

RULES
- State NO numbers, odds, or tiers. Refer to direction in words only.
- Every dropped contested move is recorded in tensions with which voice killed it and why.
- You do NOT schedule by semester, name programs, enforce budget/location, or compute tiers — those
  are later steps. You choose and order moves.

Return only the moves JSON (selected_moves, dropped_moves, tensions).

GAP MAP: {{gap_map_json}}
PROFILE: {{profile_json}}
INTENDED: {{intended_colleges_and_major}}
```

**Rubric — one Fitness grade.**
1. **Right moves** — relevance + stage fit (on-spine, grade-appropriate, closes gaps that matter).
2. **Fits the kid** — sustainable (won't be abandoned), within rough capacity, right dependency order. *(Not dollar/geo — that's the guardrail.)*
3. **Honest tensions** — surfaces trade-offs, records dropped moves and why.
4. **Stays in lane** — selects/orders moves only; no scheduling, programs, tiers, numbers, or invented constraints.

---

## 6 · Plan  *(agents R6 + R7, module R5 — with the Constraint Guardrail woven in)*

**Role.** Turn the prioritized moves into the actual strategy: **goals + tasks** across grades 8→12, **recommendations** for the immediate two semesters, a **target and stretch** version, and the **college tiering** — all inside the parents' constraints.

**Input.** Selected moves + `Profile` (constraints) + gap map + grade + the verified program catalog.

### 6a · Goals & Tasks  *(agent — R6)*

**Output.** A grade-staged arc (8→12) of **goals** (yearly / semester / short 10–20-day) and their **tasks**, organized around the spine. Only the current + next semester get dated detail.

**Prompt (paste-ready):**
```
You are the planner for Compass. Turn a set of prioritized, already-chosen moves into goals and
tasks across the student's remaining grades. The strategy is decided; your job is realistic,
grade-appropriate scheduling — not strategy, not resources, not odds.

RULES
- Work only from the given moves. Each goal maps to one or more of them.
- Grade stages: grade 8–9 explore + build breadth/depth; grade 10 commit and go deep; grade 11–12
  specialize and create real impact. Place goals to match where the kid is.
- Goals can be long (a 2-year GPA target), semester, or short (10–20 days, e.g. "get selected for
  competition X"). Tasks are the concrete steps under each goal.
- Only the current + next semester get dated task-level detail. Outer years are a coarse arc.
- Respect the weekly-hours capacity; if a term is overloaded, stagger and say so. Organize around the
  spine; depth over breadth.
- State NO numbers that belong to modules (odds, tiers). Refer to gaps in words.

Return only the plan JSON (multi_year_arc + current/next-semester goals with tasks).

MOVES: {{moves_json}}
PROFILE/CAPACITY: {{profile_json}}
GRADE: {{grade}}
```

### 6b · Recommendations  *(agent — R7, fans out per task)*

**Output.** For each *near-term* task, real resources — one recommended + 2–3 alternates, each with a "choose this if" — from the **verified catalog**. For an **unknown-interest** task with no catalog match, do a **web search**, then **verify** the program is real (URL resolves, cost/deadline check) before recommending; if it can't be verified → **ESCALATE**.

**Prompt (paste-ready):**
```
You are the recommendation matcher for Compass. For ONE task, recommend real, specific resources a
family can act on — from the verified catalog you are given. Give one recommended option plus 2–3
alternates, each with a "choose this if" clause.

GRANULARITY RULE (important)
- Be specific enough to act on, but never name a single local person/place you can't defend (a named
  neighborhood tutor/coach). For a local service, recommend the CATEGORY + what to look for + a way to
  compare ("a diagnostic-first ACT tutor, ~$X/hr"), and give the parent a small set of choices — not
  one opinionated pick.
- Online/national resources may be named specifically if they're in the verified catalog and scored.

UNKNOWN INTEREST
- If the task grows an interest the catalog doesn't cover (e.g. rockets), you may web-search for real
  programs/labs/competitions. Then VERIFY each (does it exist, does the link resolve, cost/deadline/
  eligibility) before recommending it. If you cannot verify it, or it feels like a guess, do NOT
  recommend it — flag ESCALATE for a human.

CONSTRAINTS
- Never recommend anything over the family's budget, outside their location/travel limits, or on their
  hard-no list. If an offline option is out of their area, flag it for human confirmation, don't ship it.

Return only the recommendation JSON for this task.

TASK: {{task_json}}
CATALOG CANDIDATES: {{catalog_json}}
CONSTRAINTS: {{constraints_json}}
```

### 6c · Constraint Guardrail  *(deterministic — woven, multi-point)*

Runs **as recommendations are formed and again before the plan is finalized** — nothing reaches the family that violates a constraint. Deterministic checks:
- every recommendation/task **within budget** (per item and total) · **within location/travel radius** · not on a **hard-no** · within the **weekly-hours** cap.
- an offline option **outside the kid's area** → **human confirm**, never auto-shipped.
- a web-found program that **couldn't be verified** → blocked, escalate.

*Test (not a rubric):* feed deliberately over-budget / out-of-area / unverified recommendations — each must be caught 100% of the time. Checked at more than one point so nothing leaks.

### 6d · Two paths + College tiering  *(module — R5)*

**Output.** A **target plan** and a **stretch plan** (stretch = a higher bar on the same task — "top-10" → "top-3" — plus, only if genuinely valuable, a small add-on). Then the **college tiering**: a balanced list of ~10–20 colleges — weighted toward the intended college + major, balanced with realistic reach/target/likely — each with a tier (likely / target / reach / far-reach) and a probability, computed on the **projected** profile under each plan. *(Numbers are the module's; agents don't set them.)*

### Plan rubric — one Fitness grade (covers 6a/6b/6d judgment; 6c is a test)
1. **Right goals/tasks** — each maps to a real move, grade-staged correctly, organized around the spine.
2. **Feasible** — within the weekly-hours cap; near-term detail only; realistic durations.
3. **Recommendations specific-but-safe** — actionable, from verified sources, **never a named local pick**, unknown-interest programs verified or escalated.
4. **Constraint-clean** — no recommendation/task outside budget/location/hard-nos (backed by 6c).
5. **Two-path integrity** — target genuinely achievable; stretch a real-but-honest push; the two are meaningfully different.
6. **College list sensible** — weighted to the intended college/major, balanced across tiers, respectable volume (~10–20), thin-data → escalate.

---

## 7 · Writer  *(agent — R9)*

**Role.** Turn the finished plan into the **PDF content** — the profile prose, the goals/tasks/recommendations, the two paths, the college tiers, the closing note, and the **final projected card** the parent actually sees (built from the real plan). Writes what was decided; invents nothing and states only the numbers it's handed.

**Input.** The full plan (moves, goals/tasks, recommendations, two paths, tiers) + `Profile` + the parent's stated worry + the numbers from the modules.

**Output — the structured `StrategicPlan`** the renderer turns into the PDF, including the shown projected card.

**Prompt (paste-ready):**
```
You are the writer for Compass. Turn the finished, validated plan into the family's strategic-plan
document. Everything factual is already decided — your job is to lay it out clearly and completely.

RULES
- Write only what's in the plan. Assert only the numbers you are handed (tiers, probabilities,
  counts) — never compute, round, or add one.
- Ground every profile statement in the intake. Add no fact the plan doesn't contain.
- Cover the fixed sections: profile · priorities · two paths (target/stretch) · the multi-year plan ·
  recommendations (near-term) · college list with tiers · a closing note that answers the parent's
  stated worry, warmly and specifically.
- Build the SHOWN projected card from the real plan (where the kid is headed if they do it).
- Do not redesign the document or invent sections.

Return only the StrategicPlan JSON.

PLAN: {{plan_json}}
PROFILE: {{profile_json}}
STATED WORRY: {{worry}}
NUMBERS (from modules): {{numbers_json}}
```

**Rubric — one Fitness grade.**
1. **Faithful** — every number cited is one it was handed; every profile line traces to the intake; nothing invented.
2. **Complete** — all sections present, including the shown projected card and the college list.
3. **Answers the worry** — the closing note names and answers the parent's actual worry, not boilerplate.
*(How it reads — tone, plainness, no jargon — is judged by the Critic, next.)*

---

## 8 · Communication Critic  *(agent — controls the writing, not the content)*

**Role.** The last pass before the PDF renders. It governs **how** the plan is written and presented — **not what it says.** Tone, honesty, word choice, structure, and the PDF's visuals/layout.

**Input.** The Writer's `StrategicPlan` draft.

**Output.** A verdict: **pass**, or **rewrite** with specific tone/structure/visual fixes (quote the offending line), or **escalate**.

**The standard it enforces:**
- **Neutral, professional, yet friendly** — a parent should feel talked *with*, not sold to or lectured.
- **Simple, plain English** — no jargon, no techy terms a parent wouldn't know, no fancy/British vocabulary that needs a dictionary.
- **Honest, never exaggerated or opinionated** — no hype, no "guaranteed," no over-confident claims; calibrated and human.
- **Clean structure + visuals** — the layout, sections, and PDF UI read clearly.

**Prompt (paste-ready):**
```
You are the communication critic for Compass — the last check before the plan becomes a PDF. You
control HOW the plan is written and presented, never WHAT it says. Do not change the strategy, the
goals, the recommendations, or any number — only the writing and the presentation.

CHECK
- Tone: neutral, professional, and friendly — a parent should feel spoken with, not sold to. Flag any
  hype, exaggeration, or opinionated wording ("guaranteed," "definitely gets in," "amazing kid").
- Plain English: flag jargon, techy terms, or fancy vocabulary a normal parent would need a dictionary
  for. Simpler is better. No British-ism showpieces.
- Honesty: flag anything that overstates the plan or oversells the odds relative to what's written.
- Structure & visuals: flag confusing layout, missing/!clear sections, or presentation that a parent
  would struggle to follow.

For each issue: quote the offending line, say why, and give a fix hint (don't rewrite the content).
Return "pass" only if a real parent would find it clear, warm, honest, and easy. Return "rewrite" with
specific fixes, or "escalate" if the writing problem is systemic.

Return only the verdict JSON.

DRAFT: {{strategic_plan_json}}
```

**Rubric — measured two ways (it's a judge, so test it):**
- **Catch rate** — feed drafts seeded with hype / jargon / exaggeration / a confusing layout → it must flag them.
- **Over-rejection** — feed clean, warm, plain drafts → it must **pass** them. A critic that rejects everything is as broken as one that passes everything.
- **Fix quality** — each flag quotes the line and gives an actionable fix, and never touches the content.

---

## Open items for Nick
1. **Peer-tier definition** — peers are **discovered from the cards** (the other colleges similar admits also landed at), weighted to the intended college + major, rather than a fixed list. Confirm the rule for when the intake names no college (derive from interest/location) and the minimum signal before a college counts as a peer.
2. **College-list volume** — ~10–20 balanced across tiers; confirm the number and the balance (how many reach vs. target vs. likely).
3. **Web-search for unknown interests** — this is the one place we break "catalog-only." Confirmed guard: verify-then-recommend, escalate if unverifiable. OK to Nick?
4. **Constraint Guardrail points** — confirm the checkpoints (as recs are formed + before finalize) are enough, or if he wants a third pass.
5. **Grade scale** — letters (A–F) per step, or 0–100.

---

*Short pipeline, 8 steps. Deterministic where a number is involved (Match & Rank, Constraint Guardrail, Two-paths/tiering); an agent with a paste-ready prompt everywhere judgment lives. Prompts are ready to test against real intake forms and tune.*
