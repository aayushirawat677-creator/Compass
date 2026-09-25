# Compass Deterministic Modules — v1 spec

**These are code, not agents.** They need unit tests, not prompt engineering. They exist because of the
governing rule: *every number in the final document is produced by a module, never by an agent.* Build
these (and their tests) **before** the agents — they're where correctness lives, and `R8a` in
particular is the safety net the whole system leans on.

Each module below lists: **purpose · inputs · outputs · algorithm · tests**.

---

## Offline data plane (batch; amortized across all students)

### D1 · Outcome Harvester
- **Purpose:** incremental pulls of new r/collegeresults posts.
- **Inputs:** Reddit (r/collegeresults). **Outputs:** raw `post_body` + metadata → feeds D2.
- **Algorithm:** extend existing `fetch_posts.py`; dedupe by `post_id`; store `posted_at`, `author_hash`.
- **Cadence:** weekly; daily during Mar–Apr decision season.
- **Tests:** dedupe correctness; incremental watermark advances; no post dropped across a run boundary.

### D3 · Institution Profiler (pure ETL)
- **Purpose:** build the Institution Store from IPEDS.
- **Inputs:** `~/nmeena/ipeds-explorer/data/ipeds.sqlite` — `ADM2024` (applicants/admits, SAT/ACT 25/50/75
  percentiles, `ADMCON1-12` stated factors), `SFA2324` + `COST1_2024` (aid), `C2024_A` (program size).
  Later joined with Common Data Set.
- **Outputs:** `Institution` records keyed by **`UNITID`** → feeds R2, R3, R3b.
- **Algorithm:** straight ETL + typed load; carry every field's source column for `Evidence`.
- **Cadence:** annual (IPEDS/CDS release). **Tests:** row counts vs source; percentile monotonicity; no null `UNITID`.

### D6 · Lever Lift Estimator (statistics)
- **Purpose:** mine the corpus for what actually separates admits from denies, **conditioned on cohort**.
  Produces the empirical basis for calling a lever a Big Mover instead of asserting it. Emits the
  `candidate_levers[]` R4 selects from.
- **Inputs:** Applicant Outcome Corpus (from D2) + Institution Store. **Outputs:** Lever Lift Tables → R4, R5.
- **Algorithm:** for a cohort slice (e.g. 3.8+/34+ social-science applicants to a school), compute admit
  share with vs without each lever (national award, published research, …). Impose **minimum cell sizes**;
  attach `n`, the query, and a confidence flag to every lift. **Lifts are associational, not causal** —
  label them cohort patterns.
- **Cadence:** after each D2 batch; full refit annually.
- **Tests:** cell-size floor enforced; lift reproducible from a frozen corpus snapshot; thin-n levers
  flagged, not dropped silently.

### D7 · Entity Resolver (fuzzy match + one-shot LLM assist)
- **Purpose:** maintain a **static alias map from free-text college names to canonical IPEDS `UNITID`.**
  **This join key is load-bearing** — without an explicit alias map over the 721 names in
  `Merged/verify/canonical_colleges.txt`, the Reddit and IPEDS datasets silently fail to join and colleges
  show n=0.
- **Inputs:** unseen `college_raw` strings from D2. **Outputs:** alias-map writes → Institution Store + Corpus.
- **Algorithm:** fuzzy match (token-set ratio) against known names → auto-map above a threshold; below it,
  one cheap LLM call to resolve a genuinely new name, then **write the result to the map** so it's never
  re-inferred. Human-review the LLM-assisted mappings periodically.
- **Cadence:** on demand. **Tests:** every name in `canonical_colleges.txt` resolves; ambiguous names
  (e.g. "Miami") route to review; no silent n=0 for a name present in both datasets.

> **Catalog note (v1):** D4 (Program Catalog Builder) and D5 (Catalog Verifier) are **deferred**. In v1
> the Program Catalog is a **hand-seeded CSV (~150 programs)** with the `ProgramCatalogEntry` schema
> (name, category, domain tags, cost, format, location, deadline window, selectivity, eligible grades,
> URL, last_verified, confidence). R7 reads from it directly. Automate D4/D5 in v1.x.

---

## Runtime modules (per student)

### R1b · Capacity & Temperament Modeler
- **Purpose:** convert the intake's behavioral answers into a `CapacityProfile` of **hard constraints**,
  not prose. *(Adds no agent — it can borrow R1's single call to parse three open-text answers, or run as
  pure scoring if the form is fully structured.)*
- **Inputs:** intake behavioral answers. **Outputs:** `CapacityProfile` (the 9 fields in
  `ARCHITECTURE.md` §4.2). **Consumers:** gates R6, filters R7, feeds R7a, supplies R8a's feasibility checks.
