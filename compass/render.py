"""
StrategicPlan JSON -> HTML -> PDF, in the Compass design language (matches the v10 look):
dark cover, cream pages, gold section labels, serif headings, green/purple projected
stat-cards, 4-column tier bands, a roadmap timeline, recommendation cards, numbered
parent actions, and a dark final note. Data-driven from the `plan` dict — see the schema
used in neerav_trial.py / mockdata.py.
"""
import os
from jinja2 import Template

CSS = r"""
@page { size: letter; margin: 0; }
@page content { margin: 44px 58px 44px; }
* { box-sizing: border-box; }
:root{
  --ink:#1c2a21; --cream:#f4f1e8; --card:#fbfaf4; --gold:#a5852f; --gold2:#9c7b2e;
  --muted:#6f7469; --line:#e0dccb; --green:#5c6b3d; --greenbg:#e7ecd7;
  --purple:#5b4a86; --purplebg:#e8e4f1; --tan:#efe8d6;
}
body{ margin:0; color:#20281f; font-family:'Inter','Helvetica Neue',Arial,sans-serif; font-size:10.5px; line-height:1.42; }
.serif{ font-family:'Playfair Display','Georgia',serif; }
h1,h2,h3,.serif{ font-family:'Playfair Display','Georgia',serif; color:#182117; font-weight:700; }

/* ---------- cover ---------- */
.cover{ page: cover; background:var(--ink); color:#efeadc; height:100vh; padding:60px 64px; position:relative; }
.cover .brand{ color:var(--gold); letter-spacing:.28em; font-size:12px; font-weight:700; }
.cover .logo{ position:absolute; top:56px; right:64px; color:var(--gold); font-size:34px; }
.cover .title{ position:absolute; bottom:150px; left:64px; font-size:78px; line-height:.98; color:#f4efe1; }
.cover .sub{ position:absolute; bottom:112px; left:66px; color:var(--gold); font-style:italic; font-size:19px; }
.cover .foot{ position:absolute; bottom:56px; left:64px; right:64px; display:flex; justify-content:space-between;
  border-top:1px solid #3a463a; padding-top:10px; color:#8a927f; letter-spacing:.12em; font-size:9.5px; }

/* ---------- content page frame ---------- */
.page{ page: content; padding:0; page-break-before:always; }
.rhead{ color:#9aa08f; letter-spacing:.18em; font-size:9px; text-transform:uppercase; margin-bottom:12px; }
.slabel{ color:var(--gold2); letter-spacing:.16em; font-size:10px; font-weight:700; text-transform:uppercase; margin-bottom:6px; }
h2.sec{ font-size:32px; margin:0 0 8px; }
.lead{ color:var(--muted); font-style:italic; font-size:13px; line-height:1.42; max-width:82%; margin-bottom:14px; }
.subhead{ font-size:15px; margin:16px 0 2px; }
.thesis{ color:var(--gold2); font-style:italic; font-size:12px; margin-bottom:5px; }
p{ margin:4px 0; }
.small{ font-size:10px; } .mut{ color:var(--muted); }

/* boxes */
.box{ background:var(--tan); border-left:4px solid var(--gold); padding:12px 15px; border-radius:3px; margin:14px 0; }
.box .lab{ color:var(--gold2); letter-spacing:.14em; font-size:9.5px; font-weight:700; text-transform:uppercase; margin-bottom:4px; }
.darkbox{ background:var(--ink); color:#efeadc; border-radius:6px; padding:16px 18px; margin:12px 0; }
.darkbox .lab{ color:var(--gold); letter-spacing:.16em; font-size:10px; font-weight:700; text-transform:uppercase; margin-bottom:6px; }
.darkbox p{ font-style:italic; }

/* projected card */
.pcard{ border:1px solid var(--line); border-radius:8px; background:var(--card); margin:10px 0 6px; overflow:hidden; }
.pcard .bar{ height:6px; }
.pcard .body{ padding:16px 18px; }
.pcard .plabel{ color:var(--muted); letter-spacing:.14em; font-size:9px; font-weight:700; text-transform:uppercase; }
.pcard h3{ font-size:19px; margin:3px 0 2px; }
.pcard .psub{ color:var(--muted); font-style:italic; font-size:11px; margin-bottom:10px; }
.stats{ display:flex; flex-wrap:wrap; gap:8px; margin:8px 0; }
.stat{ flex:1 1 46%; border:1px solid var(--line); border-radius:5px; padding:8px 10px; background:#fff; }
.stat .k{ color:var(--muted); letter-spacing:.1em; font-size:8.5px; text-transform:uppercase; }
.stat .v{ font-size:17px; font-weight:700; } .stat .v small{ font-weight:400; color:var(--muted); font-size:10px; }
.cred{ margin-top:8px; } .cred .lab{ color:var(--gold2); letter-spacing:.12em; font-size:9px; font-weight:700; text-transform:uppercase; margin-bottom:4px; }
.cred li{ list-style:none; padding-left:14px; position:relative; margin:4px 0; }
.cred li:before{ content:'▪'; position:absolute; left:0; color:var(--green); }
.reachrow{ display:flex; gap:16px; margin-top:8px; font-size:10px; }
.reachrow .lab{ letter-spacing:.1em; font-size:8.5px; font-weight:700; text-transform:uppercase; color:var(--muted); }

/* tier bands */
.bands{ display:flex; gap:10px; margin:8px 0; }
.band{ flex:1; border:1px solid var(--line); border-radius:6px; padding:10px; }
.band .bh{ font-weight:700; letter-spacing:.08em; font-size:9.5px; text-transform:uppercase; color:#3a463a; }
.band .br{ color:var(--muted); font-style:italic; font-size:10px; margin-bottom:6px; }
.pill{ border:1px solid var(--line); border-radius:4px; padding:4px 7px; margin:4px 0; font-size:10px; background:#fff; }
.pill.likely{ background:var(--greenbg); border-color:#cdd8b6; }

/* course targets */
.ct{ display:flex; gap:14px; margin:10px 0; }
.ct .c{ flex:1; border-radius:6px; padding:12px 14px; }
.ct .c.t{ background:#eef1e4; border-top:4px solid var(--green); }
.ct .c.s{ background:#eee9f4; border-top:4px solid var(--purple); }
.ct .c .k{ letter-spacing:.12em; font-size:9px; font-weight:700; text-transform:uppercase; color:var(--muted); }
.ct .c .g{ font-size:26px; font-weight:700; margin:2px 0 6px; }
table{ width:100%; border-collapse:collapse; margin-top:8px; }
th,td{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); font-size:10px; vertical-align:top; }
th{ color:#3a463a; letter-spacing:.06em; font-size:9px; text-transform:uppercase; }
td.tg{ color:var(--green); } td.st{ color:var(--purple); }

/* roadmap */
.grow.stretchgoal{ border-left:3px solid var(--purple); padding-left:9px; background:rgba(91,74,134,.045); }
.trackpill{ font-size:7.5px; letter-spacing:.1em; text-transform:uppercase; padding:1px 5px;
  border-radius:8px; margin-left:6px; vertical-align:2px; }
.trackpill.s{ background:var(--purplebg); color:var(--purple); }
.why{ font-size:9.5px; color:var(--muted); font-style:italic; margin:1px 0 3px; }
.stages{ display:flex; gap:12px; margin:10px 0; }
.stage{ flex:1; border:1px solid var(--line); border-top:3px solid var(--gold); border-radius:5px; padding:10px 12px; }
.stage.g{ border-top-color:var(--green); } .stage.p{ border-top-color:var(--purple); }
.stage .k{ letter-spacing:.12em; font-size:8.5px; font-weight:700; text-transform:uppercase; color:var(--muted); }
.stage h4{ margin:2px 0 4px; font-size:15px; } .stage.g h4{ color:var(--green); } .stage.p h4{ color:var(--purple); }
.gradebar{ background:var(--ink); color:#efeadc; border-radius:6px 6px 0 0; padding:9px 14px; display:flex; justify-content:space-between; margin-top:14px; }
.gradebar .g{ font-family:'Playfair Display',serif; font-size:17px; font-weight:700; }
.gradebar .yrs{ color:#b7bda9; font-size:9px; letter-spacing:.1em; }
.gradebar .tag{ color:var(--gold); font-style:italic; font-size:12px; }
.gwrap{ border:1px solid var(--line); border-top:none; border-radius:0 0 6px 6px; padding:10px 14px; margin-bottom:10px; }
.grow{ margin:7px 0; } .grow .t{ font-weight:700; padding-left:14px; position:relative; }
.grow .t:before{ content:'■'; position:absolute; left:0; font-size:9px; }
.grow .task{ display:flex; gap:8px; margin:3px 0 3px 14px; }
.termpill{ background:var(--tan); color:#5a5030; border-radius:3px; padding:2px 7px; font-size:8.5px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; white-space:nowrap; height:fit-content; }

/* recommendation cards */
.reccard{ border:1px solid var(--line); border-left:4px solid var(--gold); border-radius:5px; background:var(--card); padding:12px 14px; margin:10px 0; }
.catpill{ background:var(--ink); color:#efeadc; border-radius:3px; padding:2px 7px; font-size:8.5px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.catpill.debate{ background:var(--purple); } .catpill.venture{ background:var(--gold); color:#241d07; }
.catpill.service{ background:var(--green); } .catpill.academics{ background:#3a463a; }
.actpill{ background:#e7e0cb; color:#6a5a2a; border-radius:3px; padding:2px 7px; font-size:8px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.reccard h4{ display:inline; font-size:14px; margin:0 6px; }
.planby{ color:var(--gold2); font-weight:700; font-size:10px; margin-top:6px; }

/* parent actions */
.pa{ display:flex; gap:12px; margin:10px 0; }
.pa .n{ width:22px; height:22px; border:1.5px solid var(--gold); border-radius:50%; color:var(--gold2); font-weight:700;
  text-align:center; line-height:19px; font-size:11px; flex:none; }
.pa .when{ color:var(--gold2); letter-spacing:.1em; font-size:9px; font-weight:700; text-transform:uppercase; }
"""

