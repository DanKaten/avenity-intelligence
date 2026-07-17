from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROSPECTS = [
    ("Dempsey Family Electric of Texas", "electrical", "dempsey-family-electric"),
    ("L & E Electrical Services", "electrical", "l-e-electrical-services"),
    ("IF Houston", "flooring", "if-houston"),
    ("Grand Floors & More", "flooring", "grand-floors-and-more"),
    ("Cutting Edge Flooring Services", "flooring", "cutting-edge-flooring-services"),
    ("Air Innovations LLC", "hvac", "air-innovations"),
    ("Avalon Insurance Agency", "insurance", "avalon-insurance-agency"),
    ("AAIGOT Insurance Agency", "insurance", "aaigot-insurance-agency"),
    ("PJS of Houston", "janitorial", "pjs-of-houston"),
    ("Atlas Janitorial Services", "janitorial", "atlas-janitorial-services"),
    ("Fernandez Landscapes", "landscaping", "fernandez-landscapes"),
    ("Evergreen Lawn Care TX", "landscaping", "evergreen-lawn-care-tx"),
    ("Integrity First Lending", "mortgage", "integrity-first-lending"),
    ("Wood Group Mortgage", "mortgage", "wood-group-mortgage"),
    ("DMR Mortgage", "mortgage", "dmr-mortgage"),
    ("911 Houston Movers", "moving", "911-houston-movers"),
    ("MET Plumbing", "plumbing", "met-plumbing"),
    ("Moss Roofing Houston", "roofing", "moss-roofing-houston"),
    ("Infinity Roofing", "roofing", "infinity-roofing"),
    ("Bluebonnet Exteriors HTX", "roofing", "bluebonnet-exteriors-htx"),
]


def parse_report(category: str):
    path = ROOT / "articles" / f"2026-06-26-houston-{category}.md"
    text = path.read_text(encoding="utf-8")
    rows = []
    pattern = re.compile(
        r"### \d+\. (?P<name>.+?)\n"
        r"\*\*Website:\*\* (?P<website>[^|]+?) \| \*\*AI Visibility Score:.*?\((?P<score>\d+)/100\)\*\*"
        r"(?P<body>.*?)(?=\n---\n\n### |\n---\n\n## Summary)", re.S)
    for match in pattern.finditer(text):
        body = match.group("body")
        dims = {}
        for label, key in [
            ("Entity Clarity", "entity"),
            ("Schema & Structure", "schema"),
            ("Authority & Reviews", "authority"),
            ("Content Depth", "content"),
        ]:
            found = re.search(rf"{re.escape(label)} \((\d+)/25\)", body)
            dims[key] = int(found.group(1)) if found else 0
        opp = re.search(r"\*\*Highest-impact opportunity:\*\* (.+)", body)
        rows.append({
            "name": match.group("name").strip(),
            "website": match.group("website").strip(),
            "score": int(match.group("score")),
            **dims,
            "opportunity": opp.group(1).strip() if opp else "Strengthen the clearest local AI-search signal.",
        })
    return rows


def signal(value: int, total=False):
    cutoff_good, cutoff_low = (70, 55) if total else (19, 14)
    cls = "good" if value >= cutoff_good else ("low" if value < cutoff_low else "")
    return f'<span class="signal {cls}">{value}</span>'


def build_page(name: str, category: str, slug: str):
    market = parse_report(category)
    target = next(row for row in market if row["name"] == name)
    average = round(sum(row["score"] for row in market) / len(market))
    top = max(row["score"] for row in market)
    table_rows = []
    for row in market:
        cls = ' class="target-row"' if row["name"] == name else ""
        table_rows.append(
            f"<tr{cls}><td>{html.escape(row['name'])}</td>"
            f"<td>{signal(row['entity'])}</td><td>{signal(row['schema'])}</td>"
            f"<td>{signal(row['authority'])}</td><td>{signal(row['content'])}</td>"
            f"<td><strong>{signal(row['score'], True)}</strong></td></tr>"
        )
    display_category = category.upper() if category == "hvac" else category.title()
    query = f"{name} · {target['website']} · {display_category} · Houston, Texas"
    gap = target["opportunity"]
    narration = [
        f"I ran {name} through the Houston {display_category} competitor report using the business name, website, primary service, and city. Here is the full market snapshot.",
        f"{name} scored {target['score']} for AI search visibility. The Houston market average is {average}, and the top score is {top}. This measures public AI search signals only, not business quality.",
        f"The clearest opportunity in the report is this: {gap}",
        "G M B Optimizer helps keep the Google Business Profile active through profile optimization, review requests and replies, scheduled posts, photo and question management, and progress reporting.",
        "G M B Optimizer is 350 dollars per month, with no setup fee and no long-term contract. Use the booking link in the email to schedule a short call with Avenity.",
    ]
    page = TEMPLATE.format(
        title=html.escape(name), category=html.escape(display_category), website=html.escape(target["website"]),
        score=target["score"], average=average, top=top, gap=html.escape(gap),
        rows="".join(table_rows), query=json.dumps(query), narrations=json.dumps(narration),
    )
    out = ROOT / "proofs" / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")


