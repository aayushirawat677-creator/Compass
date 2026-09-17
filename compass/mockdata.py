"""
Canned, correctly-shaped step outputs so the pipeline runs end-to-end and produces a
FULL v10-design PDF with no API key. Modeled on 'Maya, Grade 9, robotics, MIT'.
The 'writer' entry is the full StrategicPlan the renderer consumes — keep it richly
populated so mock runs look like a real, fleshed plan (not thin). Real mode replaces
each of these with an actual Claude call.
"""

def for_step(step: str) -> dict:
    return _MOCK.get(step, {})

_MOCK = {
    # --- intermediate steps (feed each other; not rendered directly) ---
    "profile": {"spine": {"activity": "Robotics", "confidence": "high"},
                "intended": {"colleges": ["MIT"], "major": "Computer Science", "grade": "9"},
                "constraints": {"budget": "$5,000/yr", "location_radius": "in-state / online",
                                "hard_nos": ["nothing out of state"], "stated_worry": "she freezes when it gets competitive"}},
    "projected": {"pattern": "MIT-CS admits show a deep, self-driven technical spine with a concrete, verifiable result"},
    "gap": {"gaps": [{"domain": "research", "category": "missing", "frequency": "7 of 10"},
                     {"domain": "robotics", "category": "lower-level", "frequency": "6 of 10"}],
            "strengths": [{"domain": "robotics", "note": "self-directed spine"}]},
    "strategy": {"selected_moves": [{"move": "deepen robotics toward national", "intensity": "core"},
                                    {"move": "add a mentored research project", "intensity": "core"}]},

    "two_paths": {
        "target_variant": {
            "spine": "robotics",
            "achievement_profile": [
                {"credential": "Regional robotics competitor, team member", "level": "regional"},
                {"credential": "Three years of self-built projects, documented", "level": "sustained"}],
            "course_targets": {"gpa": "3.8+", "math": "Calculus by 12th"},
            "moves_included": ["grow robotics to a competition record", "hold the GPA floor"]},
        "stretch_variant": {
            "spine": "robotics",
            "achievement_profile": [
                {"credential": "State qualifier, team lead", "level": "state", "via": "intensified"},
                {"credential": "A documented build with an external result", "level": "regional",
                 "via": "intensified"},
                {"credential": "Placement at an engineering design competition", "level": "state",
                 "via": "added"}],
            "course_targets": {"gpa": "3.9-4.0", "math": "Calculus by 11th"},
            "moves_included": ["grow robotics", "hold the GPA floor", "add a design competition"],
            "intensified": ["robotics: regional -> state, member -> team lead"],
            "added": ["engineering design competition placement"]},
        "fit_assessment": [
            {"school": "Carnegie Mellon University", "pattern_coverage":
             "covers 3 of 5 credentials common to admits on target; 4 of 5 on stretch",
             "covered_of_total": "3/5 -> 4/5", "n": 38, "sufficient": True}],
        "delta": {"what_is_harder": ["math a year earlier", "one more competition cycle"],
                  "extra_hours_per_week": 4, "extra_cost": "$300-600 competition fees",
                  "added_risk": "a heavier junior year alongside the test cycle"}
    },
    "plan_goals": {"current_year": [{"goal_title": "Enter a first regional robotics competition",
                                     "tasks": [{"task_title": "Join the robotics team", "when": "Fall G9"}]}]},
    "plan_recs": {"task_id": "T1", "options": [{"name": "A free online intro-to-robotics course", "cost_usd": 0}]},
    "critic": {"verdict": "pass", "findings": []},

    # --- the WRITER output = the full StrategicPlan the renderer draws (v10 design) ---
    "writer": {
      "cover": {"student": "Maya R.", "grade": "9", "prepared": "September 2026", "family": "R.", "date": "Sept 2026"},
      "profile": {
        "title": "About Maya.",
        "lead": "A 9th grader who builds robots at home for fun — this plan points that self-driven energy at one clear result before high school scatters it.",
        "blocks": [
          {"subhead": "Her main strength: a self-driven technical spine.",
           "thesis": "What she does without being asked is what we build on.",
           "body": "Maya builds robots at home on weekends, without being told to — the single clearest signal in her profile, and the thing MIT-tier CS admits share: a deep, self-directed technical through-line. She's competed at the regional level. The plan is to deepen that one spine toward a national result and a documented project, not to add breadth around it."},
          {"subhead": "Her other activities: keep them, don't add to them.",
           "thesis": "Dance and her academics — steady, not expanded.",
           "body": "She's danced for five years and holds a strong GPA. These matter as supporting activities and a solid floor, but they're not the spine. The plan keeps them steady and adds nothing new."},
          {"subhead": "How she works best: low-stakes first, steady encouragement.",
           "thesis": "A perfectionist who does her best work when she can practice before performing.",
           "body": "She's a careful perfectionist who freezes when things get competitive, so every new step starts low-stakes and social, with a way to recover from a bad day. A national competition as step one would make her quit; smaller competitions first build the confidence for bigger stages later."},
          {"subhead": "What's working in her favor — and the real limits.",
           "thesis": "A STEM-focused school and a real spine — built for a tight budget and one home base.",
           "body": "Her school has a robotics lab and a supportive STEM culture. Real life shapes the plan too: the family activity budget is about $5,000 a year, they're rural and in-state only, so the plan favors low-cost, local, online-first options over expensive travel programs."}],
        "flags": "No high-school transcript yet — GPA and test figures here are entering targets, not records. Confirm her 8th-grade math placement, which sets her high-school math ceiling."},
      "target": {
        "lead": "The steady, realistic plan — the card below, turned into admission odds. Read each percentage as a condition: if she builds this profile, this is how often similar applicants got in.",
        "card": {"label": "TARGET PLAN · CLASS OF 2030 · PROJECTED",
          "title": "The self-built engineer.",
          "subtitle": "A deep robotics spine plus one documented project, built over four years.",
          "stats": [{"k": "GPA (target)", "v": "3.9+", "sub": "UW"}, {"k": "Testing floor", "v": "1500+", "sub": "/ 34+"},
                    {"k": "Rigor", "v": "7–9", "sub": "APs, paced"}, {"k": "Math ceiling", "v": "Calc BC", "sub": "by 12th"}],
          "credentials": [
            {"h": "State-level robotics result.", "t": "Grows from regional to a state placement — the self-driven technical result CS programs look for."},
            {"h": "A documented independent project.", "t": "A mentored build or research output with a real artifact — beyond-school work that stands out."},
            {"h": "A sustained STEM role.", "t": "A steady role on the robotics team; depth over titles."},
            {"h": "Strong, protected academics.", "t": "GPA held at 3.9+, advanced math on track — the floor kept solid, not chased."}],
          "within_reach": "Target 35–60% Georgia Tech · UIUC · Purdue · Likely 60%+ UC Davis · ASU · in-state publics",
          "toughest": "Reach 15–35% Carnegie Mellon · UMich · UW · Far reach <15% MIT · Stanford · Caltech",
          "takeaway": "A strong, self-built profile that makes Georgia Tech and Purdue realistic — with MIT as an honest long shot, not the plan."},
        "bands": {"intro": "TARGET PLAN — the odds if she reaches this profile: 3.9+ GPA, a state robotics result, and a documented project.",
          "bands": [
            {"name": "Far Reach", "range": "< 15%", "colleges": [{"name": "MIT"}, {"name": "Stanford"}, {"name": "Caltech"}]},
            {"name": "Reach", "range": "15–35%", "colleges": [{"name": "Carnegie Mellon"}, {"name": "UMichigan"}, {"name": "UW Seattle"}]},
            {"name": "Target", "range": "35–60%", "colleges": [{"name": "Georgia Tech"}, {"name": "UIUC"}, {"name": "Purdue"}]},
            {"name": "Likely", "range": "60%+", "colleges": [{"name": "UC Davis"}, {"name": "ASU"}, {"name": "SJSU"}]}]}},
      "stretch": {
        "lead": "The same student, pushed harder — most schools become more reachable. Same condition: the odds if she reaches this stronger profile.",
        "card": {"label": "STRETCH PLAN · CLASS OF 2030 · PROJECTED",
          "title": "The same spine, driven to the top.",
          "subtitle": "Her one spine pushed harder and earlier — every school becomes more reachable.",
          "stats": [{"k": "GPA (target)", "v": "3.95–4.0", "sub": "UW"}, {"k": "Testing floor", "v": "1550+", "sub": "/ 35+"},
                    {"k": "Rigor", "v": "10–12", "sub": "APs"}, {"k": "Math ceiling", "v": "Calc BC", "sub": "by 11th"}],
          "credentials": [
            {"h": "National robotics result.", "t": "Reaches a national competition with a standout result — her spine, proven at the top."},
            {"h": "A published research output.", "t": "The independent project taken to a submission or publication — a real capstone, not a hobby."},
            {"h": "A leadership role with impact.", "t": "Leads a build team or mentors younger students — impact, not a title."},
            {"h": "Front-loaded rigor + a funded summer.", "t": "Calculus a year ahead, more APs early, and a selective program that offers aid."}],
          "within_reach": "Target 35–60% Carnegie Mellon · UMich · UW · Likely 60%+ Georgia Tech · UIUC · Purdue",
          "toughest": "Reach 15–35% MIT · Stanford · Caltech · UC Berkeley (EECS)",
          "takeaway": "The same student, pushed further: this plan moves MIT, Stanford, and Caltech from long shots to real reaches."},
        "bands": {"intro": "STRETCH PLAN — the odds if she reaches this profile · the top-tech schools move up a tier · the in-state anchors stay likely.",
          "bands": [
            {"name": "Far Reach", "range": "< 15%", "colleges": []},
            {"name": "Reach", "range": "15–35%", "colleges": [{"name": "MIT", "up": True}, {"name": "Stanford", "up": True}, {"name": "Caltech", "up": True}, {"name": "Berkeley EECS", "up": True}]},
            {"name": "Target", "range": "35–60%", "colleges": [{"name": "Carnegie Mellon", "up": True}, {"name": "UMichigan", "up": True}, {"name": "UW Seattle", "up": True}]},
            {"name": "Likely", "range": "60%+", "colleges": [{"name": "Georgia Tech", "up": True}, {"name": "UIUC", "up": True}, {"name": "Purdue", "up": True}]}]}},
      "course": {
        "lead": "The course level to aim for when she picks classes — both plans, side by side. These are targets, not grades she already has.",
        "target_gpa": "3.9+ UW", "stretch_gpa": "3.95–4.0 UW",
        "target_bullets": ["Advanced-math placement (on track for Calculus BC by 12th)", "Honors track where offered; a paced AP arc", "Strong PSAT baseline in 10th, no early testing pressure"],
        "stretch_bullets": ["One year ahead in math (Calculus BC by 11th)", "AP Physics / CS early, in her spine's subjects", "Front-loaded rigor that still protects downtime"],
        "table": [
          {"track": "Math", "target": "Precalc 10th → Calculus BC by 12th", "stretch": "Calculus BC by 11th + Multivariable"},
          {"track": "CS / Engineering (spine)", "target": "AP CS A; robotics electives", "stretch": "AP CS A early + advanced/dual-enroll"},
          {"track": "Science", "target": "Honors sequence + AP Physics 1", "stretch": "AP Physics C + a second AP science"},
          {"track": "English", "target": "Honors English", "stretch": "Honors → AP Lang & Lit"},
          {"track": "Total APs (9–12)", "target": "7–9, sustainably paced", "stretch": "10–12, front-loaded but protected"}],
        "note": "Confirm her 8th-grade math placement this fall — it sets how far she can go in math. Keep the load sustainable; depth over a rigor pile-up."},
      "roadmap": {
        "title": "Grades 9 to 12: deepen, then stand out.",
        "lead": "A strong profile isn't built by adding activities — it's built by taking one real spine deep. The four years have three stages, and Maya is at the start.",
        "stages": [
          {"grade": "GRADE 9", "name": "Deepen", "body": "Enter real robotics competitions and start an independent build. Set strong study habits.", "color": ""},
          {"grade": "GRADE 10–11", "name": "Specialize", "body": "State-level results, a mentored research project, first AP classes.", "color": "g"},
          {"grade": "GRADE 12", "name": "Stand out", "body": "National reach, a documented capstone, leadership, the essay.", "color": "p"}],
        "grades": [
          {"grade": "Grade 9", "years": "2026–27 · YOU ARE HERE", "tag": "Deepen the one spine.", "rows": [
            {"title": "Enter a first regional robotics competition.", "tasks": [
              {"term": "Fall", "text": "Join the school robotics team and pick a build role — low-stakes, on a team."},
              {"term": "Spring", "text": "Enter one regional competition; keep it to one."}]},
            {"title": "Start the fundamentals for an independent project.", "tasks": [
              {"term": "Fall", "text": "Complete a free intro robotics/CS course; begin a small independent build."}]},
            {"title": "Set strong study habits and confirm math placement.", "tasks": [
              {"term": "Fall–Winter", "text": "Lock advanced-math placement; hold the GPA; strong habits from the start."}]}]},
          {"grade": "Grades 10–11", "years": "2027–29", "tag": "Specialize and go deep.", "rows": [
            {"title": "Reach the state level in robotics.", "tasks": [{"term": "All year", "text": "Compete and aim to place at state; lead by contributing, not by a title."}]},
            {"title": "Begin a mentored research project.", "tasks": [{"term": "All year", "text": "Start a mentored build/research project toward a documented output."}]},
            {"title": "First AP classes; hold 3.9+.", "tasks": [{"term": "All year", "text": "AP CS / Physics in her spine; keep the load sustainable."}]}]},
          {"grade": "Grade 12", "years": "2029–30", "tag": "Stand out, then apply.", "rows": [
            {"title": "National reach + a documented capstone.", "tasks": [{"term": "Fall", "text": "Push for a national result; finish the research submission; lead a build team."}]},
            {"title": "Apply, and finish strong.", "tasks": [{"term": "Fall", "text": "Finalize the list; EA/ED; secure recommenders; essays drafted around her spine."}]}]}]},
      "this_year": {
        "title": "Grade 9, term by term.",
        "lead": "Fall is laid out in full — real options, prices, and a \"plan by\" date a few weeks before each deadline. Spring and summer are kept short on purpose.",
        "cards": [
          {"cat": "Robotics", "cat_class": "debate", "title": "Join the robotics team and pick a role", "act": "ACT NOW",
           "body": "The one spine to deepen — a team activity that counts, low-pressure to start. Two low-cost options:",
           "options": ["1 · Free — the school robotics team. Ask the STEM teacher about joining this semester.",
                       "2 · Budget — a free online intro-to-robotics course to build fundamentals alongside."],
           "plan_by": "This week — team rosters set early in the fall.", "note": None},
          {"cat": "Academics", "cat_class": "academics", "title": "Confirm math placement", "act": "ACT NOW",
           "body": "Free · through the school. Confirm her 8th→9th math placement — it sets her high-school math ceiling — and get the course catalog before selection opens.",
           "options": [], "plan_by": "Early October — before course selection opens.", "note": None},
          {"cat": "Venture", "cat_class": "venture", "title": "Enter one regional competition (spring)", "act": "PLAN AHEAD",
           "body": "One first, low-stakes competition once she has a semester of practice — her coach enters her; she doesn't sign up alone.",
           "options": [], "plan_by": "Late fall — commit a few weeks before the registration window.", "note": "Keep it to one — a perfectionist needs the reps before the stakes."}]},
      "parent_actions": {
        "lead": "Ordered by deadline, each with a few weeks of room built in. None take much from Maya — the point is to handle the setup so her week stays light.",
        "items": [
          {"n": 1, "when": "This week", "text": "Get her on the school robotics team; if rosters are full, start the free online course so she's building either way."},
          {"n": 2, "when": "By early October", "text": "Book the counseling meeting; confirm her 8th-grade math placement and request the course catalog."},
          {"n": 3, "when": "By late fall", "text": "Through the team, commit to ONE spring regional competition — a few weeks before its registration window."},
          {"n": 4, "when": "Ongoing", "text": "Keep dance and academics steady; protect one weekly downtime block; add nothing new this year."},
          {"n": 5, "when": "Winter refresh", "text": "Revisit this plan in December–January to pick a low-cost, local summer option before registration opens."}]},
      "final_note": [
        "You told us Maya has real potential but freezes when things get competitive — and that budget and being rural shape what's possible. This plan is built around exactly that: it grows her through small, local, low-cost wins first, protects a strong GPA, and never asks for more time or money than your family has.",
        "She already has what most 9th graders are still looking for — a technical spine she drives herself. The next few years are about taking that one thing deep, not adding more. A careful perfectionist who is given fewer things and more support doesn't fall behind — she keeps getting stronger."]
    },
}