TEMPLATE = Template(r"""
<style>{{ css }}</style>

<!-- COVER -->
<div class="cover">
  <div class="brand">◉ COMPASS</div><div class="logo">✦</div>
  <div class="title serif">Strategic<br>Plan.</div>
  <div class="sub">{{ c.cover.student }} · Grade {{ c.cover.grade }} · Prepared {{ c.cover.prepared }}</div>
  <div class="foot"><span>CONFIDENTIAL · {{ c.cover.family|upper }} FAMILY</span><span>GENERATED FROM INTAKE · {{ c.cover.date|upper }}</span></div>
</div>

{% macro pcard(card, color) %}
<div class="pcard">
  <div class="bar" style="background:{{ '#5c6b3d' if color=='g' else '#5b4a86' }}"></div>
  <div class="body">
    <div class="plabel">{{ card.label }}</div>
    <h3 class="serif">{{ card.title }}</h3>
    <div class="psub">{{ card.subtitle }}</div>
    <div class="stats">
      {% for s in card.stats %}<div class="stat"><div class="k">{{ s.k }}</div><div class="v">{{ s.v }} <small>{{ s.sub }}</small></div></div>{% endfor %}
    </div>
    <div class="cred"><div class="lab">Load-bearing credentials</div><ul>
      {% for cr in card.credentials %}<li><strong>{{ cr.h }}</strong> {{ cr.t }}</li>{% endfor %}</ul></div>
    <div class="reachrow">
      <div><div class="lab">▲ Within reach</div>{{ card.within_reach }}</div>
      <div><div class="lab">★ Toughest reaches</div>{{ card.toughest }}</div>
    </div>
    <div class="darkbox"><div class="lab">Takeaway</div><p>{{ card.takeaway }}</p></div>
  </div>
</div>
{% endmacro %}

{% macro bands(bset) %}
<p class="small mut" style="margin:10px 0 4px">{{ bset.intro }}</p>
<div class="bands">
  {% for b in bset.bands %}
  <div class="band"><div class="bh">{{ b.name }}</div><div class="br">{{ b.range }}</div>
    {% for col in b.colleges %}<div class="pill {{ 'likely' if b.name=='Likely' else '' }}">{{ '↑ ' if col.up else '' }}{{ col.name }}</div>{% endfor %}
  </div>{% endfor %}
</div>
{% endmacro %}

<!-- 01 PROFILE -->
<div class="page">
  <div class="rhead">Compass · Strategic Plan · {{ c.cover.student }} · Grade {{ c.cover.grade }}</div>
  <div class="slabel">01 · Profile</div>
  <h2 class="sec">{{ c.profile.title }}</h2>
  <div class="lead">{{ c.profile.lead }}</div>
  {% for blk in c.profile.blocks %}
    <div class="subhead serif">{{ blk.subhead }}</div>
    <div class="thesis">{{ blk.thesis }}</div>
    <p>{{ blk.body }}</p>
  {% endfor %}
  <div class="box"><div class="lab">Flags to confirm</div><p class="small">{{ c.profile.flags }}</p></div>
</div>

<!-- 02 TARGET PLAN -->
<div class="page">
  <div class="rhead">Compass · Strategic Plan · {{ c.cover.student }} · Grade {{ c.cover.grade }}</div>
  <div class="slabel">02 · The Target Plan</div>
  <h2 class="sec">The Target plan.</h2>
  <div class="lead">{{ c.target.lead }}</div>
  {{ pcard(c.target.card, 'g') }}
  {{ bands(c.target.bands) }}
</div>

<!-- 03 STRETCH PLAN -->
<div class="page">
  <div class="rhead">Compass · Strategic Plan · {{ c.cover.student }} · Grade {{ c.cover.grade }}</div>
  <div class="slabel">03 · The Stretch Plan</div>
  <h2 class="sec">The Stretch plan.</h2>
  <div class="lead">{{ c.stretch.lead }}</div>
  {{ pcard(c.stretch.card, 'p') }}
  {{ bands(c.stretch.bands) }}
</div>

<!-- 04 COURSE TARGETS -->
<div class="page">
  <div class="rhead">Compass · Strategic Plan · {{ c.cover.student }} · Grade {{ c.cover.grade }}</div>
  <div class="slabel">04 · Course & Grade Targets</div>
  <h2 class="sec">Course and grade targets.</h2>
  <div class="lead">{{ c.course.lead }}</div>
  <div class="ct">
    <div class="c t"><div class="k">Target plan — entering targets</div><div class="g serif">{{ c.course.target_gpa }}</div>
      <ul>{% for b in c.course.target_bullets %}<li>{{ b }}</li>{% endfor %}</ul></div>
    <div class="c s"><div class="k">Stretch plan — entering targets</div><div class="g serif">{{ c.course.stretch_gpa }}</div>
      <ul>{% for b in c.course.stretch_bullets %}<li>{{ b }}</li>{% endfor %}</ul></div>
  </div>
  <table><tr><th>Track</th><th>Target plan</th><th>Stretch plan</th></tr>
    {% for r in c.course.table %}<tr><td>{{ r.track }}</td><td class="tg">{{ r.target }}</td><td class="st">{{ r.stretch }}</td></tr>{% endfor %}
  </table>
  <div class="box"><p class="small mut" style="font-style:italic">{{ c.course.note }}</p></div>
</div>

<!-- 05 ROADMAP -->
<div class="page">
  <div class="rhead">Compass · Strategic Plan · {{ c.cover.student }} · Grade {{ c.cover.grade }}</div>
  <div class="slabel">05 · The Roadmap</div>
  <h2 class="sec">{{ c.roadmap.title }}</h2>
  <div class="lead">{{ c.roadmap.lead }}</div>
  <div class="stages">
    {% for s in c.roadmap.stages %}<div class="stage {{ s.color }}"><div class="k">{{ s.grade }}</div><h4 class="serif">{{ s.name }}</h4><p class="small">{{ s.body }}</p></div>{% endfor %}
  </div>
  {% for g in c.roadmap.grades %}
    <div class="gradebar"><span><span class="g">{{ g.grade }}</span> <span class="yrs">{{ g.years }}</span></span><span class="tag">{{ g.tag }}</span></div>
    <div class="gwrap">
      {% for row in (g.goals or g.rows) %}
        <div class="grow {{ 'stretchgoal' if row.track == 'stretch' else '' }}">
          <div class="t">{{ row.goal or row.title }}{% if row.track == 'stretch' %}<span class="trackpill s">stretch</span>{% endif %}</div>
          {% if row.why_now %}<div class="why">{{ row.why_now }}</div>{% endif %}
          {% for t in row.tasks %}<div class="task"><span class="termpill">{{ t.term }}</span><span>{{ t.text }}{% if t.track == 'stretch' %}<span class="trackpill s">stretch</span>{% endif %}</span></div>{% endfor %}
        </div>
      {% endfor %}
    </div>
  {% endfor %}
</div>

{% macro reccard(r) %}
    <div class="reccard">
      <span class="catpill {{ r.cat_class }}">{{ r.cat }}</span> <span class="serif" style="font-size:14px;font-weight:700">{{ r.title }}</span> <span class="actpill">{{ r.act }}</span>
      <p class="small">{{ r.body }}</p>
      {% for o in r.options %}<p class="small" style="margin:3px 0">{{ o|safe }}</p>{% endfor %}
      {% if r.contact %}<p class="small" style="color:#9c7b2e">CONTACT — {{ r.contact }}</p>{% endif %}
      <div class="planby">PLAN BY — {{ r.plan_by }}</div>
      {% if r.note %}<div class="box" style="margin-top:8px"><p class="small">{{ r.note }}</p></div>{% endif %}
    </div>
{% endmacro %}

<!-- 06 THIS YEAR -->
<div class="page">
  <div class="rhead">Compass · Strategic Plan · {{ c.cover.student }} · Grade {{ c.cover.grade }}</div>
  <div class="slabel">06 · This Year, Specifically</div>
  <h2 class="sec">{{ c.this_year.title }}</h2>
  <div class="lead">{{ c.this_year.lead }}</div>
  {% if c.this_year.terms %}
    {% for t in c.this_year.terms %}
      <div class="gradebar"><span><span class="g" style="font-size:15px">{{ t.term }}</span> <span class="yrs">{{ t.dates }}</span></span><span class="tag">{{ t.tag }}</span></div>
      <div class="gwrap">
        {% if t.intro %}<p class="small mut" style="font-style:italic;margin-bottom:6px">{{ t.intro }}</p>{% endif %}
        {% for r in t.cards %}{{ reccard(r) }}{% endfor %}
      </div>
    {% endfor %}
  {% else %}
    {% for r in c.this_year.cards %}{{ reccard(r) }}{% endfor %}
  {% endif %}
</div>

<!-- 07 PARENT ACTIONS -->
<div class="page">
  <div class="rhead">Compass · Strategic Plan · {{ c.cover.student }} · Grade {{ c.cover.grade }}</div>
  <div class="slabel">07 · Parent Actions</div>
  <h2 class="sec">What to do now.</h2>
  <div class="lead">{{ c.parent_actions.lead }}</div>
  {% for a in c.parent_actions['items'] %}
    <div class="pa"><div class="n">{{ a.n }}</div><div><div class="when">{{ a.when }}</div><div class="small">{{ a.text }}</div></div></div>
  {% endfor %}
  <div class="darkbox" style="margin-top:24px"><div class="lab">A final note</div>
    {% for p in c.final_note %}<p>{{ p }}</p>{% endfor %}</div>
</div>
""")


