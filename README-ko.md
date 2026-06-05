# hplan_codex

> **WHETHER before HOW** — 만들어야 하는가를 먼저 묻고, 어떻게 만들지를 묻습니다.

Codex CLI용 PM Build Gate. AI 에이전트 코딩에 구조화된 의사결정 프레임워크.

[![skills](https://img.shields.io/badge/skills-28-blue)](skills/)
[![plugins](https://img.shields.io/badge/plugins-5-green)](skills/)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## 문제

AI 코딩 에이전트는 빠릅니다. 너무 빠릅니다.
무엇을 시키든 만들어냅니다 — 잘못된 제품을, 빠른 속도로.

hplan_codex는 HOW 앞에 **WHETHER 게이트**를 추가합니다:
- 이게 해결해야 할 맞는 문제인가?
- 실제 고통의 증거가 있는가?
- 이 규모에서 운영 비용이 감당 가능한가?

---

## 사전 준비: Codex CLI 설치

hplan_codex는 OpenAI Codex CLI 안에서 동작합니다. **먼저 Codex CLI를 설치하세요:**

```bash
npm install -g @openai/codex
```

공식 문서 및 다른 설치 방법: https://developers.openai.com/codex

---

## hplan_codex 설치

**권장 — Codex 세션 안에서 스킬 설치:**

```
$skill-installer https://github.com/kimsanguine/hplan_codex
```

28개 스킬을 Codex CLI 스킬 디렉토리로 가져옵니다. 현재 작업 중인 프로젝트에
`harness/` 파일이나 보조 스크립트를 복사하지는 않습니다.

**프로젝트 설정 — harness 파일과 스크립트 복사:**

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh)
```

`scripts/setup.sh`는 `harness/` 템플릿, `AGENTS.md`, `config.toml.example`,
`scripts/track-probe.sh` 같은 보조 스크립트를 프로젝트로 복사합니다.
Codex 스킬 설치는 하지 않으므로 `$skill-installer`와 함께 사용합니다.

`main`에 push하기 전 로컬 변경으로 설치를 검증하려면:

```bash
HPLAN_CODEX_SOURCE_DIR=/path/to/hplan_codex bash scripts/setup.sh --dir=/path/to/test-project
```

**수동 대안** (clone + 스킬 + harness 설정):

```bash
git clone https://github.com/kimsanguine/hplan_codex.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R hplan_codex/skills/* "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -r hplan_codex/harness/ ./harness/
cp -r hplan_codex/scripts/ ./scripts/
cp hplan_codex/AGENTS.md ./AGENTS.md
# 선택: config 예시를 전역 Codex 설정으로 복사
cp hplan_codex/config.toml.example ~/.codex/config.toml   # 이후 값 편집
```

---

## 빠른 시작

설치 후, 프로젝트 폴더에서:

```
$brainstorm "아이디어"
```

→ 5분 안에 "만들어야 하는가" 판단이 나옵니다.

**전체 워크플로우:**

```
$brainstorm → $socratic-question → $opp-tree → $prd → $conductor
```

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

## 보안 & 샌드박스

hplan_codex는 Codex CLI 샌드박스 안에서 실행됩니다. Codex 0.130.0은 세 가지 샌드박스 모드를 지원합니다:

| 모드 | 권한 |
|---|---|
| `read-only` | 프로젝트 파일 읽기 전용 — 쓰기·네트워크 불가 |
| `workspace-write` | 프로젝트 파일 읽기 + 쓰기 + 워크스페이스 내 명령 실행 (기본값) |
| `danger-full-access` | 전체 읽기/쓰기 + 네트워크 — 태스크를 신뢰할 때만 사용 |

샌드박스 모드는 Codex CLI 세션 또는 설정에서 지정합니다. hplan_codex의 빌드 단계 스킬은 `workspace-write`를 전제로 합니다.

> Codex CLI 0.130.0은 file-based hook을 지원하지 않습니다. `scripts/track-probe.sh`는 `bash scripts/track-probe.sh`로 직접 실행하거나 Codex automation에 연결할 수 있는 수동 스프린트 추적 프로브로 제공됩니다.

## 현재 상태 & 검증

현재 실행 가능:
- `$skill-installer`를 통한 스킬 설치
- `bash scripts/setup.sh`를 통한 harness/script bootstrap
- `bash scripts/track-probe.sh` 수동 probe 실행
- `python3 scripts/validate_agents.py` 정적 스킬/문서 검증

예정 또는 adapter 의존:
- `$agent-gtm`, `$build-or-buy`, `$instruction`, `$respect`, `$ui-validate`, `$weekly-rollup`
- Codex CLI file-based hook 자동 등록

검증 명령:

```bash
python3 scripts/validate_agents.py
bash scripts/setup.sh --help
HPLAN_CODEX_SOURCE_DIR="$PWD" bash scripts/setup.sh --dir="$(mktemp -d)"
printf '%s\n' '{"tool_name":"write_file","tool_input":{"file_path":"noop","content":"a\nb\n"}}' | bash scripts/track-probe.sh
```

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