- **Algorithm:** deterministic scoring rules mapping each answer to a field (e.g.
  `discretionary_hours_per_week = stated_hours − fixed_commitments`, normalized to a grade homework norm).
- **Tests:** each field derivable from a fixed answer set; `perceived_load_headroom` low when quit-intent
  high; `autonomy_ratio` low when activities are parent-driven.

### R2 · Neighbor Matcher (retrieval)
- **Purpose:** find the k most similar `ApplicantOutcome` records and return the cohort + their per-college
  outcomes. This cohort is the **evidence substrate for everything downstream.**
- **Inputs:** `Profile` (as a de-identified feature vector) + Applicant Outcome Corpus. **Outputs:** `Cohort`.
- **Feature vector:** UW & W GPA, test composite + section split, rigor relative to school offerings,
  school type, major category, hook flags, activity-strength summary, state/region. Numeric standardized,
  categorical one-hot.
- **Distance:** **weighted Gower distance**; weights initialized from NACAC factor importances, then
  **tuned against held-out calibration, not taste.**
- **k:** **adaptive** — expand the radius until a minimum cohort size is met; **record the radius**. A
  cohort that needed a wide radius is weak and **must be labelled as such** in its `Evidence` record.
- **Missing fields:** match on the observed subspace, record the omission — **never impute silently.**
  Runs on the de-identified vector.
- **Tests:** identical input → identical cohort; wide-radius cohorts flagged; missing-field handling never
  imputes; weight vector loads from the tuned config, not a literal.

### R3 · Tiering Engine
- **Purpose:** assign the four bands — **Far Reach <15% · Reach 15–35% · Target 35–60% · Likely 60%+.**
- **Inputs:** `Cohort` (R2) + Institution Store. **Outputs:** `tier_table` (band + posterior interval + n
  per school).
- **Algorithm — the thin-tail fix:** of 842 colleges, 499 have n≤4 and only 71 have n≥100, so a raw cohort
  rate is noise for most schools. Use **empirical-Bayes partial pooling**: a Beta-Binomial posterior per
  college, with the **IPEDS published rate as the prior** and the **cohort-conditional count as the
  likelihood.** Every tier claim carries **its posterior interval and its n.**
- **Self-selection is signal, not noise:** Duke 26% in-corpus vs ~6% published — do **not** correct this
  to the published rate. Bands are **profile-conditional**: "reflects this student's profile given the work
  each plan describes — not published acceptance rates."
- **Tests:** thin-n school → wide interval → not assertable (R8a rejects); posterior collapses to cohort
  rate as n grows; prior dominates at n=0; reproducible from a frozen snapshot.

### R3b · Admissibility Screen
- **Purpose:** the product's most consequential stage, and it is **pure arithmetic.** Takes the family's
  declared college list and returns a verdict per school **before any planning happens.**
- **Inputs:** `DeclaredCollegeList` + `Cohort` (R2) + IPEDS `ADM2024` percentiles (covers 1,956 colleges).
  **Outputs:** `AdmissibilityVerdict` per school + a proposed **balanced list.**
- **Three verdicts:**
  - **Evidence-supported** → tier + n + interval.
  - **Outside observed range** → a measured gap statement (how far the student is from the observed band).
  - **No evidence** → a gap statement and a **reframed list — never a percentage.** (A 2.0 applicant to
    MIT gets no invented probability. This is absolute.)
- **Balanced list:** deterministic IPEDS filtering against family preferences (geography, size, major, net
  price vs `SFA2324` income band).
- **Tests:** no-evidence school never gets a number; outside-range gap is measured, not guessed; balanced
  list respects every stated preference.

### R5 · Scenario Simulator
- **Purpose:** the **mathematical core.** Re-run R3 under hypothetical lever completion to produce **Target
  Plan vs Reach Plan** and the tier-shift table ("shifts 5 of 6 schools up one tier").
- **Inputs:** selected `Lever`s (R4) + Lift Tables (D6). **Outputs:** `scenario_result` — **Big Mover vs
  Compounder classification** + reach-plan tier table.
- **Algorithm:** apply each lever's measured lift to the cohort-conditional likelihood, re-run the
  Beta-Binomial, recompute bands. **Big Mover vs Compounder is an output of measured tier movement, not a
  label an LLM chooses.** A lever that moves ≥1 school up a tier is a Big Mover; one that only tightens the
  interval is a Compounder. (This is the Empowerly-Score scenario mechanic.)
- **Tests:** movement matches recomputed bands exactly; an unsupported (off-menu) lever produces **no**
  movement; classification is deterministic from the numbers.

