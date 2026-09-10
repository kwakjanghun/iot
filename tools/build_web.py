# -*- coding: utf-8 -*-
"""구글드라이브의 수업 자료 → GitHub Pages용 웹 빌드.

로컬본과 다른 점
  · 파일명을 ASCII로 (ch05-buzzer.html) — 한글 URL 인코딩 문제 회피. 드라이브 원본은 그대로.
  · 수업 진행 대본은 아예 제외 (교사용 문서)
  · 영상은 깃에 올리지 않고 안내 문구로 교체
  · 교재 PDF·실습코드·라이브러리는 넣지 않음 (ICBANQ 저작물)

웹 파일명 규칙 (장 번호가 앞에 오므로 정렬 순서가 그대로 유지된다)
  chNN-<주제>.html   소스 실행기 (01장은 조립 순서기)
  (수업 진행 대본은 교사용이라 웹에 올리지 않는다)
  chNN-easy.html     아주 쉬운 설명서
"""
import os, re, glob, io, sys, shutil
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"G:/내 드라이브/2026년/올인원_사물"
KIT = os.path.join(ROOT, "ESP32 올인원 키트_교안")
WEB = r"C:/Users/ai/iot-site"

# 장 번호 → 영문 슬러그. 새 장을 만들면 여기에 한 줄 추가.
SLUG = {
    "01": "assembly",  "02": "setup",      "03": "led",        "04": "rgb-led",
    "05": "buzzer",    "06": "display",    "07": "lcd-servo",  "08": "button",
    "09": "game",      "10": "sensor",     "11": "analog",     "12": "sound-sensor",
    "13": "dht",       "14": "ultrasonic", "15": "parking",    "16": "ir-remote",
    "17": "wifi",
}

NOTICE = '''<section id="film">
  <div class="secnum"><span class="chip">영상</span></div>
  <h2>📺 오늘의 영상</h2>
  <div class="warn" style="border-top-color:var(--amber)">
    <div class="lab" style="color:var(--amber)">🏫 영상은 학교 자료에서</div>
    해설 영상은 용량이 커서 이 사이트에는 올리지 않았습니다.
    <b>구글 드라이브의 수업 폴더</b>에서 재생하세요.
    그 폴더의 같은 대본 파일에서는 영상이 페이지 안에서 바로 열립니다.
  </div>
</section>'''

os.makedirs(WEB, exist_ok=True)


def kit_glob(pat):
    return sorted(glob.glob(os.path.join(glob.escape(KIT), pat)))


# 장 번호 → {"run": 파일, "kind": 실행기/조립 순서기, "script": 파일, "easy": 파일}
pages = {}

# ── 소스 실행기 · 조립 순서기 ──────────────
for path in kit_glob("*장_*_소스실행기.html") + kit_glob("*장_*_조립순서기.html"):
    num = os.path.basename(path)[:2]
    if num not in SLUG:
        print(f"  !! SLUG 에 {num} 장이 없어 건너뜀: {os.path.basename(path)}")
        continue
    out = f"ch{num}-{SLUG[num]}.html"
    shutil.copyfile(path, os.path.join(WEB, out))
    kind = "조립 순서기" if "조립순서기" in path else "소스 실행기"
    pages.setdefault(num, {})["run"] = out
    pages[num]["kind"] = kind
    print(f"  {out:22s} ← {os.path.basename(path)}")

# ── 수업 진행 대본 : 웹에 올리지 않는다 ─────
# 2026-09-10 사용자 결정. 대본은 교사가 수업하며 보는 문서다.
# 학생 답·교사 메모·다음 반에서 쓸 발문이 그대로 들어 있어 공개 사이트에 두지 않는다.
# 드라이브 로컬 index.html 에는 그대로 나온다 (build_index.py 쪽).

# ── 아주 쉬운 설명서 ───────────────────────
for path in kit_glob("*장_*_아주쉬운설명서.html"):
    num = os.path.basename(path)[:2]
    out = f"ch{num}-easy.html"
    shutil.copyfile(path, os.path.join(WEB, out))
    pages.setdefault(num, {})["easy"] = out
    print(f"  {out:22s} ← {os.path.basename(path)}")

# ── 핀 지도 · 3D 핀맵 ─────────────────────
for src, dst in ((os.path.join(KIT, "ESP32_핀지도.html"), "pinmap.html"),
                 (os.path.join(ROOT, "ESP32_핀맵_3D뷰어.html"), "pinmap-3d.html")):
    if os.path.exists(src):
        shutil.copyfile(src, os.path.join(WEB, dst))
        print(f"  {dst:22s} ← {os.path.basename(src)}")

# ── AI 영상 특강 (Flow) 페이지 ──
for src, dst in (("특강_Flow프롬프트생성기.html", "flow-prompt.html"),
                 ("특강_Flow실전_프롬프트모음.html", "flow-prompts.html")):
    fp = os.path.join(KIT, src)
    if os.path.exists(fp):
        shutil.copyfile(fp, os.path.join(WEB, dst))
        print(f"  {dst:22s} ← {src}")
shots = os.path.join(KIT, "flow-shots")
if os.path.isdir(shots):
    dst_dir = os.path.join(WEB, "flow-shots"); os.makedirs(dst_dir, exist_ok=True)
    for fn in os.listdir(shots):
        if fn.lower().endswith(".jpg"):
            shutil.copyfile(os.path.join(shots, fn), os.path.join(dst_dir, fn))
    print("  flow-shots/ 복사")

