"""
Does the same draft still render the same document?  [#89][#92]

The question behind this file is Aayushi's: *"make sure if i run again, my system should
generate same of pdf."* That question has three different answers and it matters which
one is being asked.

    1. SAME DRAFT -> SAME DOCUMENT.   Guaranteed, and this file is the proof. The HTML is
       byte-identical across renders; the PDF is not, because WeasyPrint stamps a creation
       time into it. So the golden is the HTML.

    2. SAME INTAKE -> SAME SHAPE.     Guaranteed by the gate set, not by luck. Twenty-odd
       gates reject a draft that is missing the stat row, the four tiers, the requirement
       citations. A second run that came back differently shaped would be REJECTED, which
       is what reproducible means for a generative system.

    3. SAME INTAKE -> SAME WORDS.     Not achievable, and not worth chasing. A language
       model at temperature 0 still varies with batching and serving. What must not vary
       is whether the document is correct.

This file answers (1) and tells you when a render change was intentional. [#92]
Answer (2) is the gate set; answer (3) is not a goal.

    python evals/golden.py            check against the stored golden
    python evals/golden.py --update   accept the current render as the new golden
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Drop compiled bytecode before importing. [#91] Python decides a .pyc is fresh by
# comparing the source's mtime at ONE-SECOND granularity, so an edit saved inside the same
# second as the previous import is silently ignored and the module that loads is not the
# module on disk. We hit exactly that: render.py written 85ms after its own .pyc, and the
# loaded CSS disagreed with the file for a full minute of confused debugging. For a tool
# whose entire job is "does the source still produce this document", reading stale
# bytecode is the one failure that invalidates the answer.
import shutil                                                     # noqa: E402
for _d in ("compass", "evals"):
    shutil.rmtree(os.path.join(ROOT, _d, "__pycache__"), ignore_errors=True)

from compass import render                                        # noqa: E402

HERE = os.path.join(ROOT, "evals", "golden")
DRAFT = os.path.join(HERE, "draft.json")
HASH = os.path.join(HERE, "render.sha256")
SNAP = os.path.join(HERE, "render.html")


def current():
    draft = json.load(open(DRAFT))
    html = render.TEMPLATE.render(css=render.CSS, c=render._safe(draft))
    return html, hashlib.sha256(html.encode()).hexdigest()


def main():
    html, digest = current()
    if "--update" in sys.argv or not os.path.exists(HASH):
        open(HASH, "w").write(digest + "\n")
        open(SNAP, "w").write(html)
        print(f"golden updated: {digest[:16]}  ({len(html):,} bytes)")
        return 0

    want = open(HASH).read().strip()
    if digest == want:
        print(f"ok  render unchanged: {digest[:16]}")
        return 0

    print(f"FAIL  render changed\n      was {want[:16]}\n      now {digest[:16]}")
    old = open(SNAP).read().splitlines() if os.path.exists(SNAP) else []
    import difflib
    diff = [l for l in difflib.unified_diff(old, html.splitlines(), "golden", "current",
                                            lineterm="", n=1)][:40]
    for line in diff:
        print("      " + line)
    print("\n      If this was intended: python evals/golden.py --update")
    return 1


if __name__ == "__main__":
    sys.exit(main())
