#!/usr/bin/env python3
"""build_glossary.py — 조각 + 템플릿 + CSS 를 조립해 용어사전.html 을 만든다.

    python3 build_glossary.py <스킬 base-dir> <조각 폴더> <출력 폴더>

모델은 CSS 나 HTML 뼈대를 받아쓰지 않는다. 아래 조각 파일만 쓰면 된다:

  <조각 폴더>/meta.json     {"TITLE_KO":…, "TITLE_ORIGINAL":…, "AUTHORS":…, "VENUE_YEAR":…}
  <조각 폴더>/glossary.html  <div class="term" …> 항목들만

번역본·요약본이 없으면 --standalone 을 붙인다. 네비게이션에서 깨질 링크를 빼 준다.
"""
import sys, os, json, re

META_KEYS = ["TITLE_KO", "TITLE_ORIGINAL", "AUTHORS", "VENUE_YEAR"]


def die(msg):
    print("오류: " + msg, file=sys.stderr)
    sys.exit(1)


def main():
    args = [a for a in sys.argv[1:] if a != "--standalone"]
    standalone = "--standalone" in sys.argv
    if len(args) != 3:
        die("사용법: build_glossary.py <스킬 base-dir> <조각 폴더> <출력 폴더> [--standalone]")
    base, src, out = (os.path.abspath(p) for p in args)
    assets = os.path.join(base, "assets")
    for p in (assets, src):
        if not os.path.isdir(p):
            die("폴더가 없습니다: " + p)

    meta_path = os.path.join(src, "meta.json")
    if not os.path.isfile(meta_path):
        die("meta.json 이 없습니다: " + meta_path)
    meta = json.load(open(meta_path, encoding="utf-8"))
    missing = [k for k in META_KEYS if not str(meta.get(k, "")).strip()]
    if missing:
        die("meta.json 에 빠진 항목: " + ", ".join(missing))

    gl_path = os.path.join(src, "glossary.html")
    if not os.path.isfile(gl_path):
        die("glossary.html 이 없습니다: " + gl_path)
    terms_html = open(gl_path, encoding="utf-8").read()
    n_terms = terms_html.count('class="term"')
    if n_terms == 0:
        die("glossary.html 에 <div class=\"term\"> 항목이 하나도 없습니다")

    css = open(os.path.join(assets, "style.css"), encoding="utf-8").read()
    html = open(os.path.join(assets, "template_glossary.html"), encoding="utf-8").read()
    html = html.replace("{{CSS}}", css).replace("{{GLOSSARY}}", terms_html)
    for k, v in meta.items():
        html = html.replace("{{%s}}" % k, v)

    if standalone:
        # 번역본·요약본이 없으면 그리로 가는 링크를 전부 걷어낸다
        html = re.sub(r'\s*<a href="(번역본|요약본)\.html"[^>]*>.*?</a>', "", html)
        html = re.sub(r'\s*<p class="more">\s*</p>', "", html)

    left = sorted(set(re.findall(r"\{\{([A-Z_]+)\}\}", html)))
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "용어사전.html")
    open(path, "w", encoding="utf-8").write(html)
    print("생성: %s (%s바이트, 용어 %d개)"
          % (path, format(len(html.encode("utf-8")), ","), n_terms))
    if left:
        print("경고: 치환 안 된 자리 " + ", ".join(left), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