# ── 챕터 목록 ──────────────────────────────
chapters = []
for name in sorted(os.listdir(KIT)):
    if not os.path.isdir(os.path.join(KIT, name)) or not name[:2].isdigit():
        continue
    chapters.append((name[:2], name[3:].strip(), pages.get(name[:2], {})))

n_run = sum(1 for _, _, p in chapters if p.get("run"))

cards = []
for num, title, p in chapters:
    if p.get("run"):
        subs = []
        if p.get("easy"):
            subs.append(f'<a class="sub" href="{p["easy"]}">🧸 아주 쉬운 설명서</a>')
        subs_html = f'<div class="subs">{"".join(subs)}</div>' if subs else ""
        cards.append(f'''  <div class="card ready">
    <div class="no">{num}</div>
    <h2>{title}</h2>
    <a class="go" href="{p["run"]}">▶ {p["kind"]} 열기</a>
    {subs_html}
  </div>''')
    else:
        cards.append(f'''  <div class="card todo">
    <div class="no">{num}</div>
    <h2>{title}</h2>
    <span class="soon">준비 중</span>
  </div>''')

html = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>사물 인터넷과 센서 제어</title>
<meta name="description" content="숭신고 2학년 사물 인터넷과 센서 제어 — 장별 소스 실행기(한 줄씩 실행하며 값을 바꿔 보는 시뮬레이터)">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@600&display=swap">
<style>
  :root{{
    --bg:#0B0F14; --panel:#141B25; --panel2:#0F141C; --line:#232D3B;
    --text:#E8EDF4; --muted:#93A1B5; --faint:#6B7A8E;
    --amber:#FFB03A; --green:#7BD88F;
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
  .lede{{color:var(--muted);font-size:21px;margin-top:16px;font-weight:500;max-width:46em;line-height:1.55}}
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

  h3.sec{{font-family:var(--disp);font-weight:400;font-size:32px;margin:0 0 6px}}
  p.hint{{color:var(--muted);font-size:17px;margin-bottom:20px;line-height:1.6}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:16px}}
  .card{{background:var(--panel);border:1px solid var(--line);border-radius:18px;
    padding:22px 24px;display:flex;flex-direction:column;gap:10px;color:inherit}}
  .card.ready{{border-left:6px solid var(--amber)}}
  .card.todo{{border-left:6px solid var(--line);opacity:.55}}
  .no{{font-family:var(--mono);font-size:16px;font-weight:600;color:var(--amber);letter-spacing:.1em}}
  .card h2{{font-family:var(--disp);font-weight:400;font-size:27px;line-height:1.25}}
  .go{{display:block;margin-top:auto;text-decoration:none;text-align:center;
    background:var(--amber);color:#1A1200;font-weight:900;font-size:18px;
    padding:12px 14px;border-radius:12px}}
  .go:hover{{filter:brightness(1.08)}}
  .go:focus-visible{{outline:3px solid #fff;outline-offset:3px}}
  .subs{{display:flex;gap:8px;flex-wrap:wrap}}
  .sub{{font-size:16px;font-weight:700;color:var(--green);text-decoration:none;
    border:1.5px solid var(--line);border-radius:999px;padding:6px 12px}}
  .sub:hover{{border-color:var(--green)}}
  .soon{{font-size:16px;font-weight:700;color:var(--faint);margin-top:auto}}

  footer{{margin-top:52px;padding-top:22px;border-top:1px solid var(--line);
    color:var(--faint);font-size:16px;font-weight:500;line-height:1.9}}
  footer b{{color:var(--muted)}}

  @media (max-width:640px){{
    h1{{font-size:38px}} body{{padding:0 18px 60px}}
    .grid{{grid-template-columns:minmax(0,1fr)}}
    .zoom{{position:static;margin-top:14px}}
  }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="eyebrow">숭신고 2학년 · ESP32 올인원 키트</div>
  <h1>사물 인터넷과 센서 제어</h1>
  <p class="lede">장을 고르면 <b>소스 실행기</b>가 열립니다.
    실습 코드를 <b>한 줄씩 실행</b>하고, 소스 안의 숫자를 <b>직접 바꿔</b> 가상 부품이 어떻게 달라지는지 봅니다.
    현재 <b>{n_run}개 장</b> 준비됨.</p>
  <div class="zoom" aria-label="글자 크기">
    <button data-z="1" class="on">보통</button>
    <button data-z="1.25">크게</button>
    <button data-z="1.5">최대</button>
  </div>
  <div class="tools">
    <a href="pinmap-3d.html">🧭 ESP32 핀맵 3D</a>
    <a href="pinmap.html">📍 ESP32 핀 지도</a>
    <a href="pwm.html">🎚 PWM 조작 실습</a>
    <a href="flow-prompt.html">🎬 Flow 프롬프트 생성기</a>
    <a href="flow-prompts.html">📋 Flow 실전 프롬프트 모음</a>
  </div>
</header>

<h3 class="sec">장별 소스 실행기</h3>
<p class="hint">▶ 실행 · 한 줄 → · 값 되돌리기 · 설명 보기 단추가 화면 위에 붙어 있습니다. 각 실행기 안에도 글자 크기 단추가 있습니다.</p>
<div class="grid">
{chr(10).join(cards)}
</div>

<footer>
  해설 영상은 용량이 커서 <b>학교 구글 드라이브</b>에 있습니다.<br>
  실습 코드와 교재의 저작권은 <b>아이씨뱅큐(ICBANQ)</b>에 있어 이 사이트에는 싣지 않았습니다.
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
</body>
</html>
'''
io.open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(html)
print(f"  index.html  (장 {len(chapters)}개 · 실행기 {n_run}개 · 대본은 웹에 올리지 않음)")
