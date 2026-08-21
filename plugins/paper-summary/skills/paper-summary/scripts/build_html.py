#!/usr/bin/env python3
"""build_html.py — 조각 + 템플릿 + CSS 를 조립해 결과 HTML 을 만든다.

    python3 build_html.py <스킬 base-dir> <조각 폴더> <출력 폴더>

모델은 CSS 나 HTML 뼈대를 받아쓰지 않는다. 아래 조각 파일만 쓰면 된다:

  <조각 폴더>/meta.json    {"TITLE_KO":…, "TITLE_ORIGINAL":…, "AUTHORS":…, "VENUE_YEAR":…}
  <조각 폴더>/body.html    번역본 본문 전체 (h2/h3/figure/table/수식)
  <조각 폴더>/summary.html 요약 조각들. 아래 마커로 구분한다:
                           <!--#TLDR--> <!--#PROBLEM--> <!--#CONTRIBUTION-->
                           <!--#METHOD--> <!--#RESULTS--> <!--#CONCLUSION-->
                           <!--#LIMITATIONS--> <!--#TERMS-->

번역본만 다시 만들려면 summary.html 을, 요약본만이면 body.html 을 생략해도 된다.
"""
import sys, os, json, re

KEYS = ["TLDR", "PROBLEM", "CONTRIBUTION", "METHOD",
        "RESULTS", "CONCLUSION", "LIMITATIONS", "TERMS"]
META_KEYS = ["TITLE_KO", "TITLE_ORIGINAL", "AUTHORS", "VENUE_YEAR"]


def die(msg):
    print("오류: " + msg, file=sys.stderr)
    sys.exit(1)


def split_markers(raw):
    """<!--#KEY--> 마커로 나뉜 조각들을 딕셔너리로."""
    parts, cur, buf = {}, None, []
    for line in raw.splitlines(True):
        m = re.match(r"\s*<!--#([A-Z_]+)-->\s*$", line)
        if m:
            if cur:
                parts[cur] = "".join(buf).strip()
            cur, buf = m.group(1), []
        else:
            buf.append(line)
    if cur:
        parts[cur] = "".join(buf).strip()
    return parts


def main():
    if len(sys.argv) != 4:
        die("사용법: build_html.py <스킬 base-dir> <조각 폴더> <출력 폴더>")
    base, src, out = (os.path.abspath(p) for p in sys.argv[1:4])
    assets = os.path.join(base, "assets")
    for p in (assets, src):
        if not os.path.isdir(p):
            die("폴더가 없습니다: " + p)

    css = open(os.path.join(assets, "style.css"), encoding="utf-8").read()

    meta_path = os.path.join(src, "meta.json")
    if not os.path.isfile(meta_path):
        die("meta.json 이 없습니다: " + meta_path)
    meta = json.load(open(meta_path, encoding="utf-8"))
    missing_meta = [k for k in META_KEYS if not str(meta.get(k, "")).strip()]
    if missing_meta:
        die("meta.json 에 빠진 항목: " + ", ".join(missing_meta))

    os.makedirs(out, exist_ok=True)
    warnings, written = [], []

    def fill(tpl_name, values, out_name):
        tpl = open(os.path.join(assets, tpl_name), encoding="utf-8").read()
        html = tpl.replace("{{CSS}}", css)
        for k, v in list(meta.items()) + list(values.items()):
            html = html.replace("{{%s}}" % k, v)
        left = sorted(set(re.findall(r"\{\{([A-Z_]+)\}\}", html)))
        if left:
            warnings.append("%s: 치환 안 된 자리 %s" % (out_name, ", ".join(left)))
        path = os.path.join(out, out_name)
        open(path, "w", encoding="utf-8").write(html)
        written.append((out_name, len(html.encode("utf-8"))))

    body_path = os.path.join(src, "body.html")
    if os.path.isfile(body_path):
        fill("template_translation.html",
             {"BODY": open(body_path, encoding="utf-8").read()}, "번역본.html")

    sum_path = os.path.join(src, "summary.html")
    if os.path.isfile(sum_path):
        parts = split_markers(open(sum_path, encoding="utf-8").read())
        empty = [k for k in KEYS if not parts.get(k)]
        if empty:
            warnings.append("요약본.html: 내용이 빈 항목 " + ", ".join(empty))
        fill("template_summary.html",
             {k: parts.get(k) or "<p>해당 없음</p>" for k in KEYS}, "요약본.html")

    if not written:
        die("body.html 도 summary.html 도 없습니다. 조각 폴더를 확인하세요: " + src)

    for name, size in written:
        print("생성: %s (%s바이트)" % (os.path.join(out, name), format(size, ",")))
    for w in warnings:
        print("경고: " + w, file=sys.stderr)
    sys.exit(1 if warnings else 0)


if __name__ == "__main__":
    main()
