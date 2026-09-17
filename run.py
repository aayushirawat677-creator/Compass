#!/usr/bin/env python3
"""
Compass engine — entry point.  Intake JSON in -> Strategic Plan PDF out.

    python run.py --intake data/sample_intake.json --out out/plan.pdf

Mock mode (default) runs with no API key so you can see the whole thing work.
Real mode:  export COMPASS_LLM_MODE=real ; export ANTHROPIC_API_KEY=<Peggy's key>
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import settings
from compass import pipeline, render


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake", required=True, help="path to an intake JSON file")
    ap.add_argument("--out", default=os.path.join(settings.OUT_DIR, "plan.pdf"))
    ap.add_argument("--dump-state", action="store_true", help="also write the full pipeline state as JSON")
    args = ap.parse_args()

    intake = json.load(open(args.intake))
    print(f"\nCompass engine  ·  mode={settings.LLM_MODE}  ·  intake={os.path.basename(args.intake)}\n")

    state = pipeline.run(intake)

    if state.get("blocked") or "draft" not in state:
        b = state.get("blocked", {})
        print("\n  ✗ RUN BLOCKED — no PDF produced, by design.")
        print(f"    step     : {b.get('step','?')}")
        print(f"    failures : {'; '.join(b.get('failures', []))}")
        if b.get("notes"): print(f"    why      : {b['notes']}")
        print("\n    A blocked run is the correct outcome here: continuing would have produced")
        print("    a complete-looking plan built on nothing. Fix the input and re-run.")
        if args.dump_state:
            json.dump(state, open(args.out.replace('.pdf', '.state.json'), 'w'),
                      indent=2, default=str)
        return
    out = render.to_pdf(state["draft"], args.out)
    print(f"\n✓ Strategic plan written to: {out}")

    if args.dump_state:
        sp = args.out.replace(".pdf", ".state.json")
        json.dump(state, open(sp, "w"), indent=2, default=str)
        print(f"✓ Full pipeline state:      {sp}")

    if state.get("critic", {}).get("verdict") != "pass":
        print("  note: the communication critic flagged the draft — see the state dump.")


if __name__ == "__main__":
    main()
