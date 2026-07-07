---
name: paper-summary-word
description: 현재 폴더의 PDF 논문(또는 paper-summary 가 만든 결과물)에서 전문 용어·약어를 뽑아 한국어 정의와 함께 정리한 검색 가능한 용어 사전 HTML(`용어사전.html`)을 만든다. 같은 `한국어_요약/` 폴더에 저장하고, 이미 있는 번역본·요약본의 네비게이션에 용어 사전 탭을 끼워 넣어 서로 클릭 이동되게 한다. 사용자가 /paper-summary-word 라고 하거나 "논문 용어/약어 사전 만들어줘"라고 할 때 사용.
---

# paper-summary-word

논문에 등장하는 **전문 용어·약어·고유명사**(모델명·데이터셋·평가지표·수학 기호 포함)를 한국어 정의와 함께 정리한 **용어 사전 HTML 1개**(`용어사전.html`)를 만든다. 실시간 검색 필터가 내장돼 있다.

`paper-summary` 스킬의 동반 스킬이다. 보통 `paper-summary` 로 번역본·요약본을 먼저 만든 뒤 실행하지만, 단독으로도(PDF만 있어도) 동작한다.

## 폴더 구조 (현재 폴더 기준)

```
./한국어_요약/          ← 결과물 폴더 (paper-summary 와 공유)
   ├─ 번역본.html       ← (있으면) 네비게이션에 용어사전 탭을 끼워 넣는다
   ├─ 요약본.html       ← (있으면) 네비게이션에 용어사전 탭을 끼워 넣는다
   ├─ 용어사전.html     ← ★ 이 스킬이 생성
   └─ images/
./작업파일/             ← (단독 실행 시) 추출 중간 산출물
   └─ fulltext.txt
```

---

## 실행 절차

### 0. 대상 PDF / 결과 폴더 찾기
- 인자(`$ARGUMENTS`)로 PDF 경로가 주어지면 그것을 사용.
- 없으면 현재 폴더의 `*.pdf` 를 찾는다. 여러 개면 사용자에게 묻고, 0개면 — 단 `작업파일/fulltext.txt` 가 이미 있으면 그걸 텍스트 소스로 쓴다.
- `한국어_요약/` 폴더가 이미 있는지 확인한다(번역본·요약본 존재 여부 파악용). 없으면 `mkdir -p 한국어_요약`.

### 1. 논문 텍스트 확보
다음 우선순위로 본문 텍스트를 얻는다:
1. `작업파일/fulltext.txt` 가 있으면 그대로 읽어 쓴다(이미 paper-summary 가 추출해 둔 것).
2. 없으면 추출 스크립트로 만든다. 스크립트 경로는 **스킬 호출 시 표시되는 "Base directory for this skill" 기준** `scripts/extract_pdf.py` 이다(`~/.claude/skills/...` 로 추측하지 말 것). PyMuPDF 확인 후 실행:
   ```bash
   python3 -c "import fitz" 2>/dev/null \
     || pip3 install --quiet pymupdf \
     || pip3 install --quiet --user pymupdf
   mkdir -p 작업파일
   python3 "<base-dir>/scripts/extract_pdf.py" \
     "<PDF경로>" "작업파일" "한국어_요약/images"
   ```
   - `작업파일/fulltext.txt` 와 `manifest.json` 이 생성된다. (이미지는 사전엔 보통 불필요하니 무시해도 된다.)
- 더 정확히 하려면 **Read 툴로 PDF 를 직접 읽어** 용어의 정확한 의미·맥락을 확인한다.

### 2. `용어사전.html` 작성
템플릿 `assets/template_glossary.html` 을 채운다. `<style>` 안의 `{{CSS}}` 자리에는 `assets/style.css` 전체 내용을 그대로 붙여넣는다.

규칙:
- 논문에 나온 전문 용어·약어를 **빠짐없이** 모은다. 보통 15~40개.
- **중요도 순** 또는 가나다/알파벳 순으로 일관되게 정렬한다.
- 각 항목은 `<div class="term" data-terms="...">` 로 감싸고 안에 `<dt>`/`<dd>` 를 둔다:
  ```html
  <div class="term" data-terms="attention 어텐션 self-attention 셀프어텐션">
    <dt>셀프 어텐션 <span class="en">Self-Attention</span></dt>
    <dd>한 시퀀스 내 서로 다른 위치들을 연관 지어 표현을 계산하는 어텐션 메커니즘. …</dd>
  </div>
  ```
- 약어는 `<dt>` 안에 `<span class="abbr">약어</span>` 배지로 표시.
  예: `<dt>장단기 메모리 <span class="en">Long Short-Term Memory</span> <span class="abbr">LSTM</span></dt>`
- 영어 원어는 `<span class="en">…</span>` 로 감싼다.
- **`data-terms` 속성에 검색 키워드(한글·영어·약어)를 모두 공백으로 나열**한다. 검색 필터가 이 값을 사용한다. 비우면 항목 텍스트로 대체된다.
- 정의는 1~3문장, 이 논문의 맥락에 맞게. 수식 기호는 MathJax 인라인(`\( ... \)`)으로.
- `{{GLOSSARY}}` 에 `.term` 블록들을 채우고, `{{TITLE_KO}}`·`{{TITLE_ORIGINAL}}`·`{{AUTHORS}}`·`{{VENUE_YEAR}}` 도 채운다.
- 검색창·카운터·필터 JS 는 템플릿에 내장돼 있으니 그대로 둔다.

### 3. 번역본·요약본 네비게이션에 용어사전 탭 끼워 넣기
`한국어_요약/번역본.html`, `한국어_요약/요약본.html` 이 **존재하면**, 각 파일의 `.nav-links` 안에 아직 용어사전 링크가 없을 때만 다음 줄을 요약본 링크 바로 뒤에 추가한다(Edit 툴 사용):
```html
    <a href="용어사전.html">📖 용어 사전</a>
```
- 이미 `용어사전.html` 링크가 있으면 건드리지 않는다(중복 방지).
- **둘 다 없으면**(단독 실행), `용어사전.html` 의 네비게이션에서 번역본·요약본 링크는 깨진 링크가 되므로 제거하고 용어사전 탭만 남긴다.

### 4. 마무리 보고
- 생성한 파일 경로(`한국어_요약/용어사전.html`)와 정리한 용어 수를 알린다.
- 번역본·요약본 네비게이션을 갱신했는지 보고한다.
- 여는 법: `open 한국어_요약/용어사전.html` (macOS).

---

## 품질 기준
- **완전성**: 본문의 주요 약어·전문용어를 빠뜨리지 않는다.
- **검색성**: 각 `.term` 의 `data-terms` 에 한/영/약어 키워드를 충분히 넣는다.
- **충실성**: 정의는 이 논문의 맥락에 맞게, 수식·기호를 임의로 바꾸지 않는다.
- **네비게이션 일관성**: 번역본·요약본이 있으면 세 HTML 이 서로 클릭 이동돼야 한다. 용어사전의 active 탭은 자기 자신(`class="active"`)이어야 한다.

## 주의
- 폴더/파일 이름(`한국어_요약`, `작업파일`, `용어사전.html`)은 한글 그대로 사용한다.
- `용어사전.html` 이 이미 있으면 덮어쓰기 전에 사용자에게 확인한다.
