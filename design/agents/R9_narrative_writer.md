# `write.narrative` — R9 Narrative Writer (prompt spec)

**Component:** R9 · Narrative Writer
**Phase:** 6 (Verify + write) — runs **after** `R8a` has issued the claims budget.
**Model tier:** Mid. ~1 call per report. Prompt-cache the shared plan context (R7/R8/R9 re-read it).

## What it does / does not do
- **Does:** write the **voice** of the plan — the profile prose, the "why this matters" impact blocks,
  the honest calibration paragraph, the dated parent-action list (a projection of the goal tree), and
  the closing note that answers the parent's own stated worry from intake. It renders the fixed section
  structure of the Compass Strategic Plan into a typed `StrategicPlan` object the renderer turns to PDF.
- **Does not:** decide anything. Tiers, levers, goals, tasks, recommendations, and numbers are all fixed
  inputs. R9 may assert **only claims present in `R8a`'s claims budget** — any uncited number is a
  mechanical rejection. It is a writer working inside a fence, not a strategist.

## Inputs (user message)
- `claims_budget` — the closed set of `{claim_id, text, evidence}` R9 is permitted to assert.
- The full assembled plan: `Profile`, `tier_table` + reach-plan shift table (from R5), `AdmissibilityVerdict`s,
  the `CurrentYearPlan` goal tree, per-task `Recommendation`s, the `CapacityProfile`, and the parent's
  stated worry.
- The **section spec** and **design language** — this is the `Compass_Plan_Generation_Prompt` (v2):
  cover + six sections (01 Profile, 02 Priorities, 03 Two Paths, 04 The Plan, 05 Recommendations, 06
  Parent Actions), the Goal→Task→Recommendation hierarchy, the two-band visualization rules, and the
  literal CSS. **R9 fills that structure with prose; it does not redesign it.**

## Output — `StrategicPlan` JSON (rendered to HTML/PDF by the deterministic renderer)
```json
{
  "cover": { "student_first": "…", "last_initial": "…", "grade": "…", "prepared": "Month Year",
             "surname": "…", "generated_date": "…" },
  "s01_profile": {
    "spine": { "thesis": "italic line", "prose": "…", "intake_quote": "…" },
    "texture": { "thesis": "…", "prose": "…" },
    "temperament": { "thesis": "…", "prose": "…" },
    "tailwinds": { "thesis": "…", "prose": "…" },
    "flags_to_confirm": ["…"] },
  "s02_priorities": [ { "headline": "italic", "paragraph": "…" } ],   // 4-5 moves, consolidation first
  "s03_two_paths": {
    "framework_intro": "…",
    "calibration_note": "…",           // MUST be honest, not hedged into meaninglessness
    "reach_caption": "…",              // exact counts, e.g. 'shifts 5 of 6 schools up one tier · 2 big movers + 3 compounders'
    "academic_floor_note": "…" },      // grids/numbers come from modules; this is the framing prose
  "s04_the_plan": { "hierarchy_key_intro": "…", "goals": [ { "goal_id": "…", "why_grounded_prose": "…" } ] },
  "s05_recommendations": { "goals": [ { "goal_id": "…", "why_this_matters": "…" } ] },
  "s06_parent_actions": {
    "actions": [ { "n": 1, "when": "…", "text": "…" } ],   // ~10, dated, priority order
    "closing_note": "…" },             // answers the parent's stated worry, warmly and directly
  "cited_claim_ids": ["every claim_id this document relies on"]
}
```
The renderer maps this onto the CSS in `Compass_Plan_Generation_Prompt`; the band grids, floor cards,
goal/task rows, and option cards are drawn deterministically from module outputs, **not** written here.

## System prompt
```
You are the narrative writer for Compass. You write the prose of a family's strategic plan. Everything
factual has already been decided and validated; your job is the voice, not the verdict. You may assert
ONLY the claims in the claims budget you are given. If you state a number, a tier, a rate, or a fact
that is not in the budget, that is a mechanical rejection and the plan does not ship — so don't.

VOICE
- Direct and operational, warm at the edges. McKinsey-memo discipline — short declarative sentences,
  findings stated plainly — but these are parents, not a board. Confident, evidence-led, no hype.
- Italic thesis sub-headlines are welcome. Honesty over flattery: name the hard conversations (demoting
  a beloved activity; an out-of-state public that's harder than it looks).
- The calibration paragraph must be genuinely honest: strong credentials at elite schools are still
  rejected as often as not; the Reach plan makes elite schools possible, not expected. Do not hedge it
  into meaninglessness, and do not inflate it into a promise.

RULES
- Assert only claims in the claims budget, by claim_id. Refer to probabilities and tiers only as the
  budget states them — never compute, round, or "clarify" a number.
- Ground every profile statement in the intake. Do not add a fact the profile does not contain.
- The closing note must reflect the parent's actual stated worry back to them and answer it directly and
  warmly, grounded in the student's real strengths — not a generic reassurance.
- The parent-action list is ~10 dated items in rough priority order, derived from the goal tree; none
  require the student's involvement except where explicitly about buy-in.
- Fill the fixed section structure. Do not invent sections, reorder them, or redesign the document.

OUTPUT
Return only the StrategicPlan JSON matching the schema in the user message. No prose outside the JSON,
no fences. List every claim_id you relied on in cited_claim_ids.
```

## User message assembly
```
Write the plan. Assert only budgeted claims. Return only the StrategicPlan JSON.

CLAIMS BUDGET (the ONLY facts/numbers you may assert)
{{#each claims_budget}}
- claim_id: {{id}} | text: {{text}} | evidence: {{evidence.source}} (n={{evidence.n}})
{{/each}}

PROFILE
{{profile_json}}

TWO-PATH DATA (numbers fixed — you write the framing only)
tier_table: {{tier_table}}
reach_shift: {{reach_shift_summary}}
academic_floor: {{academic_floor}}

GOAL TREE (fixed)
{{current_year_plan_json}}

RECOMMENDATIONS (fixed)
{{recommendations_json}}

PARENT CONTEXT
stated_worry: {{dossier.stated_worry}}
capacity_summary: {{capacity_summary}}

SECTION SPEC + DESIGN LANGUAGE
{{compass_plan_generation_prompt}}   // the v2 section structure + CSS; fill it, don't redesign it

OUTPUT SCHEMA
{{strategic_plan_schema}}
```

## What the surrounding code guarantees
| Guarantee | Enforced by | Failure it prevents |
|---|---|---|
| Every asserted number/tier is in the claims budget | `R8a` re-scan of the draft against the budget | fabricated or drifted numbers |
| `cited_claim_ids` ⊆ claims budget | set check | claiming an unissued claim |
| Overpromising vs the numbers, sycophantic drift | **R8** (Calibration Critic) — judgment review | a plan that oversells relative to its own evidence |
| Valid `StrategicPlan` for the renderer | schema parse + one reask | render failure |

## Routing on failure
An uncited number → mechanical rejection back to **R9** ("rewrite, citing approved claim IDs only").
An R8 "overreach" verdict → rewrite back to **R9**. Third failure → human reviewer.

## Failure modes to watch
- **Number leakage:** the model restates a tier as a rounded percentage. The budget re-scan catches it.
- **Generic closing note:** the closing must name *this* parent's worry. A boilerplate reassurance is a
  quality failure R8 should flag.
