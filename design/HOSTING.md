# Compass Strategy Engine — Hosting (managed cloud, fast to prod)

You chose **managed cloud**. This is the right call for a small team: the checkpointer, task queue,
retries, and fan-out concurrency come for free, so you spend your engineering on the deterministic core
and the corpus — not on infrastructure plumbing.

> **Two things to verify at build time** (both change and I won't hardcode stale values): (1) the exact
> Claude model IDs and their current per-token prices — these set your ~$2/report figure; (2) LangGraph
> Platform's current plan tiers and quotas. Everything else below is stable architecture.

---

## 1. Runtime: LangGraph Platform

The graph in `orchestration/` maps onto LangGraph almost one-to-one, and Platform gives you the pieces
this design specifically needs:

- **Managed Postgres checkpointer + long-term store.** This is *the* load-bearing reason to use
  LangGraph. Phase 1 (intake) waits **days to weeks** on the family. `nodes.collect` calls `interrupt()`;
  the run durably suspends and resumes when the web form posts the dossier back. Do not try to hold this
  in memory or a job that times out — the whole point is a run that survives a two-week gap.
- **`Send` API fan-out.** R7's ~8 per-task branches run concurrently; the Platform manages the
  concurrency and merges results through the `recommendations` reducer.
- **Typed retry cycles.** The validation gate's `add_conditional_edges` loops (max 3, then escalate) run
  as ordinary graph execution — no custom queue.
- **Human-in-the-loop.** Both `interrupt()` points (Phase 1 intake, and `human_escalation`) surface as
  Platform interrupts your reviewer UI resumes.

**Deploy:** point the Platform at `orchestration/langgraph.json` (graph id `compass`). It provisions the
checkpointer/store; `graph = build().compile()` compiles bare (no explicit checkpointer) — Platform
injects it. For **local dev**, run `langgraph dev`, or compile with `PostgresSaver.from_conn_string(...)`
as shown in `graph.py`.

**Managed services you attach:**
| Need | Managed choice | Why |
|---|---|---|
| Checkpointer + store | LangGraph Platform's Postgres | durable suspend/resume across the Phase-1 wait |
| Corpus + Institution Store + Lift Tables + Catalog | a managed Postgres (or keep IPEDS SQLite + Postgres for corpus) | modules query these read-only at runtime |
| Object storage for rendered PDFs | S3 / GCS bucket | the renderer writes here; delivery links point at it |
| Web form (intake) | your existing Lovable app | posts `StudentDossier` to the Platform run's resume endpoint |

The **offline data plane (D1/D2/D3/D6/D7)** deliberately does **not** run in LangGraph — it's scheduled
batch. Keep your existing `split.py → subagents → merge.py` pattern on plain job scheduling (cron / a
managed scheduler). It writes to the same Postgres the runtime modules read.

---

## 2. Models & tiers

Three tiers, mapped in `orchestration/nodes.py` (`TIER`). Fill the exact IDs after verifying current
model names/prices:

| Tier | Agents | Guidance |
|---|---|---|
| **top** | R1, R4, R8 | strongest Claude model — the hardest judgment (spine, lever selection, calibration). ~3–4 calls/report. |
| **mid** | R6, R7, R9 | mid Claude model — planning, matching, writing. R7 fan-out is ~8 of these. |
| **cheap** | D2 (offline) | cheapest model — highest volume (2,617 posts + incrementals). |

Requirements baked into the design:
- **Zero-retention endpoints + no-training agreements are prerequisites** (student data). Record the
  model ID per stage in `ReportProvenance`.
- **Prompt caching** on the shared plan context — R7/R8/R9 re-read the same draft/plan; cache the system
  blocks and the shared context across retries.
- **Model upgrades are gated:** a new model version ships only after the calibration eval **and** the R8
  injection set both pass (see `evals/EVALS.md`). Never hot-swap a model in prod without re-running the gate.

---

## 3. Secrets / env (`.env`, referenced by `langgraph.json`)

```
ANTHROPIC_API_KEY=...            # zero-retention endpoint
DATABASE_URL=...                 # corpus / institution store / lift tables / catalog (read-only at runtime)
LANGGRAPH_CHECKPOINT_DB=...      # provisioned by Platform; local dev only
PDF_BUCKET=...                   # S3/GCS for rendered plans
MODEL_TOP=...                    # verified model id
MODEL_MID=...
MODEL_CHEAP=...
COMPASS_CORPUS_SNAPSHOT=...      # pinned into ReportProvenance for reproducibility
COMPASS_LIFT_VERSION=...
COMPASS_CATALOG_VERSION=...
```

Student PII lives only in the dossier and the checkpointer. R2 runs on a **de-identified feature
vector** — keep it that way; the corpus join never needs the student's name.

---

## 4. Cost model (re-verify prices before quoting anyone)

Per the architecture doc, at the model prices it assumed:

| Item | Figure | Note |
|---|---|---|
| Model spend / report | **~$2** (~$5 with slop) | ~25 calls; only 3–4 top-tier; R7 ≈ 8 mid calls |
| Data plane stand-up | **< $100** one-time | |
| Data plane upkeep | **< $50 / quarter** | |
| D2 backfill (2,617 posts) | **$15–30** cheap tier (~$85 mid) | one-time + incrementals |
| Latency | Phases 2–6 in **3–4 min** | Phase 1 dominates elapsed time (human wait) |

Why it's this cheap: **every number is a module, not an agent**, so the LLM only ever sees a
few-thousand-token *summary* of the cohort, never the corpus. The real costs are the CDS scraping work
and human review time, not inference. **`Escalation volume, not token spend, is the number to drive
down.`**

---

## 5. Rollout

1. **Data plane** stood up (corpus loaded via D2, Institution Store, alias map, lift tables, hand-seeded
   catalog). Verify the join: **no college that exists in both datasets shows n=0** (that's a D7 alias-map
   miss).
2. **Deterministic core + R8a + eval gate** deployed and green (`evals/EVALS.md`).
3. **Agents** wired (`nodes.py` IMPL points filled), graph deployed to Platform.
4. **Shadow mode:** run the graph on the plans you already made by hand (Neerav, Rob) and diff — the
   numbers should be reproducible; the prose will differ. Fix discrepancies before any real family.
5. **Human-review every plan** (service model: plan + review call + response commitment) until R8a/R8
   show measured catch rates; then review becomes exception-only.
6. **Re-planning is cheap and defined** (see the invalidation rules): new score → R2 onward (~$2); new
   award → R4 onward (<$1); catalog refresh → R7/R8a/R9 (cents). Provenance makes "re-run this plan" a
   real operation.

---

## 6. Alternative if managed ever chafes

If you later want off LangGraph Platform: the same graph runs self-hosted (LangGraph on your own
container host + your own Postgres for the checkpointer) with no code change — only the deploy target and
`graph.py`'s compile line change. That's your escape hatch; you don't need it for v1.