### R5b · Trajectory Scheduler
- **Purpose:** assign selected levers to specific years. **Planning logic, not an observed trajectory.**
- **Inputs:** classified levers (R5) + Program Catalog (deadlines) + `CapacityProfile`. **Outputs:**
  `scheduled_levers` (levers → years).
- **Algorithm:** **topological ordering** under four constraints: catalog deadline windows, grade
  eligibility, prerequisites (a national competition presupposes a regional one), and the **per-year
  capacity budget from R1b.**
- **Tests:** no lever scheduled past its deadline; prereqs precede dependents; per-year hours ≤ budget;
  infeasible sets surface a typed error rather than silently overload.

### R7a · Modality Selector
- **Purpose:** decide **what kind of help** each task needs — free self-serve / AI tool / paid human /
  institution — **before any provider is named.** Frequently the honest answer is that no money should
  change hands.
- **Inputs:** goal tree (R6) + `CapacityProfile` (specifically `autonomy_ratio`,
  `executive_function_support`, gap type). **Outputs:** `ModalityVerdict` per task → R7, R8a.
- **Algorithm:** deterministic gap-type → help mapping. Content gap → free/AI; Structure gap → paid human;
  Diagnosis gap → paid human; Signal gap → human or institution. The discriminators are already computed,
  so this is a rule, not a judgment.
- **Tests:** a content gap never maps to paid human; low executive-function-support biases toward
  structured formats; mapping is a pure function of inputs.

### R8a · Constraint Validator  ← **build this first**
- **Purpose:** the deterministic **veto.** Enforces every guarantee code can decide; **catch rate 100% by
  construction.** Its key move: it issues the **claims budget** — the closed set of claim IDs R9 may assert,
  each bound to its `Evidence` — **before** R9 runs. Issuing permitted claims before generation makes
  fabrication structurally unavailable.
- **Inputs:** the full `PlanState`. **Outputs:** on pass → `claims_budget` → R9; on fail → a **typed
  rejection edge** to R3/R4/R6/R7/R9 carrying an executable constraint change (see `ARCHITECTURE.md` §5).
- **The nine checks:** (1) every number traces to an `Evidence` record; (2) no tier claim on insufficient
  n / too-wide interval; (3) **no tier percentage on a no-evidence school**; (4) no program/price/URL
  absent from the catalog; (5) total cost ≤ family ceiling AND per-year cost ≤ annual ceiling; (6) total
  weekly hours ≤ `CapacityProfile` budget; (7) no task past its deadline window; (8) no paid recommendation
  where R7a says free suffices (absent recorded justification); (9) no tier improvement exceeding what R5
  computed.
- **Rejection carries a fix:** each rejection is an *executable constraint change*, not a complaint (e.g.
  "cost exceeds ceiling by $600 → re-match within $X"). Iteration counter in `PlanState`, **cap 3**, then
  escalate.
- **Tests:** THE **injection set** is R8a's test suite — inflated tiers, invented programs, over-budget
  recs, hour-total violations, thin-n tier claims, no-evidence percentages, deadline violations, unjustified
  paid recs, tier movement beyond R5. Each must be caught 100% of the time. Also test that each rejection
  routes to the correct stage with a valid constraint change.

### Renderer (M2)
- **Purpose:** produce the HTML/PDF from the final typed `StrategicPlan`. **No model involved** — so layout
  bugs are never content bugs.
- **Inputs:** `StrategicPlan` (from R9) + module outputs (tier grids, floor cards, goal/task rows, option
  cards drawn from R3/R5/R6/R7, not written by R9). **Outputs:** the PDF.
- **Algorithm:** WeasyPrint over the section structure + literal CSS in `Compass_Plan_Generation_Prompt`
  (cover + six sections; the two-band visualization rules; Playfair Display / Inter, navy/gold). Rasterize
  every page (pdf2image, ~100–110 dpi) and visually inspect until nothing overflows or splits. ~12–14 pages.
- **Tests:** golden-file render of a fixed `StrategicPlan`; band-grid shift rules (up exactly one tier,
  Likely-under-Target stays put, arrows only on shifted chips); no page overflow; `<` HTML-escaped; en-dash
  in ranges.

---

## Build order (modules)
1. **R8a + its injection set** (the safety net) and the `Evidence`/`claims_budget` plumbing.
2. **D3, D7, D2-output load** → Institution Store + alias map + corpus (the join must work: no silent n=0).
3. **D6** lift tables.
4. **R2 → R3 → R3b** (the position core) with the calibration eval alongside.
5. **R5 → R5b** (scenario + schedule).
6. **R1b, R7a** (capacity + modality).
7. **Renderer** last (it's deterministic and swappable; you already have the CSS).
