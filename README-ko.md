# hplan_codex

> **WHETHER before HOW** — 만들어야 하는가를 먼저 묻고, 어떻게 만들지를 묻습니다.

Codex CLI용 PM Build Gate. AI 에이전트 코딩에 구조화된 의사결정 프레임워크.

---

## 문제

AI 코딩 에이전트는 빠릅니다. 너무 빠릅니다.
무엇을 시키든 만들어냅니다 — 잘못된 제품을, 빠른 속도로.

hplan_codex는 HOW 앞에 **WHETHER 게이트**를 추가합니다:
- 이게 해결해야 할 맞는 문제인가?
- 실제 고통의 증거가 있는가?
- 이 규모에서 운영 비용이 감당 가능한가?

---

## 빠른 시작

```
$brainstorm [아이디어]
```

→ 5분 안에 "만들어야 하는가" 판단이 나옵니다.

---

## 5개 플러그인 라이프사이클

| 플러그인 | 핵심 질문 | 주요 스킬 |
|---|---|---|
| **hplan** | 만들어야 하는가? | brainstorm, evidence-rubric |
| **discover** | 진짜 문제가 무엇인가? | socratic-question, opp-tree |
| **architect** | 어떻게 설계하는가? | orchestration, memory-arch |
| **deliver** | 어떻게 만들고 출시하는가? | prd, conductor, sprint |
| **operate** | 어떻게 지속하는가? | pm-engine, metrics-design |

---

## 스킬 호출

```
$socratic-question [아이디어]    ← 가정 심문
$opp-tree [도메인]               ← 기회 발굴
$brainstorm [아이디어]           ← WHETHER 3문 체크
$prd [제품]                      ← 15섹션 PRD 작성
$cost-sim [기능]                 ← 비용 시뮬레이션
```

---

## 핵심 원칙

**P1 — 결정론 우선**: LLM은 분류·초안·자연어 생성에만. if문으로 쓰지 않는다.
**P2 — Fail Loud**: 불확실성을 숨기지 않는다. 검증 없는 "완료" 보고 금지.
**P3 — 외과적 변경**: 필요한 것만 건드린다.
**P4 — 목표 주도**: 검증 행위가 인용된 "완료"만 인정한다.
