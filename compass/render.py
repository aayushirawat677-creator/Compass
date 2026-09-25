"""
StrategicPlan JSON -> HTML -> PDF, in the Compass design language (matches the v10 look):
dark cover, cream pages, gold section labels, serif headings, green/purple projected
stat-cards, 4-column tier bands, a roadmap timeline, recommendation cards, numbered
parent actions, and a dark final note. Data-driven from the `plan` dict — see the schema
used in neerav_trial.py / mockdata.py.
"""
import re
import os
from jinja2 import Template

CSS = r"""
@page { size: letter; margin: 0; }
@page content { margin: 40px 56px 40px; }
* { box-sizing: border-box; }
:root{
  --ink:#1c2a21; --cream:#f4f1e8; --card:#fbfaf4; --gold:#a5852f; --gold2:#9c7b2e;
  --muted:#6f7469; --line:#e0dccb; --green:#5c6b3d; --greenbg:#e7ecd7;
  --purple:#5b4a86; --purplebg:#e8e4f1; --tan:#efe8d6;
}
body{ margin:0; color:#20281f; font-family:'Inter','Helvetica Neue',Arial,sans-serif; font-size:10.45px; line-height:1.4; }
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
h2.sec{ font-size:30px; margin:0 0 6px; }
.lead{ color:var(--muted); font-style:italic; font-size:12.5px; line-height:1.38; max-width:82%; margin-bottom:10px; }
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
.stats{ display:flex; flex-wrap:wrap; gap:6px; margin:7px 0; }
.stat{ flex:1 1 30%; border:1px solid var(--line); border-radius:5px; padding:6px 9px; background:#fff; }
.stat .k{ color:var(--muted); letter-spacing:.1em; font-size:8.5px; text-transform:uppercase; }
.stat .v{ font-size:14.5px; font-weight:700; line-height:1.25; } .stat .v small{ font-weight:400; color:var(--muted); font-size:9.3px; }
.cred{ margin-top:8px; } .cred .lab{ color:var(--gold2); letter-spacing:.12em; font-size:9px; font-weight:700; text-transform:uppercase; margin-bottom:4px; }
.cred li{ list-style:none; padding-left:14px; position:relative; margin:2.5px 0; }
.cred li:before{ content:'▪'; position:absolute; left:0; color:var(--green); }
.tracks{ display:flex; flex-wrap:wrap; gap:3px 14px; }
/* Two plans, side by side, in the colours the document already uses for them. [#80] */
.planrow{ display:flex; gap:10px; margin:12px 0 4px; }
.plan{ flex:1 1 50%; border:1px solid var(--line); border-radius:6px; padding:9px 11px 10px; }
.plan.p1{ background:#f4f5f0; border-left:3px solid #5c6b3d; }
.plan.p2{ background:#f3f1f7; border-left:3px solid #5b4a86; }
.plan .ph{ font-size:9px; font-weight:700; letter-spacing:.13em; text-transform:uppercase; margin-bottom:6px; }
.plan.p1 .ph{ color:#5c6b3d; } .plan.p2 .ph{ color:#5b4a86; }
.pfigs{ display:flex; gap:5px; margin-bottom:6px; }
.pfig{ flex:1 1 33%; background:#fff; border-radius:4px; padding:5px 7px; }
.pfig .fk{ display:block; color:var(--muted); font-size:7.6px; letter-spacing:.08em; text-transform:uppercase; }
.pfig .fv{ display:block; font-weight:700; font-size:11.5px; margin-top:1px; }
.plan .pline{ font-size:9.3px; line-height:1.45; color:var(--ink); }
.shared{ float:right; color:var(--muted); font-weight:400; letter-spacing:.04em; text-transform:none; font-size:8.6px; font-style:italic; }
.diffbox{ margin-top:13px; border:1px solid #d8d2e4; background:#f7f5fb; border-radius:6px; padding:9px 12px 10px; }
.diffbox .lab{ color:#5b4a86; letter-spacing:.11em; font-size:8.8px; font-weight:700; text-transform:uppercase; margin-bottom:4px; }
.diffbox p{ margin:0; }
/* Decisions: a when-column and a body-column, so the moments line up down the page. */
.cdec{ display:flex; gap:11px; padding:5px 0; border-top:1px solid var(--line); }
.cdec:first-of-type{ border-top:0; }
.cdw{ color:var(--gold2); font-size:8.2px; font-weight:700; letter-spacing:.09em; text-transform:uppercase; min-width:104px; padding-top:2px; }
.cdhd{ font-weight:700; margin-bottom:1px; }
.cdk{ margin-top:3px; font-size:9.1px; color:var(--muted); }
.cdk span{ color:var(--gold2); letter-spacing:.09em; text-transform:uppercase; font-size:8px; font-weight:700; margin-right:5px; }
.cblk{ margin-top:14px; border-top:1px solid var(--line); padding-top:8px; }
.cblk .lab{ color:var(--gold2); letter-spacing:.12em; font-size:9px; font-weight:700; text-transform:uppercase; margin-bottom:5px; }
.trk{ flex:1 1 46%; font-size:9.6px; display:flex; gap:6px; }
.trk .tk{ color:var(--muted); min-width:74px; letter-spacing:.04em; text-transform:uppercase; font-size:8.6px; padding-top:1px; }
.reachrow{ display:flex; gap:16px; margin-top:8px; font-size:10px; }
.oddsrow{ display:flex; gap:22px; margin-top:10px; border-top:1px solid var(--line); padding-top:8px; }
.oddsrow > div{ flex:1 1 50%; }
.ot{ font-size:9.6px; margin:2.5px 0; line-height:1.4; }
.oddsrow .lab{ color:var(--gold2); letter-spacing:.12em; font-size:9px; font-weight:700; text-transform:uppercase; margin-bottom:4px; }
.ot .otn{ font-weight:700; color:#3a463a; }
.ot .otr{ color:var(--gold2); font-weight:700; }
.ot .otc{ color:var(--ink); }
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
/* current year: the semester is the container, named once */
.termblock{ margin:9px 0 2px; }
.termblock + .termblock{ border-top:1px solid var(--line); padding-top:8px; }
.termhead{ display:flex; align-items:baseline; gap:8px; margin-bottom:5px; }
.termhead .tname{ font-size:14px; font-weight:700; color:#182117; }
.termhead .tspan{ color:var(--muted); letter-spacing:.12em; font-size:8.5px; text-transform:uppercase; }
.termhead .ttag{ margin-left:auto; color:var(--gold2); font-style:italic; font-size:10.5px; }
.catchip{ font-size:7.5px; letter-spacing:.1em; text-transform:uppercase; padding:1px 6px; border-radius:3px;
  margin-right:7px; vertical-align:1px; background:#e6e3d6; color:#4b4a3a; }
.catchip.debate{ background:var(--purplebg); color:var(--purple); }
.catchip.venture{ background:#f3e9cf; color:#8a6a1c; }
.catchip.service{ background:var(--greenbg); color:var(--green); }
.catchip.academics{ background:#e2e5dd; color:#3a463a; }
.catchip.summer{ background:#f6ecd8; color:#96762a; }
.catchip.schedule{ background:#eceadf; color:#6a6450; }
.catchip.other{ background:#eceadf; color:#6a6450; }
/* profile: where each existing thread can reach */
.threads{ border:1px solid var(--line); border-radius:5px; padding:11px 14px; margin:12px 0 4px; background:var(--card); }
.thlab{ color:var(--gold2); letter-spacing:.14em; font-size:9.5px; font-weight:700; text-transform:uppercase; margin-bottom:6px; }
.throw{ display:flex; align-items:baseline; gap:9px; margin:5px 0 0; }
.throw .thname{ font-weight:700; }
.throw .threach{ color:var(--muted); font-size:10px; }
.throw .thdisp{ margin-left:auto; color:var(--green); font-style:italic; font-size:10px; white-space:nowrap; }
.thnote{ font-size:9.5px; color:var(--muted); font-style:italic; margin:0 0 3px 46px; }
.box.ask{ background:#efeaf4; border-left-color:var(--purple); }
.box.ask .lab{ color:var(--purple); }
.grow.again .t{ font-weight:600; color:#41493d; }
.growbare{ margin:3px 0 3px 14px; padding-left:11px; position:relative; }
.growbare:before{ content:'\00b7'; position:absolute; left:0; color:var(--gold2); font-weight:700; }
.growbare.stretchgoal{ border-left:3px solid var(--purple); padding-left:9px; margin-left:11px; background:rgba(91,74,134,.045); }
.contpill{ font-size:7.5px; letter-spacing:.09em; text-transform:uppercase; color:var(--muted);
  border:1px solid var(--line); border-radius:8px; padding:1px 6px; margin-left:7px; vertical-align:2px; }
.subtask{ margin:2px 0 2px 16px; padding-left:11px; position:relative; }
.subtask:before{ content:'·'; position:absolute; left:0; color:var(--gold2); font-weight:700; }

/* recommendation cards */
.reccard{ border:1px solid var(--line); border-left:4px solid var(--gold); border-radius:5px; background:var(--card); padding:9px 12px; margin:7px 0; }
.catpill{ background:var(--ink); color:#efeadc; border-radius:3px; padding:2px 7px; font-size:8.5px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.catpill.debate{ background:var(--purple); } .catpill.venture{ background:var(--gold); color:#241d07; }
.catpill.service{ background:var(--green); } .catpill.academics{ background:#3a463a; }
.actpill{ background:#e7e0cb; color:#6a5a2a; border-radius:3px; padding:2px 7px; font-size:8px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.reccard h4{ display:inline; font-size:13.5px; margin:0 5px; }
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
    {# NO COURSES ON THE CARD. [#78] They had a page, I merged them here in #76, and that
       was wrong in a way the page count hid: this card PROJECTS — it is what he looks
       like in senior year if the plan is carried out. A course target is a DECISION the
       family makes at registration. Putting a decision inside a projection tells a parent
       their son's schedule is already settled. Courses went back to their own page. #}
    <div class="cred"><div class="lab">What his application will show</div><ul>
      {% for cr in card.credentials %}<li><strong>{{ cr.h }}</strong> {{ cr.t }}</li>{% endfor %}</ul></div>
    {# ONE ODDS BLOCK, TWO TIERS A SIDE. [#78] This was three things saying the same thing:
       a prose sentence about what is within reach, a prose sentence about the toughest
       reaches, and a band strip underneath naming the same schools again with percentages.
       Now: two columns, two labelled lines each, the schools named in full. #}
    {% if card.odds %}
    <div class="oddsrow">
      {% for col in card.odds %}
      <div><div class="lab">{{ '▲' if loop.first else '★' }} {{ col.head }}</div>
        {% for t in col.tiers %}<div class="ot"><span class="otn">{{ t.name }}</span> <span class="otr">{{ t.range }}</span> <span class="otc">{{ t.colleges }}</span></div>{% endfor %}
      </div>{% endfor %}
    </div>
    {% endif %}
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
  {% if c.profile.family_questions %}
  <div class="box ask"><div class="lab">We'd like your view before we decide</div>
    {% for q in c.profile.family_questions %}<p class="small" style="margin:4px 0"><strong>{{ q.about }}</strong> — {{ q.question }}</p>{% endfor %}
  </div>
  {% endif %}
  <div class="box"><div class="lab">Flags to confirm</div><p class="small">{{ c.profile.flags }}</p></div>
</div>

<!-- 02 TARGET PLAN -->
<div class="page">
  <div class="rhead">Compass · Strategic Plan · {{ c.cover.student }} · Grade {{ c.cover.grade }}</div>
  <div class="slabel">02 · The Target Plan</div>
  <h2 class="sec">The Target plan.</h2>
  <div class="lead">{{ c.target.lead }}</div>
  {{ pcard(c.target.card, 'g') }}
</div>

<!-- 03 STRETCH PLAN -->
<div class="page">
  <div class="rhead">Compass · Strategic Plan · {{ c.cover.student }} · Grade {{ c.cover.grade }}</div>
  <div class="slabel">03 · The Stretch Plan</div>
  <h2 class="sec">The Stretch plan.</h2>
  <div class="lead">{{ c.stretch.lead }}</div>
  {{ pcard(c.stretch.card, 'p') }}
</div>

<!-- 04 COURSES AND GRADES -->
{# A PAGE OF ITS OWN, AND NOT A PROJECTION. [#78] The card says what he WILL LOOK LIKE;
   a course target is something the family DECIDES, at a registration desk, on a date.

   THE SHAPE OF THIS PAGE ANSWERS A QUESTION THE OLD TABLE ANSWERED BADLY. [#80] Aayushi
   wants the two plans told apart at a glance. The first version did that with a
   Target-against-Stretch table whose stretch column said "Same." five times out of six —
   the distinction drawn by repeating the word for "no distinction". The second version
   buried the difference in a paragraph at the foot, where it was honest and invisible.

   So: the two plans sit side by side AT THE TOP, in their own colours, with the three
   academic figures each. A reader sees in one second that the figures are identical and
   that one line differs. Then ONE shared subject grid, labelled as shared, because a
   column of "Same." is not information — the label carries it. Then the difference
   itself, once, in a box of its own. Then what to do about it.  #}
<div class="page">
  <div class="rhead">Compass · Strategic Plan · {{ c.cover.student }} · Grade {{ c.cover.grade }}</div>
  <div class="slabel">04 · Courses and Grades</div>
  <h2 class="sec">{{ c.course.title }}</h2>
  <div class="lead">{{ c.course.lead }}</div>

  {% if c.course.plans %}
  <div class="planrow">
    {% for pl in c.course.plans %}
    <div class="plan {{ 'p2' if loop.last else 'p1' }}">
      <div class="ph">{{ pl.name }}</div>
      <div class="pfigs">
        {% for fg in pl.figures %}<div class="pfig"><span class="fk">{{ fg.k }}</span><span class="fv">{{ fg.v }}</span></div>{% endfor %}
      </div>
      <div class="pline">{{ pl.line }}</div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if c.course.tracks %}
  <div class="cblk">
    <div class="lab">Where to aim, subject by subject{% if c.course.tracks_note %}<span class="shared">{{ c.course.tracks_note }}</span>{% endif %}</div>
    <div class="tracks">
      {% for t in c.course.tracks %}<div class="trk"><span class="tk">{{ t.track }}</span><span>{{ t.target }}</span></div>{% endfor %}
    </div>
  </div>
  {% endif %}

  {% if c.course.difference %}
  <div class="diffbox">
    <div class="lab">{{ c.course.difference_head or 'Where the two plans differ' }}</div>
    <p class="small">{{ c.course.difference }}</p>
  </div>
  {% endif %}

  {% if c.course.decisions %}
  <div class="cblk"><div class="lab">What to do, and when</div>
    {% for d in c.course.decisions %}
    <div class="cdec">
      <div class="cdw">{{ d.when }}</div>
      <div><div class="cdhd">{{ d.head }}</div>
        <div class="small">{{ d.body }}</div>
        {% if d.keeps_open %}<div class="cdk"><span>Keeps open</span> {{ d.keeps_open }}</div>{% endif %}
      </div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if c.course.note %}<div class="darkbox" style="margin-top:14px"><div class="lab">The one thing to hold on to</div>
    <p>{{ c.course.note }}</p></div>{% endif %}
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
      {% if g.terms %}
        {# CURRENT YEAR — the semester is the container, the goals sit inside it. The
           term is stated once as a heading instead of repeated on every task row. #}
        {% set seen = namespace(g=[]) %}
        {% for tm in g.terms %}
          <div class="termblock">
            <div class="termhead"><span class="tname serif">{{ tm.term }}</span>{% if tm.span %}<span class="tspan">{{ tm.span }}</span>{% endif %}{% if tm.tag %}<span class="ttag">{{ tm.tag }}</span>{% endif %}</div>
            {% for row in tm.goals %}
              {# A goal that runs across terms states itself ONCE, in the term it starts.
                 On later terms it carries its short form and no why-now line — the term
                 block is what has changed, not the reasoning. [#57] #}
              {% set gk = (row.goal or row.title) %}
              {% set again = gk in seen.g %}
              {% if not again %}{% set _ = seen.g.append(gk) %}{% endif %}
              {# A REPEAT CARRYING ONE TASK NEEDS NO HEADER. [#75] Every goal entry in the
                 last run held exactly one task, so the roadmap was 56 bold titles each
                 wrapping a single bullet, 35 of them stamped "continued" — a header as
                 tall as its content, and two pages of it. The goal was already stated in
                 the term it began; on a later term the task row plus its category chip
                 says everything. Nothing the plan says is lost. #}
              {% set bare = again and (row.tasks|length) == 1 %}
              {% if bare %}
                <div class="growbare {{ 'stretchgoal' if row.track == 'stretch' else '' }}">
                  {% if row.cat %}<span class="catchip {{ row.cat_class }}">{{ row.cat }}</span>{% endif %}<span>{{ (row.tasks[0].text or row.tasks[0]) }}</span>{% if row.tasks[0].track == 'stretch' and row.track != 'stretch' %}<span class="trackpill s">stretch</span>{% endif %}
                </div>
              {% else %}
              <div class="grow {{ 'stretchgoal' if row.track == 'stretch' else '' }}{{ ' again' if again else '' }}">
                <div class="t">{% if row.cat %}<span class="catchip {{ row.cat_class }}">{{ row.cat }}</span>{% endif %}{{ (row.goal_short or gk.split(',')[0].split(' - ')[0]) if again else gk }}{% if again %}<span class="contpill">continued</span>{% elif row.track == 'stretch' %}<span class="trackpill s">stretch</span>{% endif %}</div>
                {% for t in row.tasks %}<div class="subtask">{{ t.text or t }}{% if t.track == 'stretch' and row.track != 'stretch' %}<span class="trackpill s">stretch</span>{% endif %}</div>{% endfor %}
              </div>
              {% endif %}
            {% endfor %}
          </div>
        {% endfor %}
      {% else %}
        {% for row in (g.goals or g.rows) %}
          <div class="grow {{ 'stretchgoal' if row.track == 'stretch' else '' }}">
            <div class="t">{{ row.goal or row.title }}{% if row.track == 'stretch' %}<span class="trackpill s">stretch</span>{% endif %}</div>
            {% for t in row.tasks %}<div class="task"><span class="termpill">{{ t.term }}</span><span>{{ t.text }}{% if t.track == 'stretch' and row.track != 'stretch' %}<span class="trackpill s">stretch</span>{% endif %}</span></div>{% endfor %}
          </div>
        {% endfor %}
      {% endif %}
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


def _odds(cols):
    """The odds block: two columns, two tiers each, every school named in full. [#78][#77]

    Joining is where a school's name gets broken. A writer told to comma-join a list
    holding "University of California, Berkeley" and "University of California, Los
    Angeles" printed "University of California, University of California" — it dropped
    each campus so its own separator stayed unambiguous, and the block then named the
    same school twice and no campus at all. A name that CONTAINS the separator cannot be
    joined by it, so the schema asks for a list, this joins it with a middot, and a
    string that arrives anyway is passed through rather than re-split. Splitting on the
    comma is the bug that caused this.
    """
    out = []
    for col in (cols or []):
        col = dict(col or {})
        tiers = []
        for t in (col.get("tiers") or []):
            t = dict(t or {})
            c = t.get("colleges")
            if isinstance(c, (list, tuple)):
                names, seen = [], set()
                for one in c:
                    n = (one.get("name") if isinstance(one, dict) else str(one)).strip()
                    if n and n.lower() not in seen:
                        seen.add(n.lower())
                        names.append(n)
                t["colleges"] = " · ".join(names)
            else:
                t["colleges"] = str(c or "")
            tiers.append(t)
        col["tiers"] = tiers
        out.append(col)
    return out


def _safe(d):
    d = dict(d or {})
    d.setdefault("cover", {})
    for k, v in {"student": "Student", "grade": "", "prepared": "", "family": "", "date": ""}.items():
        d["cover"].setdefault(k, v)
    # The template supplies the word "Grade"; a writer that also supplies it printed
    # "Grade Grade 8" in every running header. Normalise rather than forbid. [#56]
    d["cover"]["grade"] = re.sub(r"^\s*grade\s+", "", str(d["cover"]["grade"]), flags=re.I)
    d.setdefault("profile", {"title": "", "lead": "", "blocks": [], "flags": ""})
    for key in ("target", "stretch"):
        d.setdefault(key, {"lead": "", "card": {}, "bands": {"intro": "", "bands": []}})
        d[key].setdefault("card", {})
        for f in ("label", "title", "subtitle", "takeaway"):
            d[key]["card"].setdefault(f, "")
        for f in ("stats", "credentials", "odds"):
            d[key]["card"].setdefault(f, [])
        d[key]["card"]["odds"] = _odds(d[key]["card"].get("odds"))
        # The card no longer carries courses. [#78]
        d[key]["card"].pop("academics", None)
    d.setdefault("course", {})
    for f in ("title", "lead", "difference", "difference_head", "tracks_note", "note"):
        d["course"].setdefault(f, "")
    for f in ("decisions", "tracks", "plans"):
        d["course"].setdefault(f, [])
    d.setdefault("roadmap", {"title": "", "lead": "", "stages": [], "grades": []})
    d.setdefault("this_year", {"title": "", "lead": "", "cards": []})
    d.setdefault("parent_actions", {"lead": "", "items": []})
    d.setdefault("final_note", [])
    return d
