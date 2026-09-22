"""
Compass Engine — configuration.

Two things you set here:
  1. Where your data lives (DATA_DIR + the file names / column maps below).
  2. How the agents call Claude (LLM_MODE + the model + the API key env var).

Nothing else in the codebase hardcodes a path or a column name — it all reads from here.
"""
import os

# ---------------------------------------------------------------------------
# 1. CLAUDE ACCESS  (the agent steps call this)
# ---------------------------------------------------------------------------
# LLM_MODE:
#   "mock"  -> no API calls; every agent returns canned, correctly-shaped JSON.
#              Use this to see the whole pipeline run and produce a PDF with zero setup.
#   "real"  -> calls the Anthropic API using the key in ANTHROPIC_API_KEY.
#              This is where "Peggy's Claude access" goes: put Peggy's Anthropic
#              API key in the env var below and the whole system runs on it.
LLM_MODE = os.environ.get("COMPASS_LLM_MODE", "mock")

ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"   # export ANTHROPIC_API_KEY=... (Peggy's key)

# model tiers — swap for whatever Peggy's access exposes
MODEL_TOP = os.environ.get("COMPASS_MODEL_TOP", "claude-opus-4-20250514")     # profile, gap, strategy, critic
MODEL_MID = os.environ.get("COMPASS_MODEL_MID", "claude-sonnet-4-20250514")   # projected, plan, writer

MAX_TOKENS = 4096
TEMPERATURE = 0.2          # low — we want reproducible-ish structure
# Live research depth. The program registry only really covers debate, so every
# other activity is researched live — that is the mechanism, not a fallback. Set
# generously: a verified, bookable option is worth far more than a saved call. [#45]
RESEARCH_MAX_SEARCHES = int(os.environ.get("COMPASS_RESEARCH_SEARCHES", "8"))

MAX_JSON_RETRIES = 2       # reask once if the model returns invalid JSON

# ---------------------------------------------------------------------------
# 2. DATA  (the deterministic steps read this)
# ---------------------------------------------------------------------------
# Point DATA_DIR at the folder that holds your CSVs + ipeds.sqlite.
# On your Mac that is the "Peggy" folder; in this cloud test it stays empty and
# the retrieval step falls back to mock cards so the pipeline still runs.
DATA_DIR = os.environ.get("COMPASS_DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))

# The verified admit/reject corpus (one row per student-college decision).
CORPUS_CSV = os.environ.get(
    "COMPASS_CORPUS_CSV",
    os.path.join(DATA_DIR, "acceptance_rejected_college_data_verified.csv"),
)

# IPEDS institution DB (published admit rates, test bands) — used for tiering.
IPEDS_SQLITE = os.environ.get("COMPASS_IPEDS", os.path.join(DATA_DIR, "ipeds.sqlite"))

# Hand-seeded program catalog (legacy shape — superseded by programs.csv below,
# still read so nothing that referenced it breaks).
CATALOG_CSV = os.environ.get("COMPASS_CATALOG", os.path.join(DATA_DIR, "catalog.csv"))

# --- PROGRAM / COMPETITION REGISTRY -----------------------------------------
# sources.json is the list of databases we draw on (one entry per source, with
# the adapter that maps it into the common schema). programs.csv is that common
# schema. Adding a new competition database means editing these two files, not
# the engine. See compass/programs.py and data/README.md.
SOURCES_JSON = os.environ.get("COMPASS_SOURCES", os.path.join(DATA_DIR, "sources.json"))
PROGRAMS_CSV = os.environ.get("COMPASS_PROGRAMS", os.path.join(DATA_DIR, "programs.csv"))

# --- COLUMN MAP -------------------------------------------------------------
# Rename these to match the real headers in your corpus CSV. The code only ever
# refers to the logical names on the left, so this is the one place to adjust.
CORPUS_COLUMNS = {
    # VERIFIED against the real file (2,723 rows). The corpus is STUDENT-level:
    # one row per Reddit post, with outcomes stored as "; "-separated college LISTS.
    # data_access.load_corpus() explodes it into application rows — see #18.
    "student_id":  "post_id",
    "major":       "major_category",      # STEM | Art/Hum | SocSci | Bus/Fin | Other
    "gpa":         "gpa_band",            # BAND, e.g. "3.8+" — not a number
    "test":        "test_score_band",     # BAND, e.g. "1500+/34+" — not a number
    "body":        "post_body",           # activities/awards live in free text here
    # outcome list columns, exploded into (student, college, result) rows:
    "accepted":    "accepted_colleges",
    "rejected":    "rejected_colleges",
    "waitlisted":  "waitlisted_colleges",
    "deferred":    "deferred_colleges",
    # row-quality gates
    "status":      "post_status",         # keep "Valid result post"
    "dedup":       "dedup_keep",          # keep "Yes"
}

# How the corpus' major buckets map onto the findings-report tracks.
MAJOR_TRACKS = {
    "Bus/Fin": "business", "SocSci": "social_science",
    "Art/Hum": "humanities", "STEM": "stem_non_cs", "Other": None,
}

COLLEGE_LIST_SEP = "; "

# Minimum similar admits before we trust a school's gap read (else -> escalate).
MIN_ADMITS_PER_SCHOOL = 5

# --- Reference data sources (retrieval layer, see compass/context.py) -------
CIRCUITS_CSV = os.environ.get("COMPASS_CIRCUITS", os.path.join(DATA_DIR, "tabroom_circuits.csv"))
FINDINGS_JSON = os.environ.get("COMPASS_FINDINGS", os.path.join(DATA_DIR, "findings.json"))
# Published (official) admit rates, pulled from the web — NOT from the corpus. See #24.
ADMIT_RATES_JSON = os.environ.get("COMPASS_ADMIT_RATES", os.path.join(DATA_DIR, "admit_rates.json"))
# Minimum decisions before a per-school rate may be stated (see modules.cohort_rates)
MIN_DECISIONS_FOR_RATE = 20


# ---------------------------------------------------------------------------
# 3. OUTPUT
# ---------------------------------------------------------------------------
OUT_DIR = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT_DIR, exist_ok=True)
