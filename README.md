# paper-summary

PDF 논문을 한국어로 변환해 주는 Claude Code 플러그인입니다. 현재 폴더의 PDF를 읽어 두 개의 HTML을 만듭니다.

- **번역본.html** — 논문 전체를 한국어로 번역 (그림·표·수식·그래프 포함)
- **요약본.html** — 문제·방법론·결과·결론을 카드 형태로 정리한 핵심 요약

두 문서는 상단 네비게이션으로 서로 클릭 이동할 수 있습니다.

## 설치

```text
/plugin marketplace add njkim/paper-summary
/plugin install paper-summary@njkim
```

## 사용

논문 PDF가 있는 폴더에서:

```text
/paper-summary
```

또는 "논문 번역/요약 html 만들어줘" 라고 요청하면 됩니다.

## 구조

```
paper-summary/                       # 이 저장소 = 마켓플레이스
├── .claude-plugin/
│   └── marketplace.json             # 마켓플레이스 정의 (name: njkim)
└── plugins/
    └── paper-summary/               # 플러그인
        ├── .claude-plugin/
        │   └── plugin.json
        └── skills/
            └── paper-summary/       # 실제 스킬
                ├── SKILL.md
                ├── scripts/
                └── assets/
```

## 업데이트 배포

`plugins/paper-summary/.claude-plugin/plugin.json` 의 `version` 을 올린 뒤 commit & push 하면
사용자는 `/plugin update` 로 새 버전을 받을 수 있습니다.
