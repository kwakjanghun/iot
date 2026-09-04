# -*- coding: utf-8 -*-
"""구글드라이브의 수업 자료 → GitHub Pages용 웹 빌드.

로컬본과 다른 점
  · 파일명을 ASCII로 (ch03.html) — 한글 URL 인코딩 문제 회피
  · 영상 <video>는 안내 문구로 교체 (영상은 깃에 올리지 않음)
  · 교재 PDF·실습코드·라이브러리는 넣지 않음 (ICBANQ 저작물)
"""
import os, re, glob, io, sys, shutil
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"G:/내 드라이브/2026년/올인원_사물"
KIT = os.path.join(ROOT, "ESP32 올인원 키트_교안")
WEB = r"C:/Users/ai/iot-site"

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

# ── 챕터 대본 ──────────────────────────────
made = []
for path in sorted(glob.glob(os.path.join(glob.escape(KIT), "*장_*_수업진행대본.html"))):
    num = os.path.basename(path)[:2]
    s = io.open(path, encoding="utf-8").read()

    # 영상 섹션 → 안내로 교체
    s = re.sub(r'<section id="film">.*?</section>', NOTICE, s, flags=re.S)
    # 핀 지도 링크를 ASCII 이름으로
    s = s.replace("ESP32_핀지도.html", "pinmap.html")
    s = s.replace("ESP32_%ED%95%80%EC%A7%80%EB%8F%84.html", "pinmap.html")

    out = os.path.join(WEB, f"ch{num}.html")
    io.open(out, "w", encoding="utf-8").write(s)
    title = re.search(r"<title>([^<]*)</title>", s).group(1)
    made.append((num, f"ch{num}.html", title))
    print(f"  ch{num}.html  ← {os.path.basename(path)}")

# ── 핀 지도 ────────────────────────────────
pin = os.path.join(KIT, "ESP32_핀지도.html")
if os.path.exists(pin):
    shutil.copyfile(pin, os.path.join(WEB, "pinmap.html"))
    print("  pinmap.html ← ESP32_핀지도.html")

# ── AI 영상 특강 (Flow) 페이지 ──
for src, dst in (("특강_Flow프롬프트생성기.html", "flow-prompt.html"),
                 ("특강_Flow실전_프롬프트모음.html", "flow-prompts.html")):
    fp = os.path.join(KIT, src)
    if os.path.exists(fp):
        shutil.copyfile(fp, os.path.join(WEB, dst))
        print(f"  {dst} ← {src}")
shots = os.path.join(KIT, "flow-shots")
if os.path.isdir(shots):
    dst_dir = os.path.join(WEB, "flow-shots"); os.makedirs(dst_dir, exist_ok=True)
    for fn in os.listdir(shots):
        if fn.lower().endswith(".jpg"):
            shutil.copyfile(os.path.join(shots, fn), os.path.join(dst_dir, fn))
    print("  flow-shots/ 복사")

# ── 챕터 목록 (대본 없는 것도 이름은 보여줌) ──
chapters = []
for name in sorted(os.listdir(KIT)):
    if not os.path.isdir(os.path.join(KIT, name)) or not name[:2].isdigit():
        continue
    num, title = name[:2], name[3:].strip()
    script = next((f for n, f, _ in made if n == num), None)
    chapters.append((num, title, script))

done = sum(1 for _, _, s in chapters if s)

cards = []
for num, title, script in chapters:
    if script:
        cards.append(f'''  <a class="card ready" href="{script}">
    <div class="no">{num}</div>
    <h2>{title}</h2>
    <span class="go">수업 대본 열기 →</span>
  </a>''')
    else:
        cards.append(f'''  <div class="card todo">
    <div class="no">{num}</div>
    <h2>{title}</h2>
    <span class="soon">대본 준비 중</span>
  </div>''')

html = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>사물 인터넷과 센서 제어</title>
<meta name="description" content="숭신고 2학년 사물 인터넷과 센서 제어 — 수업 대본과 실습 도구">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@600&display=swap">
<style>
  :root{{
    --bg:#0B0F14; --panel:#141B25; --panel2:#0F141C; --line:#232D3B;
    --text:#E8EDF4; --muted:#93A1B5; --faint:#5C6B7E;
    --amber:#FFB03A; --green:#7BD88F;
    --disp:'Black Han Sans',sans-serif;
    --body:'Noto Sans KR','Apple SD Gothic Neo',sans-serif;
    --mono:'IBM Plex Mono','Consolas',monospace;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:var(--body);
    padding:0 28px 80px;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:1180px;margin:0 auto}}

  header{{padding:64px 0 36px;border-bottom:1px solid var(--line);margin-bottom:40px}}
  .eyebrow{{font-size:16px;letter-spacing:.24em;color:var(--amber);font-weight:700;margin-bottom:14px}}
  h1{{font-family:var(--disp);font-weight:400;font-size:54px;line-height:1.15}}
  .lede{{color:var(--muted);font-size:20px;margin-top:16px;font-weight:500;max-width:44em}}
  .lede b{{color:var(--text)}}

  .tools{{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}}
  .tools a{{display:inline-flex;align-items:center;gap:9px;text-decoration:none;
    background:var(--panel);border:2px solid var(--line);border-radius:999px;
    padding:11px 22px;color:var(--text);font-weight:900;font-size:17px}}
  .tools a:hover{{border-color:var(--amber);color:var(--amber)}}
  .tools a:focus-visible{{outline:3px solid var(--amber);outline-offset:3px}}

  h3.sec{{font-family:var(--disp);font-weight:400;font-size:30px;margin:0 0 18px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
  .card{{background:var(--panel);border:1px solid var(--line);border-radius:18px;
    padding:24px 26px;display:flex;flex-direction:column;gap:10px;
    text-decoration:none;color:inherit}}
  .card.ready{{border-left:6px solid var(--green)}}
  .card.ready:hover{{border-color:var(--green);background:#182231}}
  .card.ready:focus-visible{{outline:3px solid var(--green);outline-offset:3px}}
  .card.todo{{border-left:6px solid var(--line);opacity:.6}}
  .no{{font-family:var(--mono);font-size:15px;font-weight:600;color:var(--amber);letter-spacing:.1em}}
  .card h2{{font-family:var(--disp);font-weight:400;font-size:26px;line-height:1.25}}
  .go{{font-size:15px;font-weight:700;color:var(--green);margin-top:auto}}
  .soon{{font-size:14px;font-weight:700;color:var(--faint);margin-top:auto}}

  footer{{margin-top:52px;padding-top:22px;border-top:1px solid var(--line);
    color:var(--faint);font-size:15px;font-weight:500;line-height:1.9}}
  footer b{{color:var(--muted)}}

  @media (max-width:640px){{
    h1{{font-size:36px}} body{{padding:0 18px 60px}}
    .grid{{grid-template-columns:minmax(0,1fr)}}
  }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="eyebrow">숭신고 2학년 · ESP32 올인원 키트</div>
  <h1>사물 인터넷과 센서 제어</h1>
  <p class="lede">챕터를 고르면 <b>수업 대본</b>이 열립니다.
    코드 해설과 <b>직접 조작하는 실행 데모</b>가 들어 있습니다.
    현재 <b>{done}개 챕터</b> 완성.</p>
  <div class="tools">
    <a href="pinmap.html">📍 ESP32 핀 지도</a>
    <a href="pwm.html">🎚 PWM 조작 실습</a>
    <a href="flow-prompt.html">🎬 Flow 프롬프트 생성기</a>
    <a href="flow-prompts.html">📋 Flow 실전 프롬프트 모음</a>
  </div>
</header>

<h3 class="sec">챕터</h3>
<div class="grid">
{chr(10).join(cards)}
</div>

<footer>
  해설 영상은 용량이 커서 <b>학교 구글 드라이브</b>에 있습니다.<br>
  실습 코드와 교재의 저작권은 <b>아이씨뱅큐(ICBANQ)</b>에 있어 이 사이트에는 싣지 않았습니다.
</footer>
</div>
</body>
</html>
'''
io.open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(html)
print(f"  index.html  (챕터 {len(chapters)}개 · 대본 {done}개)")
