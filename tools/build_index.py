# -*- coding: utf-8 -*-
"""수업 홈 index.html 생성 — 챕터 폴더를 훑어 메뉴를 자동으로 만든다.

카드에 걸리는 것 (앞 두 자리 숫자로 짝을 찾는다)
  🕹️ 소스 실행기 / 🔧 조립 순서기   NN장_*_소스실행기.html · NN장_*_조립순서기.html  (앰버)
  🗣️ 수업 대본                      NN장_*_수업진행대본.html  (초록)
  📖 쉬운 설명서                    NN장_*_아주쉬운설명서.html
  📺 해설 영상 · 🎬 실습 영상 · 📄 교재 · 💻 실습코드
"""
import os, glob, io, sys, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")

def g(pattern_dir, pat):
    """대괄호가 든 경로를 안전하게 glob."""
    return glob.glob(os.path.join(glob.escape(pattern_dir), pat))

ROOT = r"G:/내 드라이브/2026년/올인원_사물"
KIT = os.path.join(ROOT, "ESP32 올인원 키트_교안")
VID = os.path.join(ROOT, "사물영상")
WEB_URL = "https://kwakjanghun.github.io/iot/"   # 학생 공유용 (build_web.py 가 올린다)

def url(p):
    """키트 폴더 기준 상대경로를 URL로."""
    return urllib.parse.quote(p.replace("\\", "/"))

def first(pat):
    hits = sorted(os.path.basename(x) for x in g(KIT, pat))
    return hits[0] if hits else None

chapters = []
for name in sorted(os.listdir(KIT)):
    d = os.path.join(KIT, name)
    if not os.path.isdir(d) or not name[:2].isdigit():
        continue
    num = name[:2]
    title = name[3:].strip()

    vids = glob.glob(os.path.join(VID, f"{num}_00_*통합_코드해설.mp4"))
    vids = [x for x in vids if "압축" not in os.path.basename(x)] or vids
    main_video = f"../사물영상/{os.path.basename(vids[0])}" if vids else None

    practice = sorted(os.path.basename(x)
                      for x in g(os.path.join(d, "실습영상"), "*.mp4"))
    pdfs = g(d, "*.pdf")
    pdf = f"{name}/{os.path.basename(pdfs[0])}" if pdfs else None

    runner = first(f"{num}장_*_소스실행기.html")
    kind = "소스 실행기"
    if not runner:
        runner = first(f"{num}장_*_조립순서기.html")
        kind = "조립 순서기"
    chapters.append(dict(num=num, title=title, folder=name, video=main_video,
                         practice=practice, pdf=pdf,
                         script=first(f"{num}장_*_수업진행대본.html"),
                         easy=first(f"{num}장_*_아주쉬운설명서.html"),
                         runner=runner, kind=kind if runner else None))

done = sum(1 for c in chapters if c["script"])
n_run = sum(1 for c in chapters if c["runner"])

cards = []
for c in chapters:
    links = []
    if c["runner"]:
        icon = "🔧" if c["kind"] == "조립 순서기" else "🕹️"
        links.append(f'<a class="lk run" href="{url(c["runner"])}">{icon} {c["kind"]}</a>')
    if c["script"]:
        links.append(f'<a class="lk main" href="{url(c["script"])}">🗣️ 수업 대본</a>')
    if c["easy"]:
        links.append(f'<a class="lk" href="{url(c["easy"])}">📖 쉬운 설명서</a>')
    if c["video"]:
        links.append(f'<a class="lk" href="{url(c["video"])}">📺 해설 영상</a>')
    if c["practice"]:
        links.append(f'<a class="lk" href="{url(c["folder"] + "/실습영상")}">🎬 실습 영상 {len(c["practice"])}</a>')
    if c["pdf"]:
        links.append(f'<a class="lk" href="{url(c["pdf"])}">📄 교재</a>')
    if os.path.isdir(os.path.join(KIT, c["folder"], "실습코드")):
        links.append(f'<a class="lk" href="{url(c["folder"] + "/실습코드")}">💻 실습코드</a>')

    # 왼쪽 띠: 대본+실행기 = 초록/앰버 반반, 실행기만 = 앰버, 대본만 = 초록, 없음 = 회색
    if c["script"] and c["runner"]:
        state, badge = "ready run2", ""
    elif c["script"]:
        state, badge = "ready", ""
    elif c["runner"]:
        state = "todo run"
        badge = f'<span class="soon" style="color:var(--amber)">{c["kind"]} 완성 · 대본 준비 중</span>'
    else:
        state, badge = "todo", '<span class="soon">대본 준비 중</span>'
    cards.append(f'''  <article class="card {state}">
    <div class="no">{c["num"]}</div>
    <h2>{c["title"]}</h2>
    {badge}
    <div class="links">{"".join(links)}</div>
  </article>''')

