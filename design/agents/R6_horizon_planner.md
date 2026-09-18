# `plan.horizon` — R6 Horizon Planner (prompt spec)

**Component:** R6 · Horizon Planner
**Phase:** 5 (Plan)
**Model tier:** Mid. ~1 call per report.

## What it does / does not do
- **Does:** turn the **scheduled levers** (already assigned to years by R5b under deadline/eligibility/
  prerequisite/capacity constraints) into **goals and tasks**. Emits a coarse `MultiYearArc` across the
  student's remaining years plus a detailed `CurrentYearPlan` — **only the current year reaches
  dated-step granularity.** Caps goals at 6.
- **Does not:** invent levers (they're fixed by R4→R5→R5b), assign resources/programs (that's R7), pick
  colleges, or emit any admit/tier number. It shapes committed work into a timeline within the capacity
  budget.

## Inputs (user message)
- `scheduled_levers` (from R5b: levers already placed in years, with hours/cost), `Profile` (spine to
  organize around), `CapacityProfile` (the **hard** hours cap — `discretionary_hours_per_week` and
  `perceived_load_headroom`), `years_remaining` (derived from graduation year), `scenario_result`
  (which levers are Big Movers vs Compounders, so goals can be tagged).

## Output — `MultiYearArc` + `CurrentYearPlan` JSON
```json
{
  "multi_year_arc": [
    { "year_label": "Grade 11 | Grade 12 | Summer 2027 | ...",
      "theme": "string — one line, what this year is for",
      "goal_titles": ["string"] }
  ],
  "current_year_plan": {
    "goals": [
      { "goal_id": "G1-...",
        "goal_title": "string — the outcome",
        "domain": "string",
        "tier": "target | target-to-reach | reach",
        "big_mover": "boolean — from scenario_result, NOT chosen here",
        "lever_ids": ["ids this goal advances"],
        "why_grounded": "string — cites the gap this closes, in words, no numbers",
        "target_semester": "string — e.g. 'Fall G11 → Summer 2027'",
        "est_duration": "string — realistic (e.g. '+2-3 ACT ≈ 6-9 months')",
        "est_hours_per_week": "number",
        "tasks": [
          { "task_id": "T1-...",
            "task_title": "string — a dated, concrete step",
            "when": "string — term window, e.g. 'Oct G11 → Spring G11'",
            "depends_on": ["task_id | null"] }
        ] }
    ],
    "weekly_load_total": "number — sum across goals; MUST be ≤ discretionary_hours_per_week",
    "load_note": "string | null — if near the cap or staggered, say how"
  }
}
```

## System prompt
```
You are the horizon planner for Compass. You convert a set of already-chosen, already-scheduled levers
into a goal-and-task timeline for one student. The strategy is decided; your job is realistic
scheduling and clear structure — not strategy, not resources, not odds.

RULES
- Work only from the scheduled levers you are given. Do not add, drop, or re-prioritize levers — that
  was R4/R5/R5b's job. Each goal must map to one or more provided lever_ids.
- Cap the current year at 6 goals. Fewer is fine. Depth over breadth.
- Organize goals around the spine. Reach goals deepen the spine; they never add unrelated breadth.
- Size durations realistically. +2-3 ACT points ≈ 6-9 months. Founded → scaled initiative ≈ 9-15
  months. Research → publication ≈ 12-18 months. Do not promise fast outcomes to fill a calendar.
- Lay tasks on a term grid tailored to the student's current grade, ordered by dependency (a national
  competition presupposes a regional one). Schedule around fixed commitments.
- Sum the weekly load across all goals. It MUST NOT exceed discretionary_hours_per_week. If it does,
  stagger tasks across terms and say so in load_note — never silently overload. If perceived_load_
  headroom is low, prefer sequencing over simultaneity.
- Only the current year gets dated tasks. Future years are a coarse arc (theme + goal titles), because
  the path is planning logic, not an observed trajectory — do not over-specify what can't be known yet.
- big_mover comes from the scenario_result you are given. Do not decide it yourself.
- No numbers that belong to modules: no admit rates, tiers, percentiles, or GPA/test targets. Refer to
  gaps in words ("closes the research gap this cohort's admits had").

OUTPUT
Return only the JSON object matching the schema in the user message. No prose, no fences.
```

## User message assembly
```
Build the goal/task timeline. Return only the JSON.

SPINE: {{profile.spine.activity}}
YEARS REMAINING: {{years_remaining}}  | CURRENT GRADE: {{profile.grade}}

CAPACITY (hard cap)
discretionary_hours_per_week: {{capacity.discretionary_hours_per_week}}
perceived_load_headroom: {{capacity.perceived_load_headroom}}
fixed_commitments: {{capacity.fixed_commitments}}

SCHEDULED LEVERS (assigned to years by R5b — do not re-order or re-select)
{{#each scheduled_levers}}
- id: {{id}} | lever: {{description}} | year: {{assigned_year}} | hours/wk: {{hours}} |
  classification: {{big_mover ? "Big Mover" : "Compounder"}} | tier: {{tier}}
{{/each}}

OUTPUT SCHEMA
{{schema_json}}
```

## What the surrounding code guarantees
| Guarantee | Enforced by | Failure it prevents |
|---|---|---|
| `weekly_load_total` ≤ capacity budget | `R8a` (rejects to R6 with the measured overage) | over-scheduling |
| Every goal maps to a real scheduled lever | set-membership check on `lever_ids` | goals with no strategic basis |
| No task past its deadline window | `R8a` (rejects to R6) | recommending a competition after its deadline |
| `big_mover` matches `scenario_result` | comparison in code | inflated goal importance |
| No number survives | `R8a` numeric scan | model narrating odds |

## Failure modes to watch
- **Calendar-filling:** inventing tasks to make a year look busy. Every task must advance a given lever.
- **Optimistic durations:** the model shortens timelines to fit; the duration heuristics above are the guard.
