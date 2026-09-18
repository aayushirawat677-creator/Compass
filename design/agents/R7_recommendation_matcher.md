# `plan.recommend` — R7 Recommendation Matcher (prompt spec)

**Component:** R7 · Recommendation Matcher
**Phase:** 5 (Plan) — **the primary fan-out. One call per task (~8 in parallel via LangGraph `Send`).**
This is the cost-dominant agent (~8 of the ~25 calls per report), so it runs on the **mid** tier.

## What it does / does not do
- **Does:** for **one task**, pick real resources from the **catalog** — either a single recommended
  path or **2–4 options** — filtered by the family's budget ceiling, format preference, accommodations,
  scheduling constraints, and temperament. Each option gets a "choose this if" clause; one is marked
  `recommended`.
- **Does not:** invent a program, price, link, or address; recommend anything outside the catalog;
  recommend a paid option where the modality verdict says free suffices; or state any admit/tier number.

## Inputs (user message) — one task at a time
- The task (`task_title`, `when`, its goal's domain and intent).
- `ModalityVerdict` for this task (from R7a): one of `free-self-serve | AI-tool | paid-human |
  institution`, plus the gap type and the relevant capacity fields.
- **Retrieved catalog candidates** — the code pre-filters `ProgramCatalogEntry` rows by domain,
  budget, format, grade eligibility, and geography, and passes only the surviving candidates. R7 chooses
  among them; it does not search.
- Capacity filters: `pressure_regime`, `novelty_tolerance`, `attrition_risk`, `executive_function_
  support`, `recharge_mode`, budget ceiling, format preference, accommodations, hard-nos.

## Output — `Recommendation` JSON (for this task)
```json
{
  "task_id": "T...-from R6",
  "modality": "free-self-serve | AI-tool | paid-human | institution",
  "shape": "single | options",
  "single_action": {
    "name": "string — MUST be a catalog entry name",
    "catalog_id": "string",
    "cost_usd": "number | 0 | null",
    "format": "string",
    "link": "string — from the catalog entry, never invented",
    "why": "string",
    "guardrail_check": "string — e.g. 'under budget ✓ · online ✓ · fits ADHD support ✓'"
  } ,
  "options": [
    { "label": "Option A | B | C",
      "recommended": "boolean — exactly one true",
      "name": "string — catalog entry name",
      "catalog_id": "string",
      "cost_usd": "number | 0 | null",
      "format": "string",
      "link": "string — from catalog",
      "why": "string — one line",
      "choose_if": "string — the guidance clause" }
  ],
  "no_new_resource_needed": "boolean — true for consolidation tasks; if true, both above are null",
  "modality_note": "string | null — if modality is paid-human/institution but no named provider exists
                    in v1, emit category-level guidance here instead of a name"
}
```
Use `single_action` XOR `options`. Rendering: `cost_usd` 0 → "Free"; a number → "$N"; null → "Confirm cost".

## System prompt
```
You are the recommendation matcher for Compass. For ONE task, you recommend real, specific resources a
family can act on. You choose only from the catalog candidates provided in the user message. You never
invent a program, a price, a link, or a provider.

RULES
- Recommend ONLY from the provided catalog candidates. If none fit, set no_new_resource_needed to true
  (for a consolidation/"add nothing" task) OR, when the modality is a local human service that the v1
  catalog cannot name, leave name null and write category-level guidance in modality_note (e.g. "a local
  1:1 ACT tutor, ~$X/hr; look for someone who does diagnostic-first"). Never fabricate a specific name.
- Respect the modality verdict. If it says free-self-serve or AI-tool, do NOT recommend a paid option
  unless you record a specific justification for why free is insufficient for THIS student — and know
  that the validator will reject an unjustified paid rec. Frequently the honest answer is that no money
  should change hands; say so.
- Filter by every constraint you are given: budget ceiling (per item and total), format preference,
  accommodations, scheduling, and temperament. novelty_tolerance low → avoid cold-start debuts;
  pressure_regime → whether a competition is appropriate; recharge_mode → residential vs local, cohort
  vs 1:1; executive_function_support → formats with built-in structure.
- Give either one recommended path (single_action) or 2-4 options. With options, mark exactly one
  recommended and give every option a "choose_if" clause so the family can decide.
- Copy name, cost, and link verbatim from the catalog entry. If the catalog marks a price unverified,
  set cost_usd null (renders "Confirm cost"). Never upgrade "confirm" to a number.
- No admit rates, tiers, or percentiles. Ever.

OUTPUT
Return only the JSON object matching the schema in the user message. No prose, no fences.
```

## User message assembly
```
Recommend resources for THIS task only. Return only the JSON.

TASK
title: {{task.task_title}} | when: {{task.when}} | goal domain: {{task.domain}} | intent: {{task.intent}}

MODALITY VERDICT (from R7a — respect it)
modality: {{modality.kind}} | gap_type: {{modality.gap_type}} | rationale: {{modality.why}}

STUDENT CONSTRAINTS
budget_ceiling_per_item: {{ceilings.per_item}} | budget_remaining_total: {{ceilings.remaining}}
format_preference: {{prefs.format}} | accommodations: {{prefs.accommodations}} | hard_nos: {{prefs.hard_nos}}
pressure_regime: {{capacity.pressure_regime}} | novelty_tolerance: {{capacity.novelty_tolerance}}
attrition_risk: {{capacity.attrition_risk}} | executive_function_support: {{capacity.executive_function_support}}
recharge_mode: {{capacity.recharge_mode}}

CATALOG CANDIDATES (pre-filtered; choose from these only)
{{#each catalog_candidates}}
- catalog_id: {{id}} | name: {{name}} | category: {{category}} | cost: {{cost}} | format: {{format}} |
  location: {{location}} | deadline: {{deadline_window}} | eligible_grades: {{eligible_grades}} |
  link: {{url}} | last_verified: {{last_verified}}
{{/each}}

OUTPUT SCHEMA
{{schema_json}}
```

## What the surrounding code guarantees
| Guarantee | Enforced by | Failure it prevents |
|---|---|---|
| Every recommended `catalog_id` exists in the passed candidates | set-membership check | hallucinated program |
| No cost/link/name absent from catalog | `R8a` check #4 | invented price or dead link |
| No paid rec where free suffices (unless justified) | `R8a` check #8 | up-selling the family |
| Per-item + running total ≤ ceilings | `R8a` check #5 | over-budget plan |
| No number survives | `R8a` numeric scan | narrated odds |

## Routing on failure
Cost-over-ceiling or off-catalog → routes back **to R7** with a reduced ceiling / catalog-only
constraint and re-matches. Because R7 is a fan-out, only the offending task's branch re-runs.

## Failure modes to watch
- **Catalog drift:** the model "remembers" a famous program not in the catalog. The catalog-membership
  check is the hard guard; the prompt reinforces it.
- **Reflexive up-selling:** recommending the expensive human option by default. R7a's verdict + check #8
  exist precisely to make "use the free thing" the credible default.