TEMPLATE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — AI Visibility Walkthrough</title>
<style>
:root{{--navy:#10213d;--blue:#2563eb;--ink:#18243a;--muted:#647189;--line:#dbe3ef;--green:#20a66a;--amber:#efb52f;--orange:#e77b43}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 90% 0,#d9e8ff,#f5f8fc 42%,#eaf0f7);font:16px/1.45 Inter,system-ui,sans-serif;color:var(--ink)}}
.shell{{max-width:1160px;margin:auto;padding:24px}}header{{display:flex;justify-content:space-between;gap:20px;margin-bottom:18px}}.brand{{font-weight:900;color:var(--navy)}}.brand span,.eyebrow{{color:var(--blue)}}.stamp{{text-align:right;color:var(--muted);font-size:13px}}
.player{{background:#fff;border:1px solid #cfd9e7;border-radius:24px;overflow:hidden;box-shadow:0 25px 70px #19365a28}}.stage{{min-height:690px;padding:38px 48px;display:grid;align-items:center}}.scene{{display:none;animation:in .35s ease}}.scene.active{{display:block}}@keyframes in{{from{{opacity:0;transform:translateY(8px)}}}}
.eyebrow{{font-size:12px;text-transform:uppercase;font-weight:900;letter-spacing:.11em}}h1,h2{{color:var(--navy);letter-spacing:-.04em;line-height:1.03}}h2{{font-size:clamp(30px,4vw,50px);margin:8px 0 16px}}p{{font-size:19px;color:var(--muted);max-width:850px}}
.search{{border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 12px 32px #10213d18}}.top{{padding:12px 16px;background:#f4f7fb;border-bottom:1px solid var(--line);font-size:12px;font-weight:800;color:var(--muted)}}.body{{padding:18px}}.query{{min-height:54px;padding:14px 16px;border:2px solid #9bb7eb;border-radius:13px;font-size:18px;font-weight:750;color:var(--navy)}}.status{{margin:10px 2px;color:var(--muted);font-size:13px}}.results{{display:none;margin-top:12px}}.results.show{{display:block;animation:in .35s ease}}
.wrap{{overflow:auto;max-height:390px}}table{{width:100%;border-collapse:collapse;font-size:12px;min-width:710px}}th,td{{padding:7px 8px;border-bottom:1px solid #e3e9f1;text-align:center}}th:first-child,td:first-child{{text-align:left}}th{{position:sticky;top:0;background:#fff;color:var(--muted);font-size:10px;text-transform:uppercase}}tr.target-row{{background:#fff0e3;font-weight:850}}
.signal{{display:inline-flex;align-items:center;gap:4px}}.signal:before{{content:'';width:9px;height:9px;border-radius:50%;background:var(--amber)}}.signal.good:before{{background:var(--green)}}.signal.low:before{{background:var(--orange)}}
.scores,.features{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:22px}}.score,.card{{padding:18px;border:1px solid var(--line);border-radius:15px;background:#f7faff}}.score{{text-align:center}}.score strong{{display:block;font-size:32px;color:var(--navy)}}.score.target{{background:#fff3e8;border:2px solid #ee9b55}}.gap{{padding:24px;border:2px solid #79c7a9;background:#f3fff9;border-radius:18px;font-size:23px;color:#116247;font-weight:750}}
.features{{grid-template-columns:repeat(2,1fr)}}.card strong{{display:block;color:var(--navy);margin-bottom:5px}}.card span{{font-size:13px;color:var(--muted)}}.offer{{font-size:26px;font-weight:900;color:var(--navy);margin-top:24px}}.note{{margin-top:20px;padding:14px 16px;background:#eaf2ff;border-radius:12px;font-weight:800;color:var(--navy)}}
.controls{{border-top:1px solid var(--line);padding:16px 22px;background:#fbfcff}}.progress{{height:6px;background:#e5ebf4;border-radius:9px;overflow:hidden}}#fill{{height:100%;width:0;background:var(--blue)}}.bar{{display:flex;align-items:center;gap:12px;margin-top:14px}}button{{border:0;border-radius:10px;padding:11px 16px;font-weight:850;cursor:pointer;background:var(--navy);color:#fff}}button.secondary{{background:#e7edf5;color:var(--navy)}}#time{{margin-left:auto;color:var(--muted);font-size:13px}}footer{{text-align:center;color:var(--muted);font-size:12px;margin-top:16px}}
@media(max-width:720px){{.stage{{padding:28px 20px;min-height:720px}}.features,.scores{{grid-template-columns:1fr}}header{{align-items:flex-start}}}}
</style></head><body><div class="shell"><header><div class="brand">Avenity Business Solutions <span>× Get More Customers™</span></div><div class="stamp">Personalized for {title}<br>Houston snapshot · July 17, 2026</div></header>
<main class="player"><div class="stage">
<section class="scene active"><div class="eyebrow">Recorded competitor search · Houston</div><h2>See {title} in the full {category} snapshot</h2><div class="search"><div class="top">AI Authority Competitor Comparison · business name + website + primary service + city</div><div class="body"><div class="query" id="query"></div><div class="status" id="status">Press play to run the recorded search.</div><div class="results" id="results"><div class="wrap"><table><thead><tr><th>Business</th><th>Entity</th><th>Structure</th><th>Authority</th><th>Content</th><th>Overall</th></tr></thead><tbody>{rows}</tbody></table></div></div></div></div></section>
<section class="scene"><div class="eyebrow">AI-search-specific market position</div><h2>The public signals show exactly where attention can go.</h2><div class="scores"><div class="score"><strong>{top}</strong>Top score</div><div class="score"><strong>{average}</strong>Market average</div><div class="score target"><strong>{score}</strong>{title}</div></div><p>This is a technical visibility snapshot, not a rating of service quality or customer satisfaction.</p></section>
<section class="scene"><div class="eyebrow">Highest-impact opportunity</div><h2>One clear place to strengthen first</h2><div class="gap">{gap}</div></section>
<section class="scene"><div class="eyebrow">GMB Optimizer · automated local visibility</div><h2>What GMB Optimizer handles</h2><div class="features"><div class="card"><strong>Profile optimization</strong><span>Services, descriptions, attributes and business details.</span></div><div class="card"><strong>Review management</strong><span>Review requests, follow-ups and AI-assisted replies.</span></div><div class="card"><strong>Automatic posts</strong><span>Creates, schedules and publishes optimized Google posts.</span></div><div class="card"><strong>Photos and Q&amp;A</strong><span>Optimizes images and keeps common questions answered.</span></div><div class="card"><strong>Multi-channel content</strong><span>Google, Facebook, Instagram and YouTube.</span></div><div class="card"><strong>Progress reporting</strong><span>Heatmaps, completed actions and ranking visibility.</span></div></div></section>
<section class="scene"><div class="eyebrow">Simple next step</div><h2>Put GMB Optimizer to work for {title}.</h2><div class="offer">$350/month · No setup fee · Cancel anytime</div><div class="note">Click the booking link in the email to schedule a call with Avenity.</div></section>
</div><div class="controls"><div class="progress"><div id="fill"></div></div><div class="bar"><button id="play">▶ Play walkthrough</button><button id="restart" class="secondary">↻ Restart</button><span id="time">0:00 / 1:05</span></div></div></main>
<footer>Dated public-search snapshot. Results can vary by platform, location, timing and personalization. Scores measure AI-search signals only, not business quality. Prepared by Avenity Business Solutions.</footer></div>
<script>
const scenes=[...document.querySelectorAll('.scene')],dur=[15,13,12,15,10],texts={narrations},queryText={query};let i=0,elapsed=0,timer=null,playing=false;
const q=document.getElementById('query'),status=document.getElementById('status'),results=document.getElementById('results'),play=document.getElementById('play'),fill=document.getElementById('fill'),time=document.getElementById('time');
function fmt(s){{return Math.floor(s/60)+':'+String(Math.floor(s%60)).padStart(2,'0')}}function voice(){{if(!speechSynthesis)return;speechSynthesis.cancel();let u=new SpeechSynthesisUtterance(texts[i]);let vs=speechSynthesis.getVoices();u.voice=vs.find(v=>/Samantha|Jenny|Aria|Guy|Natural/i.test(v.name))||vs.find(v=>v.lang.startsWith('en'))||null;u.rate=.98;u.pitch=.96;speechSynthesis.speak(u)}}
function render(){{scenes.forEach((s,x)=>s.classList.toggle('active',x===i));fill.style.width=(elapsed/65*100)+'%';time.textContent=fmt(elapsed)+' / 1:05';play.textContent=playing?'❚❚ Pause':'▶ Play walkthrough'}}
function replay(){{q.textContent='';results.classList.remove('show');status.textContent='Entering the report criteria…';[...queryText].forEach((c,x)=>setTimeout(()=>q.textContent+=c,x*24));setTimeout(()=>status.textContent='Comparing the Houston {category} report…',queryText.length*24+200);setTimeout(()=>{{status.textContent='Competitive snapshot returned · July 17, 2026';results.classList.add('show')}},queryText.length*24+900)}}
function start(){{if(elapsed>=65)restart();playing=true;if(i===0&&elapsed<1)replay();voice();clearInterval(timer);timer=setInterval(()=>{{elapsed+=.1;let rem=elapsed,next=0;while(next<dur.length-1&&rem>=dur[next]){{rem-=dur[next];next++}}if(next!==i){{i=next;voice()}}if(elapsed>=65)pause();render()}},100);render()}}function pause(){{playing=false;clearInterval(timer);timer=null;if(speechSynthesis)speechSynthesis.cancel();render()}}function restart(){{pause();i=0;elapsed=0;q.textContent='';results.classList.remove('show');status.textContent='Press play to run the recorded search.';render()}}
play.onclick=()=>playing?pause():start();document.getElementById('restart').onclick=restart;render();
</script></body></html>'''


for prospect in PROSPECTS:
    build_page(*prospect)

print(f"Generated {len(PROSPECTS)} unique proof pages")