def to_pdf(plan: dict, out_path: str) -> str:
    html = TEMPLATE.render(css=CSS, c=_safe(plan))
    html_path = out_path.replace(".pdf", ".html")
    open(html_path, "w").write(html)
    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(out_path)
        return out_path
    except Exception as e:
        return html_path + f"   (PDF skipped: {e})"


def _safe(d):
    d = dict(d or {})
    d.setdefault("cover", {})
    for k, v in {"student": "Student", "grade": "", "prepared": "", "family": "", "date": ""}.items():
        d["cover"].setdefault(k, v)
    d.setdefault("profile", {"title": "", "lead": "", "blocks": [], "flags": ""})
    for key in ("target", "stretch"):
        d.setdefault(key, {"lead": "", "card": {}, "bands": {"intro": "", "bands": []}})
        d[key].setdefault("card", {})
        for f in ("label", "title", "subtitle", "within_reach", "toughest", "takeaway"):
            d[key]["card"].setdefault(f, "")
        for f in ("stats", "credentials"):
            d[key]["card"].setdefault(f, [])
        d[key].setdefault("bands", {"intro": "", "bands": []})
    d.setdefault("course", {"lead": "", "target_gpa": "", "stretch_gpa": "", "target_bullets": [],
                            "stretch_bullets": [], "table": [], "note": ""})
    d.setdefault("roadmap", {"title": "", "lead": "", "stages": [], "grades": []})
    d.setdefault("this_year", {"title": "", "lead": "", "cards": []})
    d.setdefault("parent_actions", {"lead": "", "items": []})
    d.setdefault("final_note", [])
    return d
