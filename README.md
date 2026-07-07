# paper-summary

PDF 논문을 한국어로 변환해 주는 Claude Code 플러그인입니다. **두 개의 스킬**이 들어 있습니다.

### 📄 `/paper-summary` — 번역본 + 요약본
현재 폴더의 PDF를 읽어 두 개의 HTML을 만듭니다.

- **번역본.html** — 논문 전체를 한국어로 번역 (그림·표·수식·그래프 포함)
- **요약본.html** — 문제·방법론·결과·결론을 카드 형태로 정리한 핵심 요약

### 📖 `/paper-summary-word` — 용어/약어 사전
논문에 등장하는 전문 용어·약어를 한국어 정의와 함께 정리합니다.

- **용어사전.html** — 검색 필터가 내장된 용어/약어 사전
- 번역본·요약본이 이미 있으면, 그 네비게이션에 용어사전 탭을 자동으로 끼워 넣어 서로 클릭 이동되게 합니다. (PDF만 있어도 단독 실행 가능)

생성된 문서들은 상단 네비게이션으로 서로 클릭 이동할 수 있습니다.
모든 HTML은 **다크 모드**(시스템 설정 따라감)와 **인쇄/PDF 저장**(네비게이션 자동 숨김)을 지원합니다.

## 요구 사항

- `python3` + [PyMuPDF](https://pymupdf.readthedocs.io/) — 없으면 스킬이 자동으로 `pip3 install pymupdf`를 시도합니다.
- 수식 렌더링은 MathJax CDN을 사용하므로 결과 HTML을 열 때 인터넷 연결이 필요합니다. (오프라인에서는 수식만 렌더링되지 않습니다.)

## 설치

```text
/plugin marketplace add zoo3323/paper-summary
/plugin install paper-summary@zoo3323
```

플러그인 하나를 설치하면 두 스킬을 모두 사용할 수 있습니다.

## 사용

논문 PDF가 있는 폴더에서:

```text
/paper-summary        # 번역본 + 요약본
/paper-summary-word   # 용어/약어 사전 (선택)
```

또는 "논문 번역/요약 html 만들어줘", "논문 용어 사전 만들어줘" 라고 요청하면 됩니다.