html = f'''<title>사물 인터넷과 센서 제어 수업</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@600&display=swap">
<style>
  :root{{
    --bg:#0B0F14; --panel:#141B25; --panel2:#0F141C; --line:#232D3B;
    --text:#E8EDF4; --muted:#93A1B5; --faint:#6B7A8E;
    --amber:#FFB03A; --amber-dim:#3A2C12; --green:#7BD88F;
    --disp:'Black Han Sans',sans-serif;
    --body:'Noto Sans KR','Apple SD Gothic Neo',sans-serif;
    --mono:'IBM Plex Mono','Consolas',monospace;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:var(--body);font-size:17px;
    padding:0 28px 80px;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:1240px;margin:0 auto;zoom:var(--zoom,1)}}

  header{{padding:56px 0 32px;border-bottom:1px solid var(--line);margin-bottom:36px;position:relative}}
  .eyebrow{{font-size:17px;letter-spacing:.24em;color:var(--amber);font-weight:700;margin-bottom:14px}}
  h1{{font-family:var(--disp);font-weight:400;font-size:56px;line-height:1.15}}
  .lede{{color:var(--muted);font-size:21px;margin-top:16px;font-weight:500;line-height:1.55}}
  .lede b{{color:var(--text)}}

  .zoom{{position:absolute;right:0;top:56px;display:flex;gap:6px}}
  .zoom button{{font:inherit;font-size:16px;font-weight:700;padding:8px 14px;border-radius:999px;
    border:2px solid var(--line);background:var(--panel);color:var(--muted);cursor:pointer}}
  .zoom button.on{{border-color:var(--amber);color:var(--amber)}}

  .tools{{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}}
  .tools a{{display:inline-flex;align-items:center;gap:9px;text-decoration:none;
    background:var(--panel);border:2px solid var(--line);border-radius:999px;
    padding:11px 22px;color:var(--text);font-weight:900;font-size:18px}}
  .tools a:hover{{border-color:var(--amber);color:var(--amber)}}
  .tools a:focus-visible{{outline:3px solid var(--amber);outline-offset:3px}}
  .tools a.web{{border-color:var(--amber);color:var(--amber)}}

  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px}}
  .card{{background:var(--panel);border:1px solid var(--line);border-radius:18px;
    padding:24px 26px;position:relative;display:flex;flex-direction:column;gap:12px}}
  .card.ready{{border-left:6px solid var(--green)}}
  .card.todo{{border-left:6px solid var(--line);opacity:.72}}
  .card.run{{border-left:6px solid var(--amber);opacity:1}}
  .card.run2{{border-image:linear-gradient(var(--green) 50%,var(--amber) 50%) 1;border-left-width:6px;border-left-style:solid}}
  .no{{font-family:var(--mono);font-size:16px;font-weight:600;color:var(--amber);
    letter-spacing:.1em}}
  .card h2{{font-family:var(--disp);font-weight:400;font-size:27px;line-height:1.25}}
  .soon{{font-size:16px;font-weight:700;color:var(--faint);letter-spacing:.05em}}

  .links{{display:flex;flex-wrap:wrap;gap:8px;margin-top:auto;padding-top:6px}}
  .lk{{text-decoration:none;font-size:16px;font-weight:700;color:var(--muted);
    background:var(--panel2);border:1px solid var(--line);border-radius:9px;
    padding:7px 13px;white-space:nowrap}}
  .lk:hover{{color:var(--text);border-color:var(--muted)}}
  .lk:focus-visible{{outline:3px solid var(--amber);outline-offset:2px}}
  .lk.main{{color:#06210F;background:var(--green);border-color:var(--green)}}
  .lk.main:hover{{background:#9BE5AB;color:#06210F}}
  .lk.run{{color:#1A0E02;background:var(--amber);border-color:var(--amber)}}
  .lk.run:hover{{background:#FFC768;color:#1A0E02}}

  footer{{margin-top:46px;padding-top:22px;border-top:1px solid var(--line);
    color:var(--faint);font-size:16px;font-weight:500;line-height:1.8}}
  footer b{{color:var(--muted)}}

  @media (max-width:640px){{
    h1{{font-size:38px}} body{{padding:0 18px 60px}}
    .grid{{grid-template-columns:minmax(0,1fr)}}
    .zoom{{position:static;margin-top:14px}}
  }}
</style>

<div class="wrap">
<header>
  <div class="eyebrow">숭신고 2학년 · ESP32 올인원 키트</div>
  <h1>사물 인터넷과 센서 제어</h1>
  <p class="lede">챕터를 고르면 <b>소스 실행기 · 수업 대본 · 해설 영상 · 실습 코드</b>로 바로 갑니다.<br>
    <b>소스 실행기 {n_run}개 챕터</b> 완성 — 소스를 한 줄씩 돌리며 3D 부품을 직접 만져 봅니다. 수업 대본 <b>{done}개 챕터</b> 완성.</p>
  <div class="zoom" aria-label="글자 크기">
    <button data-z="1" class="on">보통</button>
    <button data-z="1.25">크게</button>
    <button data-z="1.5">최대</button>
  </div>
  <div class="tools">
    <a class="web" href="{WEB_URL}">🌐 학생 공유 사이트</a>
    <a href="ESP32_%ED%95%80%EC%A7%80%EB%8F%84.html">📍 ESP32 핀 지도</a>
    <a href="../ESP32_%ED%95%80%EB%A7%B5_3D%EB%B7%B0%EC%96%B4.html">🧭 ESP32 핀맵 3D</a>
    <a href="../%EC%82%AC%EB%AC%BC%EC%98%81%EC%83%81">📺 영상 폴더</a>
  </div>
</header>

<div class="grid">
{chr(10).join(cards)}
</div>

<footer>
  소스 실행기는 <b>인터넷이 되어야</b> 열립니다(3D 라이브러리와 글꼴을 내려받습니다). 영상은 <b>사물영상</b> 폴더에서 인터넷 없이 재생됩니다.<br>
  학생에게는 <b>{WEB_URL}</b> 를 알려 주세요 — 실행기·대본만 있고 교재·영상은 없습니다.<br>
  교재 PDF의 저작권은 <b>아이씨뱅큐(ICBANQ)</b>에 있습니다. 교내 수업 용도로만 사용하세요.
</footer>
</div>
<script>
(function(){{
  var KEY="iot-index-zoom", bs=document.querySelectorAll(".zoom button");
  function set(z){{document.documentElement.style.setProperty("--zoom",z);
    bs.forEach(function(b){{b.classList.toggle("on",b.dataset.z===String(z))}});
    try{{localStorage.setItem(KEY,z)}}catch(e){{}}}}
  bs.forEach(function(b){{b.onclick=function(){{set(b.dataset.z)}}}});
  try{{var s=localStorage.getItem(KEY); if(s) set(s)}}catch(e){{}}
}})();
</script>
'''

out = os.path.join(KIT, "index.html")
io.open(out, "w", encoding="utf-8").write(html)
print(f"생성: index.html")
print(f"  챕터 {len(chapters)}개 · 실행기 {n_run}개 · 대본 {done}개")
for c in chapters:
    marks = " ".join(x for x in (c["runner"] and "🕹️", c["script"] and "🗣️", c["easy"] and "📖") if x)
    print(f"  {c['num']} {c['title']:<14} {marks}")
