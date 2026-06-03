---
name: customer-reach
description: "인터뷰 대상자 확보 + 컨택 초안 생성 + 인터뷰 질문 설계. plan(확보 전략), linkedin(LinkedIn cold DM 초안), community(커뮤니티 포스팅 초안), survey(설문 초안), interview-questions(인터뷰 질문 세트 설계) 모드를 지원한다. pain 증거를 채우기 위한 선행 단계. Use when a PM needs to find and contact interview candidates before evidence-gate."
metadata:
  short-description: "인터뷰 대상자 확보·컨택 초안·인터뷰 질문 설계 도구"
  plugin: discover
---

## Core Goal

"고객 발화 3건"을 pain 증거로 채우기 위한 인터뷰 대상자 확보 도구.
발견(plan/search) → 초안 생성(linkedin/community/survey) → 기록(pain) 순서로 사용.

## Trigger Gate

### Use This Skill When
- "인터뷰할 사람 어떻게 찾아요?" → plan
- "LinkedIn에서 DM 보내고 싶어요" → linkedin
- "커뮤니티에 포스팅하려고요" → community
- "설문지 만들어줘요" → survey
- 실제 인터뷰 증거를 얻기 전에 이 스킬부터 시작하세요
- "인터뷰 약속을 잡았는데 뭘 물어봐야 할지 모르겠어" → interview-questions 모드

### Route to Other Skills When
- 인터뷰 결과를 기록할 때 → pain 기록 문서에 직접 작성
- 소크라테스 가정 심문 (인터뷰 전) → `socratic-question`

## Instructions

`$customer-reach`를 모드(plan/linkedin/community/survey/interview-questions)와 타겟 ICP 설명과 함께 호출한다.

### mode: plan
1. 입력받은 ICP 설명을 읽어 타겟 확보 전략을 설계한다 (LLM)
2. 3가지 채널 추천: LinkedIn / 커뮤니티(오픈채팅, Reddit, Discord) / 지인 네트워크
3. 각 채널별 예상 성공률과 소요 시간 추정 (결정론: 고정 기준표 기반)
4. reach-plan 문서에 저장

### mode: linkedin
ICP에 맞는 LinkedIn cold DM 초안 생성:
```
안녕하세요 [이름]님,

저는 [내 소개 1줄]입니다.
[ICP의 특정 역할/상황]에서 [핵심 고충]을 어떻게 해결하시는지 15분 여쭤봐도 될까요?

보상 없이도 가능하지만, 원하신다면 [가치 교환 1줄]도 가능합니다.
```
ICP 분야에 따라 문구를 조정한다. 스팸 느낌 패턴 (긴급/할인/과장) 제거.

### mode: community
커뮤니티 포스팅 초안:
- 제목: "[ICP 역할] 분들께 15분 인터뷰 요청드립니다"
- 내용: 무엇을 만드는지 1줄, 누구에게 물어보고 싶은지, 왜 당신의 의견이 중요한지
- 플랫폼별 톤 조정: Reddit(영문/격식X) vs 카카오오픈채팅(한국어/친근함)

### mode: survey
인터뷰 대체용 5문 이하 설문 초안:
- Q1: 현재 [문제 영역]을 어떻게 해결하시나요? (객관식 4개)
- Q2: 가장 번거로운 점은? (서술 or 객관식)
- Q3: 기존 해결책에 얼마나 만족하시나요? (1-5)
- Q4: 새로운 도구가 생긴다면 가장 원하는 기능 1가지는?
- Q5: 인터뷰 참여 의향 (예/아니오 + 연락처 선택)

### mode: interview-questions

> 인터뷰 약속을 잡은 후, 어떤 질문을 할지 설계합니다.
> socratic-question이 내 가정을 심문한다면, interview-questions는 고객에게 던질 질문을 설계합니다.

**입력**: ICP 설명 + 검증하고 싶은 핵심 가정 (없으면 가정 브레인스토밍 결과에서 로드)

1. JTBD(Jobs to Be Done) 프레임으로 핵심 질문 3~5개 생성 (LLM):
   - "마지막으로 이 문제를 겪은 게 언제인가요?" (사실 확인형)
   - "그때 어떻게 해결하셨나요?" (현재 우회책 확인)
   - "이 과정에서 가장 번거로운 부분은 뭔가요?" (pain 깊이 측정)

2. 각 질문에 대해 인터뷰 지침 추가:
   - 좋은 답변 신호 (pain 실재 확인)
   - 나쁜 답변 신호 (pain 없거나 의례적 답변)
   - 후속 질문 힌트

3. 인터뷰 가이드 문서에 저장:
   ```markdown
   # 인터뷰 가이드 — [ICP 설명]

   ## 핵심 가정
   - [검증할 가정 목록]

   ## 질문 세트
   ### Q1. [질문]
   - 좋은 답변 신호: ...
   - 나쁜 답변 신호: ...
   - 후속: ...
   ```

4. 인터뷰 후: 답변을 pain 기록 형식으로 정리하는 방법 안내:
   ```
   - Source: [역할/직군, 회사 규모]
   - Date: YYYY-MM-DD
   - Quote: "[실제 발언]"
   ```
   3건 이상 채우면 → 증거 품질 점검 단계로 이동

> 질문은 Yes/No를 유도하지 않습니다. 열린 질문으로 시작하되, 구체적 사례로 좁힙니다.

## Failure Handling

| 실패 상황 | 대응 |
|---|---|
| ICP 설명 없음 | fail loud — "타겟 ICP를 한 줄로 설명하세요" |
| LinkedIn DM 초안이 세일즈처럼 보임 | 압박/할인/긴급 문구 제거 후 재생성 |
| 커뮤니티 포스팅 플랫폼 미지정 | "어느 커뮤니티인지 알려주세요 (카카오오픈채팅/Reddit/Discord)" |
| 설문이 5문 초과 요청 | "5문 이하로 제한합니다 — 우선순위 3개만 선택하세요" |
| 인터뷰 가이드 저장 실패 | fail loud — 저장 디렉토리 존재 여부 확인 안내 |


## Quality Gate
- [ ] DM/포스팅 초안에 과장/압박 문구 없음
- [ ] 설문 5문 이하 (인지 부하 최소화)
- [ ] 확인 게이트: 초안 보여주고 수정 기회 제공 후 저장
- [ ] interview-questions: 질문이 Yes/No 유도형이 아닌 열린 질문인지 확인
