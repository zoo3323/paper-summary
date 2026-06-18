#!/usr/bin/env python3
"""
extract_pdf.py — paper-summary 스킬용 PDF 추출기

PDF에서 다음을 뽑아낸다:
  - 페이지별 텍스트 (fulltext.txt + manifest.json)
  - 임베디드 래스터 이미지 (사진/스캔 그림)  -> images_dir
  - 벡터 그래프/도표 영역을 크롭 렌더링       -> images_dir (vec_*.png)

사용법:
  python3 extract_pdf.py <pdf> <work_dir> <images_dir> [--dpi 150] [--min 70]

출력:
  <work_dir>/manifest.json   : 페이지 텍스트 + 사용 가능한 이미지 목록(경로/크기/타입/bbox)
  <work_dir>/fulltext.txt    : 전체 텍스트 덤프(페이지 구분)
  <images_dir>/*.png         : HTML 에서 참조할 그림 파일들

manifest.json 에는 base64 를 넣지 않는다(토큰 절약). HTML 은 images/<file> 상대경로로 참조.
"""
import sys, os, json, argparse


def log(msg):
    print(msg, file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("work_dir")
    ap.add_argument("images_dir")
    ap.add_argument("--dpi", type=int, default=150, help="벡터 그래프 크롭 렌더 DPI")
    ap.add_argument("--min", type=int, default=70, help="이 픽셀 미만 이미지는 무시")
    args = ap.parse_args()

    try:
        import fitz  # PyMuPDF
    except ImportError:
        print(json.dumps({"ok": False, "error": "PYMUPDF_MISSING"}))
        log("PyMuPDF 미설치. `pip3 install pymupdf` 후 다시 실행하세요.")
        sys.exit(2)

    if not os.path.isfile(args.pdf):
        print(json.dumps({"ok": False, "error": "PDF_NOT_FOUND", "pdf": args.pdf}))
        sys.exit(1)

    os.makedirs(args.work_dir, exist_ok=True)
    os.makedirs(args.images_dir, exist_ok=True)

    doc = fitz.open(args.pdf)
    rel_prefix = "images"  # HTML 에서의 상대 경로 접두사
    manifest = {
        "pdf": os.path.abspath(args.pdf),
        "title": doc.metadata.get("title") or "",
        "author": doc.metadata.get("author") or "",
        "n_pages": doc.page_count,
        "pages": [],
    }

    seen_xref = set()
    n_raster = 0
    n_vector = 0

    for pno in range(doc.page_count):
        page = doc[pno]
        text = page.get_text("text")
        page_imgs = []

        # --- 1) 임베디드 래스터 이미지 ---
        for info in page.get_images(full=True):
            xref = info[0]
            if xref in seen_xref:
                continue
            seen_xref.add(xref)
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.width < args.min or pix.height < args.min:
                    pix = None
                    continue
                if pix.n - pix.alpha >= 4:  # CMYK 등 -> RGB 변환
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                fname = "p%03d_img%d.png" % (pno + 1, xref)
                pix.save(os.path.join(args.images_dir, fname))
                page_imgs.append({
                    "src": rel_prefix + "/" + fname,
                    "type": "raster",
                    "page": pno + 1,
                    "width": pix.width,
                    "height": pix.height,
                })
                n_raster += 1
                pix = None
            except Exception as e:
                log("page %d xref %d raster 실패: %s" % (pno + 1, xref, e))

        # --- 2) 벡터 그래프/도표 클러스터 크롭 ---
        try:
            clusters = page.cluster_drawings()
        except Exception:
            clusters = []
        pw, ph = page.rect.width, page.rect.height
        for i, rect in enumerate(clusters):
            try:
                if rect.width < 80 or rect.height < 60:
                    continue
                # 페이지 거의 전체를 덮는 건 배경/테두리로 보고 스킵
                if rect.width > pw * 0.95 and rect.height > ph * 0.95:
                    continue
                mat = fitz.Matrix(args.dpi / 72.0, args.dpi / 72.0)
                pix = page.get_pixmap(matrix=mat, clip=rect, alpha=False)
                fname = "p%03d_vec%d.png" % (pno + 1, i)
                pix.save(os.path.join(args.images_dir, fname))
                page_imgs.append({
                    "src": rel_prefix + "/" + fname,
                    "type": "vector",
                    "page": pno + 1,
                    "width": pix.width,
                    "height": pix.height,
                    "bbox": [round(rect.x0, 1), round(rect.y0, 1),
                             round(rect.x1, 1), round(rect.y1, 1)],
                })
                n_vector += 1
                pix = None
            except Exception as e:
                log("page %d vec %d 실패: %s" % (pno + 1, i, e))

        manifest["pages"].append({
            "page": pno + 1,
            "text": text,
            "images": page_imgs,
        })

    # manifest.json
    with open(os.path.join(args.work_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)

    # fulltext.txt
    with open(os.path.join(args.work_dir, "fulltext.txt"), "w", encoding="utf-8") as fh:
        for p in manifest["pages"]:
            fh.write("\n===== PAGE %d =====\n" % p["page"])
            fh.write(p["text"])

    doc.close()
    print(json.dumps({
        "ok": True,
        "n_pages": manifest["n_pages"],
        "n_raster": n_raster,
        "n_vector": n_vector,
        "title": manifest["title"],
        "manifest": os.path.join(args.work_dir, "manifest.json"),
        "fulltext": os.path.join(args.work_dir, "fulltext.txt"),
        "images_dir": args.images_dir,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
