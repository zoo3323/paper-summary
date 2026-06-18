# paper-summary

PDF 논문을 한국어로 변환해 주는 Claude Code 플러그인입니다. 현재 폴더의 PDF를 읽어 두 개의 HTML을 만듭니다.

- **번역본.html** — 논문 전체를 한국어로 번역 (그림·표·수식·그래프 포함)
- **요약본.html** — 문제·방법론·결과·결론을 카드 형태로 정리한 핵심 요약

두 문서는 상단 네비게이션으로 서로 클릭 이동할 수 있습니다.

## 설치

```text
/plugin marketplace add zoo3323/paper-summary
/plugin install paper-summary@zoo3323
```

## 사용

논문 PDF가 있는 폴더에서:

```text
/paper-summary
```

또는 "논문 번역/요약 html 만들어줘" 라고 요청하면 됩니다.
