# -*- coding: utf-8 -*-
"""대본 HTML에 ① 홈 링크 ② 영상 재생 블록을 넣는다. 여러 번 돌려도 안전."""
import os, glob, io, sys, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"G:/내 드라이브/2026년/올인원_사물"
KIT = os.path.join(ROOT, "[배포용_교안]_ESP32 올인원 키트")
VID = os.path.join(ROOT, "사물영상")
enc = lambda p: urllib.parse.quote(p.replace("\\", "/"))

VIDEO_CSS = """
  /* ── 영상 ── */
  .films{display:flex;flex-direction:column;gap:16px;margin:24px 0}
  .film{background:var(--panel);border:1px solid var(--line);border-radius:16px;
    overflow:hidden}
  .film > b{display:block;padding:16px 24px 12px;font-size:19px;font-weight:900}
  .film > b small{display:block;font-size:15px;color:var(--muted);
    font-weight:700;margin-top:3px}
  .film video{display:block;width:100%;background:#000;max-height:70vh}
  .clips{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
  .clips .film > b{padding:12px 18px 9px;font-size:17px}
  .nofilm{color:var(--muted);font-size:17px;font-weight:700;padding:16px 24px}
"""

HOME = ('  <a class="home" href="index.html">\u2190 \uc218\uc5c5 \ud648</a>\n')
HOME_CSS = """
  nav .in .home{color:var(--amber);border-color:var(--amber);font-weight:900}
"""

for path in sorted(glob.glob(os.path.join(glob.escape(KIT), "*장_*_수업진행대본.html"))):
    fn = os.path.basename(path)
    num = fn[:2]
    s = io.open(path, encoding="utf-8").read()

    if "class=\"films\"" in s:
        print(f"  건너뜀 (이미 있음): {fn}")
        continue

    # 챕터 폴더 찾기
    folder = next((n for n in os.listdir(KIT)
                   if os.path.isdir(os.path.join(KIT, n)) and n[:2] == num), None)

    # 통합 해설 영상
    vids = glob.glob(os.path.join(VID, f"{num}_00_*통합_코드해설.mp4"))
    vids = [v for v in vids if "압축" not in os.path.basename(v)] or vids

    blocks = []
    if vids:
        src = enc("../사물영상/" + os.path.basename(vids[0]))
        blocks.append(f'''  <div class="film">
    <b>통합 코드해설<small>{os.path.basename(vids[0])}</small></b>
    <video controls preload="metadata" src="{src}"></video>
  </div>''')

    clips = sorted(glob.glob(os.path.join(glob.escape(os.path.join(KIT, folder, "실습영상")), "*.mp4"))) if folder else []
    if clips:
        inner = "\n".join(
            f'''    <div class="film">
      <b>{os.path.splitext(os.path.basename(c))[0]}</b>
      <video controls preload="metadata" src="{enc(folder + "/실습영상/" + os.path.basename(c))}"></video>
    </div>''' for c in clips)
        blocks.append(f'  <div class="clips">\n{inner}\n  </div>')

    body = "\n".join(blocks) if blocks else '  <div class="nofilm">이 챕터는 영상이 아직 없습니다.</div>'
    section = f'''
<section id="film">
  <div class="secnum"><span class="chip">영상</span></div>
  <h2>📺 오늘의 영상</h2>
  <div class="films">
{body}
  </div>
</section>
'''

    # ① CSS 추가
    s = s.replace("</style>", VIDEO_CSS + HOME_CSS + "</style>", 1)
    # ② 홈 링크 + 영상 메뉴
    s = s.replace('<nav><div class="in">\n', '<nav><div class="in">\n' + HOME
                  + '  <a href="#film">📺 영상</a>\n', 1)
    # ③ 도입 섹션 앞에 영상 섹션
    s = s.replace('<section id="intro">', section.strip() + '\n\n<section id="intro">', 1)

    io.open(path, "w", encoding="utf-8").write(s)
    print(f"  적용: {fn}  (통합 {len(vids)}개 · 실습 {len(clips)}개)")
